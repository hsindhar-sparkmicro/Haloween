import io
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo
from halloween_hub.app import create_app
from halloween_hub.core import DEFAULTS, countdown
from halloween_hub.weather import Weather


class HubTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app(self.tmp.name)
        self.client = self.app.test_client()
        self.sim = self.app.extensions['simulation']
        self.store = self.app.extensions['store']

    def tearDown(self):
        self.sim.close()
        self.tmp.cleanup()

    def test_independent_countdowns(self):
        self.client.patch('/api/settings',json={'party_date':'2030-10-20T20:00'})
        state=self.client.get('/api/state').json
        halloween=datetime.fromisoformat(state['countdown']['target'])
        self.assertEqual((halloween.month,halloween.day),(10,31))
        self.assertTrue(state['party_countdown']['target'].startswith('2030-10-20'))

    def test_selected_random_scene_and_replacement(self):
        for name in ('Quiet shadows','Purple mist','Pumpkin parade'):
            result=self.client.post('/api/haunt',json={'action':'play','scene':name}).json
            self.assertTrue(result['active'])
            self.assertEqual(result['scene'],name)
            self.assertIn(name,result['stage'])
            self.assertTrue(result['audio'].endswith('-scene.wav'))
        result=self.client.post('/api/haunt',json={'action':'random'}).json
        self.assertNotEqual(result['scene'],'Pumpkin parade')
        self.assertTrue(result['active'])
        with self.sim.lock:
            self.sim.started=time.monotonic()-21
        time.sleep(1.1)
        self.assertFalse(self.sim.snapshot()['haunt']['active'])
        self.assertEqual(self.sim.snapshot()['haunt']['progress'],100)
        self.assertEqual(self.client.post('/api/haunt',json={'action':'play','scene':'Unknown'}).status_code,400)

    def test_native_minimize_local_guard_and_unavailable(self):
        with patch('halloween_hub.app.manage_window',return_value={'available':True,'backend':'Wayland'}) as manager:
            self.assertEqual(self.client.post('/api/window/minimize',json={}).status_code,200)
            manager.assert_called_with('minimize')
            self.assertEqual(self.client.post('/api/window/minimize',json={},environ_base={'REMOTE_ADDR':'192.168.0.50'}).status_code,403)
        with patch('halloween_hub.app.manage_window',side_effect=OSError('Unavailable')):
            self.assertEqual(self.client.post('/api/window/minimize',json={}).status_code,409)

    def test_persistence_and_safe_restart(self):
        self.client.post('/api/candy', json={'delta': 5})
        self.client.post('/api/records', json={'kind':'guest','name':'Luna'})
        self.client.patch('/api/settings', json={'units':'F','rotation':True})
        self.client.post('/api/haunt', json={'action':'activate'})
        other = create_app(self.tmp.name)
        try:
            state = other.test_client().get('/api/state').json
            self.assertEqual(state['candy'], 5)
            self.assertEqual(state['records'][0]['name'], 'Luna')
            self.assertEqual(state['settings']['units'], 'F')
            self.assertFalse(state['haunt']['active'])
            self.assertFalse(state['scan']['active'])
        finally:
            other.extensions['simulation'].close()

    def test_candy_atomic_and_clamped(self):
        with ThreadPoolExecutor(max_workers=8) as workers:
            list(workers.map(lambda _: self.store.candy(1), range(40)))
        self.assertEqual(self.store.get('candy'), 40)
        self.assertEqual(self.client.post('/api/candy', json={'delta':-80}).json['candy'], 0)
        self.assertEqual(self.client.post('/api/candy', json={'delta':True}).status_code, 400)

    def test_record_edit_and_delete(self):
        ident = self.client.post('/api/records', json={'kind':'task','name':'Buy candy'}).json['id']
        self.assertEqual(self.client.patch(f'/api/records/{ident}', json={'done':True,'name':'Buy treats'}).status_code, 200)
        row = self.client.get('/api/state').json['records'][0]
        self.assertEqual(row['name'], 'Buy treats')
        self.assertEqual(row['done'], 1)
        self.client.delete(f'/api/records/{ident}')
        self.assertEqual(self.store.rows('records'), [])
        self.assertEqual(self.client.delete(f'/api/records/{ident}').status_code, 404)

    def test_scene_presets_and_light_sequence(self):
        result = self.client.post('/api/haunt', json={'action':'set','key':'scene','value':'Purple mist'}).json
        self.assertEqual((result['room'],result['porch'],result['fog']), (25,40,60))
        self.client.post('/api/haunt', json={'action':'activate'})
        time.sleep(1.1)
        self.assertLess(self.sim.snapshot()['haunt']['room'],25)
        self.assertEqual(self.client.post('/api/haunt', json={'action':'set','key':'room','value':90}).status_code,400)
        self.client.post('/api/haunt',json={'action':'stop'})
        self.assertEqual(self.sim.snapshot()['haunt']['room'],25)
        self.assertEqual(self.sim.snapshot()['haunt']['fog'],0)
        self.client.post('/api/haunt',json={'action':'set','key':'room','value':90})
        self.client.post('/api/haunt',json={'action':'stop'})
        self.assertEqual(self.sim.snapshot()['haunt']['room'],90)

    def test_haunt_and_scan_stop(self):
        self.client.post('/api/haunt', json={'action':'activate'})
        self.assertTrue(self.sim.snapshot()['haunt']['active'])
        self.client.post('/api/haunt', json={'action':'stop'})
        self.assertEqual(self.sim.snapshot()['haunt']['fog'], 0)
        self.client.post('/api/scan', json={'active':True})
        time.sleep(1.1)
        self.assertGreater(len(self.store.rows('detections')), 0)
        self.client.post('/api/scan', json={'active':False})
        old = self.sim.snapshot()['scan']['emf']
        time.sleep(1.1)
        self.assertEqual(self.sim.snapshot()['scan']['emf'], old)
        self.assertIn('simulated', self.client.get('/api/logs/export').text.lower())

    def test_settings_validation_and_origin(self):
        for data in [{'units':'K'}, {'timezone':'Mars/Orbit'}, {'volume':101}, {'rotation':'yes'},
                     {'location':{'name':'Invalid','latitude':999,'longitude':0}}, {'party_date':'nonsense'}]:
            self.assertEqual(self.client.patch('/api/settings', json=data).status_code,400)
        self.assertEqual(self.client.post('/api/candy', json={'delta':1},headers={'Origin':'https://example.org'}).status_code,403)

    def test_audio_rejection_and_range(self):
        response = self.client.post('/api/tracks', data={'file':(io.BytesIO(b'not audio'),'wrong.mp3')})
        self.assertEqual(response.status_code,400)
        with open('halloween_hub/static/assets/whisper.wav','rb') as f:
            ident = self.client.post('/api/tracks', data={'file':(io.BytesIO(f.read()),'wind.wav')}).json['id']
        with self.client.get(f'/api/tracks/{ident}',headers={'Range':'bytes=0-63'}) as response:
            self.assertEqual(response.status_code,206)
        self.assertEqual(self.client.delete(f'/api/tracks/{ident}').status_code,200)

    def test_weather_offline_and_stale(self):
        weather = Weather(self.store)
        location = {'name':'Test','latitude':43,'longitude':-79}
        self.store.put('weather',{'key':'43,-79','fetched':time.time()-1000,'current':{'temperature_2m':4}})
        weather.retry_at = time.time()+60
        self.assertEqual(weather.snapshot(location)['status'],'stale')
        self.assertEqual(weather.snapshot(None)['status'],'unset')
        with patch('halloween_hub.weather.fetch',side_effect=OSError('offline')):
            weather.refresh(location,'43,-79')
        self.assertGreater(weather.retry_at,time.time())
        self.assertEqual(weather.snapshot({'latitude':0,'longitude':0})['status'],'offline')

    def test_halloween_and_timezone_countdown(self):
        zone=ZoneInfo('America/Toronto')
        self.assertEqual(countdown(DEFAULTS,datetime(2026,10,31,12,tzinfo=zone))['seconds'],0)
        after=countdown(DEFAULTS,datetime(2026,11,1,tzinfo=zone))
        self.assertTrue(after['target'].startswith('2027-10-31'))
        custom=dict(DEFAULTS,party_date='2026-10-31T20:00')
        self.assertEqual(countdown(custom,datetime(2026,10,31,19,tzinfo=zone))['seconds'],3600)
        utc=datetime(2026,11,1,2,tzinfo=ZoneInfo('UTC'))
        self.assertEqual(countdown(DEFAULTS,utc)['seconds'],0)


if __name__ == '__main__':
    unittest.main()
