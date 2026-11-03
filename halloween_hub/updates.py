"""Download verified GitHub release packages; never execute or replace running code."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import threading
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener
from .version import VERSION, RELEASE_REPOSITORY

INTERVAL = 6 * 60 * 60
MAX_PACKAGE = 1024 * 1024 * 1024
HOSTS = {'api.github.com', 'github.com', 'release-assets.githubusercontent.com', 'objects.githubusercontent.com'}


def stable_version(tag):
    match = re.fullmatch(r'v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', tag or '')
    return tuple(map(int, match.groups())) if match else None


def newer(tag, current=VERSION):
    candidate = stable_version(tag)
    base = stable_version(current.split('-')[0])
    return bool(candidate and base and (candidate > base or (candidate == base and '-' in current)))


def sha256(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


class SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urlsplit(newurl)
        if target.scheme != 'https' or target.hostname not in HOSTS or target.port not in (None, 443):
            raise ValueError('Unexpected release download destination')
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected and target.hostname != 'api.github.com':
            redirected.remove_header('Authorization')
        return redirected


class GitHub:
    def __init__(self, repository=RELEASE_REPOSITORY):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
            raise ValueError('Invalid release repository')
        self.repository = repository
        self.opener = build_opener(SafeRedirect())

    def token(self):
        token = os.environ.get('HALLOWEEN_GITHUB_TOKEN', '').strip()
        if not token and shutil.which('gh'):
            try:
                token = subprocess.check_output(['gh', 'auth', 'token', '--hostname', 'github.com'],
                                                stderr=subprocess.DEVNULL, timeout=5, text=True).strip()
            except (OSError, subprocess.SubprocessError):
                pass
        return token

    def open(self, suffix, binary=False):
        headers = {'Accept': 'application/octet-stream' if binary else 'application/vnd.github+json',
                   'User-Agent': 'HalloweenHub/' + VERSION, 'X-GitHub-Api-Version': '2026-03-10'}
        token = self.token()
        if token:
            headers['Authorization'] = 'Bearer ' + token
        return self.opener.open(Request('https://api.github.com/repos/' + self.repository + suffix, headers=headers), timeout=30)

    def releases(self):
        # Inspect published releases by semantic version rather than creation-date order.
        with self.open('/releases?per_page=100') as response:
            data = response.read(4 * 1024 * 1024 + 1)
        if len(data) > 4 * 1024 * 1024:
            raise ValueError('Release listing is too large')
        releases = json.loads(data)
        if not isinstance(releases, list):
            raise ValueError('Invalid release listing')
        return releases

    def asset(self, identifier):
        if type(identifier) is not int or identifier <= 0:
            raise ValueError('Invalid release asset identifier')
        return self.open('/releases/assets/' + str(identifier), binary=True)


class ReleaseUpdates:
    def __init__(self, store, client=None, version=VERSION):
        self.store = store
        self.directory = store.root / 'updates'
        self.client = client or GitHub()
        self.version = version
        self.lock = threading.Lock()
        self.busy = False
        self.stop = threading.Event()
        self.ready = None
        self.last_attempt = 0
        self.info = dict(status='idle', message='Waiting for the first release check.', current_version=version,
                         repository=self.client.repository, latest_version=None, progress=0, checked_at=None)

    def snapshot(self):
        with self.lock:
            return dict(self.info, busy=self.busy,
                        download_url='/api/updates/package' if self.ready else None,
                        filename=self.ready.name if self.ready else None)

    def set(self, **changes):
        with self.lock:
            self.info.update(changes)

    def enabled(self):
        return self.store.get('settings').get('auto_download_updates', True)

    def start(self):
        def loop():
            if self.stop.wait(15):
                return
            while not self.stop.is_set():
                if self.enabled():
                    self.trigger()
                if self.stop.wait(INTERVAL):
                    return
        self.thread = threading.Thread(target=loop, name='release-scheduler', daemon=True)
        self.thread.start()

    def close(self):
        self.stop.set()

    def trigger(self):
        with self.lock:
            if self.busy or self.stop.is_set() or (self.last_attempt and time.monotonic() - self.last_attempt < 60):
                return False
            self.busy = True
            self.last_attempt = time.monotonic()
            self.info.update(status='checking', message='Checking GitHub releases…', progress=0)
        threading.Thread(target=self._run, name='release-download', daemon=True).start()
        return True

    def _run(self):
        try:
            self.check_download()
        except HTTPError as error:
            if error.code in (401, 404):
                message = 'GitHub access unavailable. Configure read access to this private repository on the server.'
            elif error.code in (403, 429):
                message = 'GitHub denied or limited this check. The app will retry later.'
            else:
                message = 'GitHub is unavailable. The app will retry later.'
            self.set(status='error', message=message)
        except (OSError, URLError, TimeoutError):
            self.set(status='error', message='Release check or download interrupted. Check connectivity and disk space; the app will retry later.')
        except (ValueError, KeyError, TypeError):
            self.set(status='error', message='Release package metadata or checksum could not be verified. No new package was saved.')
        except Exception:
            # Never expose response URLs, signed redirects, credentials or raw subprocess errors.
            self.set(status='error', message='The release check failed. The app will retry later.')
        finally:
            with self.lock:
                self.busy = False
                self.info['checked_at'] = datetime.now(timezone.utc).isoformat()

    def check_download(self):
        releases = [r for r in self.client.releases() if not r.get('draft') and not r.get('prerelease') and stable_version(r.get('tag_name'))]
        if not releases:
            self.set(status='current', message='No published stable releases yet.')
            return
        release = max(releases, key=lambda r: stable_version(r['tag_name']))
        tag = release['tag_name'].removeprefix('v')
        self.set(latest_version=tag)
        if not newer(tag, self.version):
            self.set(status='current', message='This version is up to date.')
            return
        filename = 'HalloweenHub-' + tag + '-source.zip'
        asset = next((a for a in release.get('assets', []) if a.get('name') == filename and a.get('state') == 'uploaded'), None)
        if not asset:
            self.set(status='waiting', message='Version ' + tag + ' is released; waiting for its source package.')
            return
        digest = asset.get('digest') or ''
        if not re.fullmatch(r'sha256:[0-9a-fA-F]{64}', digest):
            raise ValueError('Missing SHA-256 digest')
        expected = digest.split(':')[1].lower()
        size = asset.get('size')
        if type(size) is not int or not 0 < size <= MAX_PACKAGE:
            raise ValueError('Unsupported package size')
        self.directory.mkdir(parents=True, exist_ok=True)
        target = self.directory / filename
        if not (target.is_file() and target.stat().st_size == size and sha256(target) == expected and zipfile.is_zipfile(target)):
            if shutil.disk_usage(self.directory).free < size + 64 * 1024 * 1024:
                raise OSError('Insufficient disk space')
            temporary = target.with_suffix('.zip.part')
            try:
                total = 0
                actual = hashlib.sha256()
                self.set(status='downloading', message='Downloading version ' + tag + '…')
                with self.client.asset(asset['id']) as response, temporary.open('wb') as output:
                    while True:
                        if self.stop.is_set():
                            raise OSError('Stopped')
                        block = response.read(256 * 1024)
                        if not block:
                            break
                        total += len(block)
                        if total > size:
                            raise ValueError('Unexpected package size')
                        actual.update(block)
                        output.write(block)
                        self.set(progress=int(total / size * 100))
                    output.flush()
                    os.fsync(output.fileno())
                if total != size or actual.hexdigest() != expected:
                    raise ValueError('Checksum mismatch')
                if not zipfile.is_zipfile(temporary):
                    raise ValueError('Invalid ZIP package')
                temporary.replace(target)
            finally:
                temporary.unlink(missing_ok=True)
        with self.lock:
            self.ready = target
            self.info.update(status='ready', message='Version ' + tag + ' downloaded and verified. Ready for installation.', progress=100)
