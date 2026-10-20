"""Minimize only a browser window titled Halloween Hub; never simulate global keys.

Wayland requests follow wlr-foreign-toplevel-management v1 (version 3).
https://github.com/swaywm/wlr-protocols/blob/master/unstable/wlr-foreign-toplevel-management-unstable-v1.xml
"""
import ctypes
import os
import platform
import shutil
import socket
import stat
import struct
import subprocess
from pathlib import Path


def uint(n):
    return struct.pack('<I', n)


def string(value):
    data = value.encode() + b'\0'
    return uint(len(data)) + data + b'\0' * (-len(data) % 4)


def read_string(data, offset=0):
    size = struct.unpack_from('<I', data, offset)[0]
    return data[offset+4:offset+4+size-1].decode(errors='replace'), offset+4+((size+3)//4)*4


class WaylandWindows:
    def __init__(self):
        runtime = Path(os.environ.get('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}'))
        display = os.environ.get('WAYLAND_DISPLAY', 'wayland-0')
        path = Path(display) if display.startswith('/') else runtime / display
        if not stat.S_ISSOCK(path.stat().st_mode) or path.stat().st_uid != os.getuid():
            raise OSError('No owned Wayland display socket')
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(2)
        self.sock.connect(str(path))
        self.next_id = 2
        self.globals = {}
        self.handles = {}
        self.manager = None
        self.registry = self.allocate()
        self.send(1, 1, uint(self.registry))
        self.roundtrip()
        global_info = self.globals.get('zwlr_foreign_toplevel_manager_v1')
        if not global_info:
            self.close()
            raise OSError('This compositor does not support native window management')
        self.manager = self.bind('zwlr_foreign_toplevel_manager_v1', min(3, global_info[1]))
        self.roundtrip()

    def __del__(self):
        if hasattr(self, 'sock'):
            self.sock.close()

    def allocate(self):
        identifier = self.next_id
        self.next_id += 1
        return identifier

    def send(self, identifier, opcode, payload=b''):
        self.sock.sendall(struct.pack('<II', identifier, (len(payload)+8)<<16 | opcode) + payload)

    def bind(self, name, version):
        identifier = self.allocate()
        self.send(self.registry, 0, uint(self.globals[name][0])+string(name)+uint(version)+uint(identifier))
        return identifier

    def read_exact(self, size):
        data = b''
        while len(data) < size:
            chunk = self.sock.recv(size-len(data))
            if not chunk:
                raise OSError('Wayland connection closed')
            data += chunk
        return data

    def roundtrip(self):
        callback = self.allocate()
        self.send(1, 0, uint(callback))
        while True:
            identifier, header = struct.unpack('<II', self.read_exact(8))
            size, opcode = header >> 16, header & 65535
            if size < 8 or size > 65535:
                raise OSError('Invalid Wayland event')
            data = self.read_exact(size-8)
            if identifier == callback and opcode == 0:
                return
            if identifier == 1 and opcode == 0:
                raise OSError('The compositor rejected window management')
            if identifier == self.registry and opcode == 0:
                name = struct.unpack_from('<I', data)[0]
                interface, offset = read_string(data, 4)
                self.globals[interface] = (name, struct.unpack_from('<I', data, offset)[0])
            elif identifier == self.manager and opcode == 0:
                self.handles[struct.unpack_from('<I', data)[0]] = dict(title='', app_id='', states=[])
            elif identifier in self.handles:
                handle = self.handles[identifier]
                if opcode == 0:
                    handle['title'] = read_string(data)[0]
                elif opcode == 1:
                    handle['app_id'] = read_string(data)[0]
                elif opcode == 4:
                    length = struct.unpack_from('<I', data)[0]
                    handle['states'] = list(struct.unpack_from('<'+'I'*(length//4), data, 4))
                elif opcode == 6:
                    del self.handles[identifier]

    def target(self):
        matches = [(identifier, handle) for identifier, handle in self.handles.items()
                   if handle['title'].startswith('Halloween Hub') and
                   any(name in handle['app_id'].lower() for name in ('chrom', 'firefox', 'edge'))]
        matches.sort(key=lambda item: 2 not in item[1]['states'])
        if not matches:
            raise OSError('No Halloween Hub browser window was found')
        return matches[0]

    def action(self, action):
        identifier, handle = self.target()
        if action == 'minimize':
            self.send(identifier, 2)
        elif action == 'restore':
            self.send(identifier, 3)
            if 'wl_seat' in self.globals:
                seat = self.bind('wl_seat', 1)
                self.send(identifier, 4, uint(seat))
        else:
            raise ValueError('Unknown window action')
        self.roundtrip()
        return self.handles.get(identifier, handle)

    def close(self):
        self.sock.close()


def windows_target(action=None):
    from ctypes import wintypes
    user = ctypes.WinDLL('user32', use_last_error=True)
    user.GetForegroundWindow.restype = wintypes.HWND
    user.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    handles = []
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    @callback_type
    def visit(handle, _):
        title = ctypes.create_unicode_buffer(512)
        user.GetWindowTextW(handle, title, len(title))
        if title.value.startswith('Halloween Hub') and any(name in title.value for name in ('Chrome','Chromium','Firefox','Edge')):
            handles.append(handle)
        return True
    user.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
    user.EnumWindows(visit, 0)
    if not handles:
        raise OSError('No Halloween Hub browser window was found')
    foreground = user.GetForegroundWindow()
    handle = foreground if foreground in handles else handles[0]
    if action:
        user.ShowWindow(handle, 6 if action == 'minimize' else 9)
    return dict(available=True, backend='Windows')


def manage(action=None):
    if platform.system() == 'Windows':
        try:
            return windows_target(action)
        except OSError as error:
            if action:
                raise
            return dict(available=False, reason=str(error))
    wayland = None
    try:
        wayland = WaylandWindows()
        _, handle = wayland.target()
        if action:
            handle = wayland.action(action)
        return dict(available=True, backend='Wayland', window=handle)
    except (OSError, ValueError) as error:
        if not os.environ.get('DISPLAY') or not shutil.which('xdotool'):
            if action:
                raise OSError(str(error)) from error
            return dict(available=False, reason=str(error))
    finally:
        if wayland:
            wayland.close()
    found = subprocess.run(['xdotool', 'search', '--name', '^Halloween Hub'], capture_output=True, text=True, timeout=2)
    windows = found.stdout.splitlines()
    if not windows:
        if action:
            raise OSError('No Halloween Hub browser window was found')
        return dict(available=False, reason='No Halloween Hub browser window was found')
    if action:
        operation = 'windowminimize' if action == 'minimize' else 'windowactivate'
        subprocess.run(['xdotool', operation, windows[-1]], check=True, timeout=2)
    return dict(available=True, backend='X11')
