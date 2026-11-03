import atexit
import csv
import io
import json
import math
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from flask import Flask, jsonify, request, send_from_directory, Response
from werkzeug.exceptions import HTTPException
from .core import DEFAULTS, SCENES, Store, Simulation, countdown, data_directory
from .gallery import cutscenes, backgrounds
from .media import import_audio
from .camera import Camera
from .weather import Weather, search_locations
from .window import manage as manage_window
from .sneak_peek import sneak_peek_calendar


def create_app(root=None):
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
    store = Store(root or data_directory())
    sim = Simulation(store)
    camera = Camera(store, sim)
    weather = Weather(store)
    app.extensions.update(store=store, simulation=sim, weather=weather, camera=camera)
    atexit.register(sim.close)
    atexit.register(camera.close)

    @app.before_request
    def same_origin_mutations():
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            origin = request.headers.get('Origin')
            if origin and origin.rstrip('/') != request.host_url.rstrip('/'):
                return jsonify(error='Cross-origin changes are not allowed'), 403

    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; media-src 'self' blob:; connect-src 'self'; frame-ancestors 'none'"
        if request.path.startswith('/api'):
            response.headers['Cache-Control'] = 'no-store'
        return response

    @app.errorhandler(Exception)
    def errors(error):
        if isinstance(error, HTTPException):
            return jsonify(error=error.description), error.code
        if isinstance(error, (ValueError, KeyError, TypeError, ZoneInfoNotFoundError)):
            return jsonify(error=str(error)), 400
        app.logger.exception('Request failed')
        return jsonify(error='The server could not complete this request'), 500

    def body():
        data = request.get_json()
        if not isinstance(data, dict):
            raise ValueError('Expected a JSON object')
        return data

    @app.get('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.get('/api/window')
    def window_capabilities():
        if request.remote_addr not in ('127.0.0.1','::1'):
            return jsonify(available=False, reason='Native controls are local to the server desktop')
        return jsonify(manage_window())

    @app.post('/api/window/minimize')
    def minimize():
        if request.remote_addr not in ('127.0.0.1','::1'):
            return jsonify(error='Native controls are local only'), 403
        try:
            return jsonify(manage_window('minimize'))
        except OSError as error:
            return jsonify(error=str(error)), 409

    @app.get('/api/health')
    def health():
        return jsonify(status='ok', version='1.0.0', hardware='simulated')

    @app.get('/api/state')
    def state():
        settings = dict(DEFAULTS, **store.get('settings'))
        return jsonify(settings=settings, candy=store.get('candy'), countdown=countdown(dict(settings, party_date='')), party_countdown=countdown(settings), sneak_peek=sneak_peek_calendar(settings['timezone']),
                       records=store.rows('records'), tracks=store.rows('tracks'), effects=store.rows('effects'),
                       detections=store.rows('detections')[:20], weather=weather.snapshot(settings['location']),
                       camera=camera.snapshot(), cutscene={'available':(store.root/'cutscenes'/'welcome.mp4').is_file(),'url':'/api/cutscene','webm_url':'/api/cutscene/webm' if (store.root/'cutscenes'/'welcome.webm').is_file() else None,'items':cutscenes(store.root)}, backgrounds=backgrounds(store.root), scenes=list(SCENES), **sim.snapshot())

    @app.get('/api/cutscene')
    @app.get('/api/cutscene/webm')
    def cutscene():
        webm=request.path.endswith('/webm')
        return send_from_directory(store.root/'cutscenes','welcome.webm' if webm else 'welcome.mp4',mimetype='video/webm' if webm else 'video/mp4',conditional=True)

    @app.get('/api/cutscenes/<filename>')
    def gallery_cutscene(filename):
        if filename not in {p['id']+ext for p in cutscenes(store.root) for ext in ('.mp4','.webm')}:
            return jsonify(error='Cutscene not found'),404
        return send_from_directory(store.root/'cutscenes',filename,conditional=True)

    @app.get('/api/backgrounds/<filename>')
    def gallery_background(filename):
        if filename not in {p['id']+'.png' for p in backgrounds(store.root)}:
            return jsonify(error='Background not found'),404
        return send_from_directory(store.root/'backgrounds',filename,mimetype='image/png')

    @app.post('/api/camera')
    def camera_command():
        return jsonify(camera.command(body().get('action')))

    @app.post('/api/encounter')
    def encounter():
        data=body()
        return jsonify(sim.encounter(data.get('action'),data.get('id')))

    @app.get('/api/camera/frame')
    def camera_frame():
        return jsonify(error='Camera images and video are disabled. Hidden motion-only mode.'),410

    @app.patch('/api/settings')
    def settings():
        changes = body()
        current = dict(DEFAULTS, **store.get('settings'))
        if set(changes) - set(DEFAULTS):
            raise ValueError('Unknown setting')
        for key, value in changes.items():
            if key in ('rotation', 'music_shuffle', 'reduced_motion', 'jumpscares', 'flicker') and not isinstance(value, bool):
                raise ValueError('Expected a boolean')
            if key == 'volume' and (isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100):
                raise ValueError('Volume must be 0–100')
            if key == 'units' and value not in ('C', 'F'):
                raise ValueError('Units must be C or F')
            if key == 'quality' and value not in ('auto', 'low', 'high'):
                raise ValueError('Invalid quality')
            if key == 'sensitivity' and value not in ('low', 'medium', 'high'):
                raise ValueError('Invalid sensitivity')
            if key == 'camera_area' and value not in ('full','center','left','right'):
                raise ValueError('Invalid camera detection area')
            if key == 'visitor_mode' and value not in ('choose','play','story','surprise'):
                raise ValueError('Invalid visitor mode')
            if key == 'camera_scan_seconds' and (isinstance(value,bool) or not isinstance(value,int) or not 6 <= value <= 600):
                raise ValueError('Camera scan window must be 6–600 seconds')
            if key in ('camera_threshold','camera_cooldown'):
                low, high = (1,30) if key == 'camera_threshold' else (20,300)
                if isinstance(value,bool) or not isinstance(value,int) or not low <= value <= high:
                    raise ValueError(f'{key} must be {low}–{high}')
            if key == 'timezone':
                ZoneInfo(value)
            if key == 'party_date':
                if not isinstance(value, str):
                    raise ValueError('Party date must be a local ISO date/time or empty')
                if value:
                    datetime.fromisoformat(value)
            if key == 'location' and value is not None:
                if not isinstance(value, dict) or not isinstance(value.get('name'), str) or not 1 <= len(value['name']) <= 160:
                    raise ValueError('Invalid location')
                for field, limit in [('latitude', 90), ('longitude', 180)]:
                    n = value.get(field)
                    if isinstance(n, bool) or not isinstance(n, (int, float)) or not math.isfinite(n) or abs(n) > limit:
                        raise ValueError('Invalid coordinates')
        current.update(changes)
        countdown(current)
        store.put('settings', current)
        weather.retry_at = 0
        return jsonify(current)

    @app.post('/api/candy')
    def candy():
        delta = body().get('delta')
        if isinstance(delta, bool) or not isinstance(delta, int) or abs(delta) > 10000:
            raise ValueError('Candy adjustment must be an integer between −10000 and 10000')
        return jsonify(candy=store.candy(delta))

    @app.route('/api/records', methods=['POST'])
    def add_record():
        data = body()
        name = data.get('name', '').strip()
        if data.get('kind') not in ('guest', 'task') or not 1 <= len(name) <= 120:
            raise ValueError('Choose guest or task and enter a name (1–120 characters)')
        with store.connect() as db:
            cursor = db.execute('INSERT INTO records(kind,name) VALUES(?,?)', (data['kind'], name))
        return jsonify(id=cursor.lastrowid), 201

    @app.route('/api/records/<int:identifier>', methods=['PATCH', 'DELETE'])
    def edit_record(identifier):
        with store.connect() as db:
            if not db.execute('SELECT id FROM records WHERE id=?', (identifier,)).fetchone():
                return jsonify(error='Record not found'), 404
            if request.method == 'DELETE':
                db.execute('DELETE FROM records WHERE id=?', (identifier,))
            else:
                data = body()
                if 'done' in data:
                    if not isinstance(data['done'], bool):
                        raise ValueError('Done must be a boolean')
                    db.execute('UPDATE records SET done=? WHERE id=?', (int(data['done']), identifier))
                if 'name' in data:
                    name = data['name'].strip()
                    if not 1 <= len(name) <= 120:
                        raise ValueError('Name must be 1–120 characters')
                    db.execute('UPDATE records SET name=? WHERE id=?', (name, identifier))
        return jsonify(ok=True)

    @app.post('/api/haunt')
    def haunt():
        return jsonify(sim.command(body()))

    @app.post('/api/scan')
    def scan():
        active = body().get('active')
        if not isinstance(active, bool):
            raise ValueError('Active must be a boolean')
        with sim.lock:
            sim.scan['active'] = active
            if active:
                sim.next_log = 0
        return jsonify(sim.snapshot()['scan'])

    @app.get('/api/logs')
    def logs():
        return jsonify(detections=store.rows('detections'))

    @app.get('/api/logs/export')
    def export():
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['time', 'room', 'event', 'emf_mG_simulated'])
        for row in store.rows('detections'):
            writer.writerow([row[k] for k in ('time', 'room', 'event', 'emf')])
        return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename="ghost-detections.csv"'})

    @app.get('/api/locations')
    def locations():
        query = request.args.get('q', '').strip()
        if not 2 <= len(query) <= 100:
            raise ValueError('Enter at least two characters')
        try:
            return jsonify(results=search_locations(query))
        except Exception:
            return jsonify(error='Location search is unavailable. Try again when online.'), 503

    @app.post('/api/tracks')
    @app.post('/api/effects')
    def upload():
        kind='effects' if request.path.endswith('/effects') else 'tracks'
        result=import_audio(store,request.files.get('file'),kind)
        return jsonify(result),200 if result['duplicate'] else 201

    @app.route('/api/tracks/<int:identifier>', methods=['GET', 'DELETE'])
    @app.route('/api/effects/<int:identifier>', methods=['GET', 'DELETE'])
    def track(identifier):
        kind='effects' if request.path.startswith('/api/effects/') else 'tracks'
        directory=store.root/('effects' if kind=='effects' else 'music')
        rows = [r for r in store.rows(kind) if r['id'] == identifier]
        if not rows:return jsonify(error='Audio file not found'),404
        row=rows[0]
        if request.method=='GET':return send_from_directory(directory,row['filename'])
        with store.connect() as db:db.execute(f'DELETE FROM {kind} WHERE id=?',(identifier,))
        (directory/row['filename']).unlink(missing_ok=True)
        return jsonify(ok=True)

    return app
