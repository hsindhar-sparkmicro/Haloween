import json
import os
import random
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

DEFAULTS = dict(timezone='America/Toronto', units='C', location=None, volume=40,
                rotation=False, music_shuffle=True, reduced_motion=False, jumpscares=False, flicker=False, auto_download_updates=True,
                quality='auto', party_date='', sensitivity='medium',
                camera_area='center', camera_threshold=4, camera_cooldown=45,
                camera_scan_seconds=180, visitor_mode='choose')


def data_directory():
    if os.environ.get('HALLOWEEN_DATA_DIR'):
        return Path(os.environ['HALLOWEEN_DATA_DIR'])
    root = Path(os.environ.get('LOCALAPPDATA', Path.home() / '.local' / 'share'))
    return root / 'HalloweenHub'


def countdown(settings, now=None):
    zone = ZoneInfo(settings['timezone'])
    now = now or datetime.now(zone)
    now = now.astimezone(zone)
    custom = settings.get('party_date')
    if custom:
        target = datetime.fromisoformat(custom)
        if target.tzinfo is None:
            target = target.replace(tzinfo=zone)
    else:
        target = datetime(now.year, 10, 31, tzinfo=zone)
        if now.date() > target.date():
            target = target.replace(year=now.year + 1)
    seconds = max(0, int(target.timestamp() - now.timestamp()))
    return dict(seconds=seconds, target=target.isoformat(), now=now.isoformat())


