import tempfile
import time
import unittest
from unittest.mock import Mock,patch
from halloween_hub.app import create_app
from halloween_hub.core import SCENES


class CameraTests(unittest.TestCase):
 def setUp(self):
  self.root=tempfile.TemporaryDirectory();self.app=create_app(self.root.name);self.client=self.app.test_client()
  self.camera=self.app.extensions['camera'];self.sim=self.app.extensions['simulation']
 def tearDown(self):
  self.camera.close();self.sim.close();self.root.cleanup()
 def sample(self,score):self.camera.consume({'scores':{'center':score},'warming':False})
 def test_images_and_legacy_preview_disabled(self):
  self.assertFalse(self.client.get('/api/state').json['camera']['enabled'])
  self.assertEqual(self.client.get('/api/state').json['settings']['camera_scan_seconds'],180)
  for value in (6,120,180,600):
   self.assertEqual(self.client.patch('/api/settings',json={'camera_scan_seconds':value}).status_code,200)
  self.assertEqual(self.client.get('/api/camera/frame').status_code,410)
  self.assertEqual(self.client.get('/api/camera/frame?delay=2').status_code,410)
  self.assertEqual(self.client.post('/api/camera',json={'action':'preview'}).status_code,400)
  self.assertFalse(hasattr(self.camera,'frame'))
  for value in [True,0,601,'180']:
   self.assertEqual(self.client.patch('/api/settings',json={'camera_scan_seconds':value}).status_code,400)
  self.assertEqual(self.client.patch('/api/settings',json={'visitor_mode':'camera-video'}).status_code,400)
 def test_motion_confirmation_only_during_active_scan(self):
  self.camera.armed=True;self.camera.process=Mock()
  for i in range(5):self.sample(0)
  self.sample(10);self.sample(10);self.assertFalse(self.sim.welcome['active'])
  self.sample(10);self.assertTrue(self.sim.welcome['active']);self.assertEqual(self.sim.welcome['source'],'camera')
  self.assertFalse(self.sim.scan['active']);self.assertTrue(self.camera.detected)
  self.camera.end_scan();self.sim.cancel_welcome()
  for i in range(10):self.sample(10)
  self.assertEqual(self.camera.triggers,1)
  self.assertGreater(self.camera.snapshot()['cooldown'],0)
 def test_every_scan_stops_capture_even_without_motion(self):
  process=Mock();self.camera.available=True;self.camera.armed=True
  with patch('halloween_hub.camera.subprocess.Popen',return_value=process),patch.object(self.camera,'read'):
   self.camera.start_scan(time.monotonic());self.assertTrue(self.camera.snapshot()['capture_active']);self.assertGreater(self.camera.snapshot()['scan_remaining'],170)
   self.assertFalse(self.camera.detected);self.camera.end_scan()
  process.terminate.assert_called_once();process.wait.assert_called()
  self.assertFalse(self.camera.snapshot()['capture_active']);self.assertGreaterEqual(self.camera.snapshot()['cooldown'],44)
  self.assertTrue(self.camera.snapshot()['armed'])
 def test_board_temperature_guard_has_hysteresis(self):
  with patch('halloween_hub.camera.shutil.which',return_value='/usr/bin/vcgencmd'),patch('halloween_hub.camera.subprocess.run') as command:
   command.return_value.stdout="temp=71.0'C";self.camera.sample_temperature(100);self.assertTrue(self.camera.heat_pause)
   command.return_value.stdout="temp=67.0'C";self.camera.sample_temperature(106);self.assertTrue(self.camera.heat_pause)
   command.return_value.stdout="temp=64.0'C";self.camera.sample_temperature(112);self.assertFalse(self.camera.heat_pause)
 def test_visitor_lease_duplicate_and_release(self):
  event=self.client.post('/api/encounter',json={'action':'start'}).json
  self.assertEqual(event['source'],'touch');self.assertTrue(event['active'])
  self.assertEqual(self.client.post('/api/encounter',json={'action':'start'}).status_code,400)
  self.client.post('/api/encounter',json={'action':'finish','id':event['id']+1});self.assertTrue(self.sim.welcome['active'])
  self.client.post('/api/encounter',json={'action':'finish','id':event['id']});self.assertFalse(self.sim.welcome['active'])
 def test_welcome_does_not_auto_start_scene_or_detector(self):
  self.client.post('/api/camera',json={'action':'test'})
  self.assertTrue(self.sim.welcome['active']);self.assertFalse(self.sim.scan['active'])
  self.assertFalse(self.camera.snapshot()['enabled'])
  self.sim.welcome_deadline=time.monotonic()-1;time.sleep(1.1)
  self.assertFalse(self.sim.welcome['active']);self.assertFalse(self.sim.haunt['active'])
 def test_manual_scene_blocks_trigger_and_scene_preserves_lease(self):
  self.sim.command({'action':'play','scene':'Phantom train'});self.assertFalse(self.sim.welcome_motion())
  self.sim.command({'action':'stop'});self.sim.welcome_motion()
  self.sim.command({'action':'random','_source':'encounter'});self.assertTrue(self.sim.welcome['active'])
  self.sim.command({'action':'stop'});self.assertFalse(self.sim.welcome['active'])
 def test_all_scenes_have_random_runs(self):
  self.assertEqual(len(SCENES),8)
  for name in SCENES:
   first=self.sim.command({'action':'play','scene':name});second=self.sim.command({'action':'play','scene':name})
   self.assertNotEqual(first['seed'],second['seed'])
