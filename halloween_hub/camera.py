"""Hidden motion scans with physical capture shutdown between scan windows."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
import time


class Camera:
    def __init__(self,store,simulation):
        self.store,self.simulation=store,simulation
        self.lock=threading.RLock()
        self.command_lock=threading.Lock()
        self.process=None
        self.thread=None
        self.stop_event=threading.Event()
        self.armed=self.ready=False
        self.error=''
        self.score=0
        self.triggers=self.scans=0
        self.quiet=self.moving=0
        self.quiet_ready=False
        self.warming=True
        self.detected=False
        self.completed=False
        self.next_scan=self.scan_until=self.last_trigger=0
        self.temperature=None
        self.temperature_source='unavailable'
        self.temperature_at=0
        self.heat_pause=False
        self.available=sys.platform.startswith('linux') and bool(shutil.which('rpicam-hello'))

    def settings(self):
        from .core import DEFAULTS
        return dict(DEFAULTS,**self.store.get('settings'))

    def snapshot(self):
        now=time.monotonic()
        with self.lock:
            cooldown=max(0,int(self.next_scan-now+.99)) if self.armed else 0
            status=('Error' if self.error else 'Off' if not self.armed else 'Cooling: board temperature high' if self.heat_pause
                    else 'Warming up' if self.process and (not self.ready or self.warming)
                    else 'Scanning' if self.process else 'Resting' if cooldown else 'Waiting for visitor activity to finish')
            return dict(available=self.available,enabled=self.armed,armed=self.armed,capture_active=self.process is not None,
                        status=status,error=self.error,motion_percent=self.score,cooldown=cooldown,triggers=self.triggers,
                        scans=self.scans,scan_remaining=max(0,int(self.scan_until-now+.99)) if self.process else 0,
                        temperature=self.temperature,temperature_source=self.temperature_source,
                        mode='Hidden local motion detection; no images or video exported')

    def command(self,action):
        with self.command_lock:return self._command(action)

    def _command(self,action):
        if action=='test':
            if not self.simulation.welcome_motion(source='test'):
                raise ValueError('Finish the current activity before testing a welcome')
            return self.snapshot()
        if action in ('stop','disarm'):
            self.close()
            with self.simulation.lock:
                if self.simulation.welcome.get('source')=='camera':self.simulation.cancel_welcome()
            return self.snapshot()
        if action!='arm':raise ValueError('Choose arm, disarm, stop or test; camera previews are disabled')
        if not self.available:raise ValueError('Pi motion camera is unavailable on this host. Pumpkin touch still works.')
        if not self.armed:self.close()
        with self.lock:
            if not self.armed:
                self.armed=True;self.error='';self.stop_event.clear();self.next_scan=0
                self.thread=threading.Thread(target=self.run,daemon=True,name='camera-duty-cycle');self.thread.start()
        return self.snapshot()

    def sample_temperature(self,now):
        if now-self.temperature_at<5:return
        value=None;source='unavailable'
        try:
            if shutil.which('vcgencmd'):
                result=subprocess.run(['vcgencmd','measure_temp'],capture_output=True,text=True,timeout=1)
                match=re.search(r'temp=([\d.]+)',result.stdout)
                if match:value=float(match[1]);source='Pi SoC (vcgencmd)'
            elif Path('/sys/class/thermal/thermal_zone0/temp').exists():
                value=int(Path('/sys/class/thermal/thermal_zone0/temp').read_text())/1000;source='SoC thermal zone'
        except (OSError,ValueError,subprocess.TimeoutExpired):pass
        with self.lock:
            self.temperature=value;self.temperature_source=source;self.temperature_at=now
            if value is not None:
                if value>=70:self.heat_pause=True
                elif value<=65:self.heat_pause=False

    def start_scan(self,now):
        with self.lock:
            if not self.armed or self.process:return
            self.ready=False;self.warming=True;self.detected=False;self.completed=False
            self.quiet=self.moving=0;self.quiet_ready=False
            executable=os.environ.get('HALLOWEEN_CAMERA_PYTHON','/usr/bin/python3')
            self.process=subprocess.Popen([executable,'-u',str(Path(__file__).with_name('camera_worker.py')),str(self.settings()['camera_scan_seconds'])],
                                          stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,bufsize=1)
            self.scan_until=now+self.settings()['camera_scan_seconds'];self.scans+=1
            threading.Thread(target=self.read,args=(self.process,),daemon=True,name='camera-scores').start()

    def end_scan(self,rest=True):
        with self.lock:
            process,self.process=self.process,None
            self.ready=False;self.scan_until=0
        if process:
            process.terminate()
            try:process.wait(timeout=2)
            except subprocess.TimeoutExpired:process.kill();process.wait(timeout=2)
        if rest:
            with self.lock:self.next_scan=time.monotonic()+self.settings()['camera_cooldown']

    def run(self):
        try:
            while not self.stop_event.is_set():
                now=time.monotonic();self.sample_temperature(now)
                with self.lock:
                    active=self.process is not None
                    end=active and (now>=self.scan_until or self.detected or self.heat_pause or not self.armed)
                    armed=self.armed
                if end:self.end_scan()
                if not armed:break
                with self.simulation.lock:
                    busy=self.simulation.haunt['active'] or self.simulation.welcome['active']
                with self.lock:
                    start=self.armed and not self.process and not self.heat_pause and now>=self.next_scan and not busy
                if start:self.start_scan(now)
                self.stop_event.wait(.2)
        except (OSError,ValueError) as error:
            with self.lock:self.error=str(error)[:300];self.armed=False
        finally:self.end_scan(rest=False)

    def consume(self,message,now=None):
        now=time.monotonic() if now is None else now
        with self.lock:
            if message.get('error'):self.error=message['error'][:300];self.armed=False;return
            if message.get('ready'):self.ready=True
            if message.get('scan_complete'):self.completed=True;self.detected=True
            if 'scores' not in message:return
            self.warming=message.get('warming',False)
            self.score=message['scores'].get(self.settings()['camera_area'],0)
            if self.warming or not self.armed or self.detected or self.process is None:return
            motion=self.score>=self.settings()['camera_threshold']
            self.quiet=0 if motion else self.quiet+1;self.moving=self.moving+1 if motion else 0
            if self.quiet>=5:self.quiet_ready=True
            if self.moving>=3 and self.quiet_ready:
                if self.simulation.welcome_motion():
                    self.triggers+=1;self.last_trigger=now;self.detected=True
                    self.quiet_ready=False;self.quiet=self.moving=0

    def read(self,process):
        try:
            for line in process.stdout:
                with self.lock:
                    if self.process is not process:return
                    try:self.consume(json.loads(line))
                    except (ValueError,TypeError,KeyError):continue
        finally:
            process.stdout.close()
            with self.lock:
                if self.process is process:
                    if self.completed:self.detected=True
                    else:
                        self.error=self.error or 'Camera scan stopped unexpectedly. Check camera availability and system Picamera2.'
                        self.armed=False

    def close(self):
        with self.lock:
            self.armed=False;self.stop_event.set();thread=self.thread
        if thread and thread is not threading.current_thread():thread.join(timeout=4)
        self.end_scan(rest=False)
        with self.lock:self.error='';self.next_scan=0
