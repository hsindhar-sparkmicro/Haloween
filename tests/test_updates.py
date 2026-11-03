import hashlib
import io
import tempfile
import unittest
import time
import zipfile
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request
from urllib.error import HTTPError
from halloween_hub.core import Store
from halloween_hub.updates import ReleaseUpdates, SafeRedirect, newer
from halloween_hub.app import create_app


class FakeGitHub:
    repository = 'test/repo'
    def __init__(self, payload=None):
        if payload is None:
            buffer=io.BytesIO()
            with zipfile.ZipFile(buffer,'w') as archive:
                archive.writestr('HalloweenHub/README.md','Fixture package')
            payload=buffer.getvalue()
        self.payload = payload
        self.downloads = 0
        self.error = None
        self.items = [dict(tag_name='v1.2.0', draft=False, prerelease=False, assets=[dict(
            id=7, name='HalloweenHub-1.2.0-source.zip', state='uploaded', size=len(payload),
            digest='sha256:' + hashlib.sha256(payload).hexdigest())])]
    def releases(self):
        if self.error:
            raise self.error
        return self.items
    def asset(self, identifier):
        self.downloads += 1
        return io.BytesIO(self.payload)


class UpdatesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(self.temp.name)
        self.client = FakeGitHub()
        self.updates = ReleaseUpdates(self.store, self.client, version='1.1.0-sneak.1')
    def tearDown(self):
        self.updates.close()
        self.temp.cleanup()
    def test_version_order_and_stable_promotion(self):
        self.assertTrue(newer('v1.10.0', '1.9.0'))
        self.assertTrue(newer('1.1.0', '1.1.0-sneak.1'))
        for tag in ['1.0.9', '1.1.0', '1.2.0-rc.1', '../../evil', 'v01.2.3']:
            self.assertFalse(newer(tag, '1.1.0'))
    def test_verified_atomic_download_reused_after_restart(self):
        self.updates._run()
        state = self.updates.snapshot()
        self.assertEqual(state['status'], 'ready')
        self.assertEqual(self.updates.ready.read_bytes(), self.client.payload)
        self.assertFalse(list(self.updates.directory.glob('*.part')))
        again = ReleaseUpdates(self.store, self.client, version='1.1.0')
        again._run()
        self.assertEqual(again.snapshot()['status'], 'ready')
        self.assertEqual(self.client.downloads, 1)
    def test_drafts_prereleases_and_older_releases_not_downloaded(self):
        for flags in [dict(draft=True), dict(prerelease=True), dict(tag_name='v1.0.0')]:
            self.client.items[0].update(draft=False, prerelease=False, tag_name='v1.2.0')
            self.client.items[0].update(flags)
            self.updates._run()
            self.assertEqual(self.updates.snapshot()['status'], 'current')
        self.assertEqual(self.client.downloads, 0)
    def test_checksum_size_and_truncated_download_cleanup(self):
        for payload in [b'bad', self.client.payload+b'extra', b'x'*len(self.client.payload)]:
            self.client.payload = payload
            self.updates._run()
            self.assertEqual(self.updates.snapshot()['status'], 'error')
            self.assertIsNone(self.updates.ready)
            self.assertFalse(list(self.updates.directory.glob('*')))
    def test_digest_required_and_asset_name_exact(self):
        asset = self.client.items[0]['assets'][0]
        asset['digest'] = None
        self.updates._run()
        self.assertEqual(self.updates.snapshot()['status'], 'error')
        asset['name'] = '../../file.zip'
        self.updates._run()
        self.assertEqual(self.updates.snapshot()['status'], 'waiting')
        self.assertEqual(self.client.downloads, 0)
    def test_interrupted_stream_and_invalid_archive_never_ready(self):
        class Interrupted(io.BytesIO):
            def read(self, amount=-1):
                if self.tell():
                    raise OSError('Connection lost')
                return super().read(10)
        with patch.object(self.client, 'asset', return_value=Interrupted(self.client.payload)):
            self.updates._run()
        self.assertIsNone(self.updates.ready)
        self.assertFalse(list(self.updates.directory.glob('*')))
        self.updates.client = FakeGitHub(b'not a ZIP even with a matching digest')
        self.updates._run()
        self.assertEqual(self.updates.snapshot()['status'], 'error')
        self.assertFalse(list(self.updates.directory.glob('*')))
    def test_scheduler_checks_at_startup_then_six_hours_and_respects_opt_out(self):
        for enabled in (True, False):
            self.store.put('settings', {'auto_download_updates': enabled})
            with patch.object(self.updates.stop, 'wait', side_effect=[False, True]) as wait, patch.object(self.updates, 'trigger') as trigger:
                self.updates.start()
                self.updates.thread.join(1)
                self.assertFalse(self.updates.thread.is_alive())
                self.assertEqual(trigger.call_count, int(enabled))
                self.assertEqual([call.args[0] for call in wait.call_args_list], [15, 21600])
    def test_offline_auth_error_and_stop_leave_app_usable(self):
        for error in [OSError('secret URL'), HTTPError('secret URL', 404, 'private', {}, None)]:
            self.client.error = error
            self.updates._run()
            self.assertEqual(self.updates.snapshot()['status'], 'error')
            self.assertNotIn('secret', str(self.updates.snapshot()))
            self.assertFalse(self.updates.snapshot()['busy'])
        self.client.error = None
        self.updates.close()
        self.updates._run()
        self.assertIsNone(self.updates.ready)
        self.assertFalse(list(self.updates.directory.glob('*.part')))
    def test_redirect_strips_credentials_and_rejects_unknown_hosts(self):
        req = Request('https://api.github.com/repos/test/repo/releases/assets/7', headers={'Authorization':'Bearer secret'})
        handler = SafeRedirect()
        redirected = handler.redirect_request(req, None, 302, '', {}, 'https://release-assets.githubusercontent.com/file?signature=test')
        self.assertIsNone(redirected.get_header('Authorization'))
        for url in ['http://release-assets.githubusercontent.com/file', 'https://attacker.example/file', 'https://api.github.com:8443/file']:
            with self.assertRaises(ValueError):
                handler.redirect_request(req, None, 302, '', {}, url)
    def test_single_job_and_manual_check_cooldown(self):
        with patch('halloween_hub.updates.threading.Thread') as thread:
            self.assertTrue(self.updates.trigger())
            self.assertFalse(self.updates.trigger())
            self.assertEqual(thread.call_count, 1)
            self.updates.busy = False
            self.assertFalse(self.updates.trigger())
    def test_auto_download_setting_and_local_only_endpoints(self):
        app = create_app(self.temp.name)
        try:
            updates = app.extensions['updates']
            updates.client = self.client
            client = app.test_client()
            self.assertEqual(client.patch('/api/settings',json={'auto_download_updates':'yes'}).status_code,400)
            self.assertEqual(client.patch('/api/settings',json={'auto_download_updates':False}).status_code,200)
            self.assertFalse(updates.enabled())
            self.assertEqual(client.post('/api/updates/check',environ_overrides={'REMOTE_ADDR':'10.0.0.2'}).status_code,403)
            self.assertEqual(client.post('/api/updates/check',headers={'Origin':'https://attacker.example'}).status_code,403)
            self.assertEqual(client.get('/api/updates/package').status_code,404)
            self.assertEqual(client.post('/api/updates/check',json={}).status_code,202)
            deadline=time.monotonic()+3
            while updates.snapshot()['busy'] and time.monotonic()<deadline:
                time.sleep(.01)
            self.assertEqual(updates.snapshot()['status'],'ready')
            response = client.get('/api/updates/package')
            self.assertEqual(response.data,self.client.payload)
            self.assertIn('attachment', response.headers['Content-Disposition'])
            response.close()
            self.assertEqual(client.get('/api/updates/package',environ_overrides={'REMOTE_ADDR':'10.0.0.2'}).status_code,403)
            self.assertIsNone(client.get('/api/updates',environ_overrides={'REMOTE_ADDR':'10.0.0.2'}).json['download_url'])
        finally:
            app.extensions['updates'].close()
            app.extensions['camera'].close()
            app.extensions['simulation'].close()


if __name__ == '__main__':
    unittest.main()
