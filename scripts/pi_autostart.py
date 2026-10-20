"""Install per-user Raspberry Pi desktop autostart; no root access required."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
SERVICE = 'halloween-hub.service'


def quoted(value):
    # Both systemd and Desktop Entry Exec use double quotes, not shell quoting.
    value = str(value)
    for old, new in [('\\', '\\\\'), ('"', '\\"'), ('`', '\\`'), ('$', '\\$')]:
        value = value.replace(old, new)
    return '"' + value.replace('%', '%%') + '"'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['install', 'remove', 'launch'])
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('port must be between 1 and 65535')
    if sys.platform != 'linux':
        parser.error('Raspberry Pi / Linux only')
    config = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
    unit = config / 'systemd/user' / SERVICE
    desktop = config / 'autostart/halloween-hub.desktop'
    python = ROOT / '.venv/bin/python'
    url = f'http://127.0.0.1:{args.port}'
    if args.action == 'launch':
        for _ in range(120):
            try:
                with urlopen(url + '/', timeout=2) as response:
                    if response.status == 200:
                        break
            except (URLError, TimeoutError, OSError):
                pass
            time.sleep(1)
        else:
            sys.exit('Halloween Hub did not become ready; see journalctl --user -u halloween-hub')
        os.execv('/bin/bash', ['bash', str(ROOT / 'kiosk.sh'), url])
    elif args.action == 'remove':
        subprocess.run(['systemctl', '--user', 'disable', '--now', SERVICE], check=True)
        unit.unlink(missing_ok=True)
        desktop.unlink(missing_ok=True)
        subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
        print('Autostart removed. Close the existing kiosk with Alt+F4.')
    else:
        if os.geteuid() == 0:
            parser.error('run as the desktop user, without sudo')
        if not python.is_file():
            parser.error('run ./run.sh once to prepare .venv and dependencies')
        subprocess.run([str(python), str(ROOT / 'scripts/check_dependencies.py')], check=True)
        if not (shutil.which('chromium') or shutil.which('chromium-browser')):
            parser.error('install Chromium first')
        subprocess.run(['systemctl', '--user', 'show-environment'], check=True, stdout=subprocess.DEVNULL)
        unit.parent.mkdir(parents=True, exist_ok=True)
        desktop.parent.mkdir(parents=True, exist_ok=True)
        unit.write_text(
            '[Unit]\nDescription=Halloween Hub kiosk server\n\n[Service]\nType=simple\n'
            f'WorkingDirectory={str(ROOT).replace(chr(37), chr(37) * 2)}\n'
            f'Environment={quoted("HALLOWEEN_DATA_DIR=" + str(ROOT / "data"))}\n'
            f'ExecStart={quoted(python)} -m halloween_hub --no-browser --port {args.port}\n'
            'Restart=on-failure\nRestartSec=5\n\n[Install]\nWantedBy=default.target\n'
        )
        desktop.write_text(
            '[Desktop Entry]\nType=Application\nName=Halloween Hub kiosk\n'
            f'Exec={quoted(python)} {quoted(Path(__file__).resolve())} launch --port {args.port}\n'
            'Terminal=false\nX-GNOME-Autostart-enabled=true\n'
        )
        subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
        subprocess.run(['systemctl', '--user', 'enable', SERVICE], check=True)
        subprocess.run(['systemctl', '--user', 'restart', SERVICE], check=True)
        print(f'Server enabled at {url}; kiosk opens at next desktop login.')
        print('Enable Desktop Autologin in Raspberry Pi Configuration for unattended boot.')


if __name__ == '__main__':
    main()
