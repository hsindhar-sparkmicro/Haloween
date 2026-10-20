import io
import tempfile
import unittest
from pathlib import Path
from halloween_hub.app import create_app
from halloween_hub.core import Store

class MediaTests(unittest.TestCase):
 def test_independent_persistent_idempotent_libraries(self):
  with tempfile.TemporaryDirectory() as root:
   app=create_app(root);client=app.test_client()
   try:
    content=Path('halloween_hub/static/assets/whisper.wav').read_bytes()
    def upload(kind,data=content,name='sample.wav'):
     return client.post('/api/'+kind,data={'file':(io.BytesIO(data),name)},content_type='multipart/form-data')
    track=upload('tracks');effect=upload('effects');again=upload('effects')
    self.assertEqual(track.status_code,201);self.assertEqual(effect.status_code,201);self.assertEqual(again.status_code,200)
    self.assertTrue(again.json['duplicate']);self.assertEqual(effect.json['id'],again.json['id'])
    with client.get('/api/effects/'+str(effect.json['id'])) as response:self.assertEqual(response.data,content)
    self.assertEqual(len(Store(root).rows('effects')),1);self.assertEqual(len(Store(root).rows('tracks')),1)
    self.assertEqual(upload('effects',b'<html>bad</html>','bad.mp3').status_code,400)
    self.assertEqual(client.delete('/api/effects/'+str(effect.json['id'])).status_code,200)
    self.assertEqual(client.get('/api/effects/'+str(effect.json['id'])).status_code,404)
    with client.get('/api/tracks/'+str(track.json['id'])) as response:self.assertEqual(response.status_code,200)
   finally:app.extensions['camera'].close();app.extensions['simulation'].close()

 def test_optional_cutscene_and_byte_ranges(self):
  with tempfile.TemporaryDirectory() as root:
   app=create_app(root);client=app.test_client()
   try:
    self.assertFalse(client.get('/api/state').json['cutscene']['available'])
    self.assertEqual(client.get('/api/cutscene').status_code,404)
    folder=Path(root)/'cutscenes';folder.mkdir();data=b'\x00\x00\x00\x18ftypisom'+bytes(range(128));(folder/'welcome.mp4').write_bytes(data)
    self.assertTrue(client.get('/api/state').json['cutscene']['available'])
    with client.get('/api/cutscene',headers={'Range':'bytes=8-23'}) as response:
     self.assertEqual(response.status_code,206);self.assertEqual(response.data,data[8:24]);self.assertEqual(response.mimetype,'video/mp4')
     self.assertEqual(response.headers['Content-Range'],f'bytes 8-23/{len(data)}')
   finally:app.extensions['camera'].close();app.extensions['simulation'].close()

 def test_gallery_preserves_original_and_adds_named_media(self):
  with tempfile.TemporaryDirectory() as root:
   app=create_app(root);client=app.test_client()
   try:
    directory=Path(root)/'cutscenes';directory.mkdir()
    for name in ['welcome','nun','pumpkin-scare']:(directory/(name+'.mp4')).write_bytes(b'video-data')
    (directory/'nun.webm').write_bytes(b'fallback-data')
    images=Path(root)/'backgrounds';images.mkdir();(images/'new.png').write_bytes(b'\x89PNG\r\n\x1a\nimage-data');(images/'old.webp').write_bytes(b'RIFF0000WEBPdata')
    state=client.get('/api/state').json
    self.assertEqual([v['id'] for v in state['cutscene']['items']],['welcome','nun','pumpkin-scare'])
    self.assertEqual([v['url'] for v in state['backgrounds']],['/api/backgrounds/new.png'])
    self.assertEqual(client.get('/api/backgrounds/old.webp').status_code,404)
    self.assertEqual(state['cutscene']['items'][1]['webm_url'],'/api/cutscenes/nun.webm')
    with client.get('/api/cutscenes/nun.mp4',headers={'Range':'bytes=0-4'}) as r:self.assertEqual(r.status_code,206);self.assertEqual(r.data,b'video')
    with client.get('/api/backgrounds/new.png') as r:self.assertEqual(r.mimetype,'image/png');self.assertEqual(r.status_code,200)
    self.assertEqual(client.get('/api/cutscenes/missing.mp4').status_code,404)
    self.assertEqual(client.get('/api/backgrounds/missing.png').status_code,404)
   finally:app.extensions['camera'].close();app.extensions['simulation'].close()