class Store:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / 'music').mkdir(exist_ok=True)
        (self.root / 'effects').mkdir(exist_ok=True)
        self.path = self.root / 'hub.sqlite3'
        with self.connect() as db:
            db.executescript('''CREATE TABLE IF NOT EXISTS state(key TEXT PRIMARY KEY, value TEXT);
            CREATE TABLE IF NOT EXISTS records(id INTEGER PRIMARY KEY, kind TEXT, name TEXT, done INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS tracks(id INTEGER PRIMARY KEY, name TEXT, filename TEXT);
            CREATE TABLE IF NOT EXISTS effects(id INTEGER PRIMARY KEY, name TEXT, filename TEXT);
            CREATE TABLE IF NOT EXISTS detections(id INTEGER PRIMARY KEY, time TEXT, room TEXT, event TEXT, emf REAL);''')
            db.execute('INSERT OR IGNORE INTO state VALUES(?,?)', ('settings', json.dumps(DEFAULTS)))
            db.execute('INSERT OR IGNORE INTO state VALUES(?,?)', ('candy', '0'))

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path, timeout=10)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def get(self, key, default=None):
        with self.connect() as db:
            row = db.execute('SELECT value FROM state WHERE key=?', (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def put(self, key, value):
        with self.connect() as db:
            db.execute('INSERT OR REPLACE INTO state VALUES(?,?)', (key, json.dumps(value)))

    def candy(self, delta):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            current = json.loads(db.execute("SELECT value FROM state WHERE key='candy'").fetchone()[0])
            value = max(0, current + delta)
            db.execute("UPDATE state SET value=? WHERE key='candy'", (json.dumps(value),))
        return value

    def rows(self, table):
        if table not in ('records', 'tracks', 'effects', 'detections'):
            raise ValueError('Unknown table')
        with self.connect() as db:
            db.row_factory = sqlite3.Row
            return [dict(row) for row in db.execute(f'SELECT * FROM {table} ORDER BY id DESC')]


SCENES = {
    'Quiet shadows': dict(preset=(60,80,0,40), audio='quiet-scene.wav',
        phases=['Candlelight', 'Wind at the window', 'A distant whisper', 'Embers fade'],
        room=[.3,.6,.45,.2], porch=[.25,.45,.8,.25], fog=[10,15,25,5]),
    'Purple mist': dict(preset=(25,40,60,35), audio='mist-scene.wav',
        phases=['Violet veil', 'Mist rolls in', 'Ghosts in the fog', 'Mist clears'],
        room=[.2,.4,.3,.2], porch=[.3,.5,.8,.25], fog=[40,80,100,20]),
    'Pumpkin parade': dict(preset=(90,100,15,65), audio='pumpkin-scene.wav',
        phases=['Lanterns awaken', 'Pumpkin procession', 'Candy celebration', 'Lanterns dim'],
        room=[.5,.8,1,.7], porch=[.6,.9,1,.4], fog=[5,15,25,5])
}

for name, audio, phases, preset in [
    ('Transylvania vampire','vampire',['Castle awakens','Coffin opens','Vampire approaches','Into the bats'],(30,35,50,45)),
    ('Ghostbuster encounter','buster',['Ectoplasm detected','Ghost appears','Energy capture','Containment'],(55,70,35,55)),
    ("Witch’s swamp",'witch',['Swamp whispers','Cauldron bubbles','Witch takes flight','Fireflies settle'],(25,30,65,40)),
    ('Graveyard awakening','graveyard',['Gates open','Ground stirs','Hands emerge','Restless spirits'],(35,45,45,40)),
    ('Phantom train','train',['Empty platform','Headlights approach','Spectral passengers','Train disappears'],(45,55,55,50))]:
    SCENES[name] = dict(preset=preset, audio=audio+'-scene.wav', phases=phases,
                        room=[.25,.5,.8,.3], porch=[.3,.6,1,.3], fog=[20,45,70,15])


class Simulation:
    """Shared simulation boundary. No GPIO or sensor access."""
    def __init__(self, store):
        self.store = store
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.haunt = dict(active=False, stage='Quiet shadows', room=60, porch=80, fog=0,
                          sound=40, motion=False, scene='Quiet shadows', audio='quiet-scene.wav', progress=0,
                          run_id=0, seed=0, source='manual')
        self.welcome = dict(active=False, id=0)
        self.welcome_deadline = 0
        self.camera_scan_owned = False
        self.scan = dict(active=False, emf=0.0, temperature=18.6, rooms=[0, 0, 0, 0], peak=0.0)
        self.saved_lights = dict(room=60, porch=80)
        self.started = 0
        self.next_log = 0
        self.thread = threading.Thread(target=self.run, daemon=True, name='simulation')
        self.thread.start()

    def command(self, body):
        with self.lock:
            action = body.get('action')
            if action in ('activate', 'play', 'random'):
                source = body.get('_source', 'manual')
                if source not in ('camera','test','encounter'):
                    self.cancel_welcome()
                scene_name = self.haunt['scene']
                if action == 'random':
                    scene_name = random.choice([name for name in SCENES if name != scene_name])
                elif action == 'play':
                    scene_name = body.get('scene')
                    if scene_name not in SCENES:
                        raise ValueError('Choose a known haunt scene')
                if action in ('play', 'random'):
                    self.haunt.update(zip(('room','porch','fog','sound'), SCENES[scene_name]['preset']))
                elif self.haunt['active']:
                    self.haunt.update(self.saved_lights)
                self.haunt['scene'] = scene_name
                self.saved_lights = {key: self.haunt[key] for key in ('room', 'porch')}
                self.started = time.monotonic()
                seed = random.getrandbits(32)
                self.haunt.update(active=True, progress=0, audio=SCENES[scene_name]['audio'],
                                  seed=seed, run_id=seed, source=source)
                self.step_scene(0)
            elif action == 'motion':
                self.haunt['motion'] = not self.haunt['motion']
            elif action == 'stop':
                self.cancel_welcome()
                restore = self.saved_lights if self.haunt['active'] else {}
                self.haunt.update(active=False, stage='Stopped', fog=0, motion=False, progress=0, **restore)
            elif action == 'set':
                key = body.get('key')
                if self.haunt['active'] and key != 'sound':
                    raise ValueError('Stop the sequence before changing this control')
                if key in ('room', 'porch', 'fog', 'sound'):
                    value = body.get('value')
                    if not isinstance(value, (int, float)) or not 0 <= value <= 100:
                        raise ValueError('Slider value must be 0–100')
                    self.haunt[key] = value
                elif key == 'scene' and body.get('value') in SCENES:
                    self.haunt['scene'] = body['value']
                    self.haunt.update(zip(('room', 'porch', 'fog', 'sound'), SCENES[body['value']]['preset']))
                    self.haunt.update(stage=body['value'], audio=SCENES[body['value']]['audio'])
                else:
                    raise ValueError('Unknown haunt control')
            else:
                raise ValueError('Unknown haunt command')
            return dict(self.haunt)

    def snapshot(self):
        with self.lock:
            return dict(haunt=dict(self.haunt), scan=dict(self.scan), welcome=dict(self.welcome))

    def welcome_motion(self, source='camera'):
        with self.lock:
            if self.haunt['active'] or self.welcome['active']:
                return False
            self.welcome = dict(active=True, id=random.getrandbits(32), source=source)
            self.welcome_deadline = time.monotonic() + 120
            return True

    def encounter(self, action, identifier=None):
        with self.lock:
            if action == 'start':
                if not self.welcome_motion(source='touch'):
                    raise ValueError('Finish the current activity before starting another')
            elif action in ('finish','heartbeat'):
                if self.welcome['id'] == identifier:
                    if action == 'finish':self.cancel_welcome()
                    else:self.welcome_deadline=time.monotonic()+120
            else:raise ValueError('Choose start, finish or heartbeat')
            return dict(self.welcome)

    def cancel_welcome(self):
        self.welcome['active'] = False
        if self.camera_scan_owned:
            self.scan['active'] = False
        self.camera_scan_owned = False

    def step_scene(self, elapsed):
        scene = SCENES[self.haunt['scene']]
        phase = min(3, int(elapsed / 5))
        self.haunt.update(stage=self.haunt['scene']+' · '+scene['phases'][phase],
                          fog=scene['fog'][phase], motion=phase == 2,
                          progress=min(100,round(elapsed*5)),
                          **{key:round(value*scene[key][phase]) for key,value in self.saved_lights.items()})

    def run(self):
        while not self.stop_event.wait(1):
            with self.lock:
                if self.welcome['active'] and time.monotonic() >= self.welcome_deadline:
                    self.cancel_welcome()
                if self.haunt['active']:
                    elapsed = time.monotonic() - self.started
                    if elapsed >= 20:
                        self.haunt.update(active=False, stage=self.haunt['scene']+' · Complete', fog=0, motion=False, progress=100, **self.saved_lights)
                        self.cancel_welcome()
                    else:
                        self.step_scene(elapsed)
                if self.scan['active']:
                    sensitivity = self.store.get('settings')['sensitivity']
                    factor = {'low': .55, 'medium': .8, 'high': 1}[sensitivity]
                    emf = round(random.uniform(.1, 5) * factor, 1)
                    self.scan.update(emf=emf, temperature=round(random.uniform(17.5, 19.8), 1),
                                     rooms=[round(random.random() * 100) for _ in range(4)],
                                     peak=max(self.scan['peak'], emf))
                    if time.monotonic() >= self.next_log:
                        self.next_log = time.monotonic() + 8
                        stamp = datetime.now(ZoneInfo(self.store.get('settings')['timezone'])).isoformat()
                        with self.store.connect() as db:
                            db.execute('INSERT INTO detections(time,room,event,emf) VALUES(?,?,?,?)',
                                       (stamp, random.choice(['Hallway', 'Attic', 'Parlor', 'Basement']),
                                        'Simulated EMF spike' if emf > 2.5 else 'Simulated faint presence', emf))
                            db.execute('DELETE FROM detections WHERE id NOT IN (SELECT id FROM detections ORDER BY id DESC LIMIT 500)')

    def close(self):
        self.stop_event.set()
        self.thread.join(timeout=2)
