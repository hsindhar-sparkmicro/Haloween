# GitHub release downloads

The kiosk checks `hsindhar-sparkmicro/Haloween` 15 seconds after launch and then every six hours. **Settings → App updates** shows the installed version, check/download status and progress. Automatic downloading is enabled by default and can be disabled using the checkbox and **Save settings**. **Check & download** performs a manual check (limited to once per minute).

This downloads a package; it does not extract, install, restart, run shell commands from a release, overwrite the checkout, or change user data. Packages are saved under `<HALLOWEEN_DATA_DIR>/updates/` (or the normal application data directory). **Save verified package** copies the completed package to the local browser's downloads folder. Management and package-serving endpoints are loopback-only; on a remote kiosk use its local browser or an SSH-forwarded connection.

## Private repository access

This repository is private. On each kiosk/server, supply a fine-grained token with **Contents: read** access to this repository through `HALLOWEEN_GITHUB_TOKEN`, or sign into the GitHub CLI as the account running the app. An existing `gh auth token --hostname github.com` credential is used when the environment token is absent. Tokens are only used by the Python server, never stored in settings, sent to the frontend or forwarded to asset storage hosts. Service installations need the environment or CLI credential available to the service account. Missing access, network outages and rate limits appear in Settings and leave the app running.

## Release contract

1. Update `VERSION` in `halloween_hub/version.py` to the intended release version. This working branch is `1.1.0-sneak.1`; prereleases are not automatically downloaded.
2. Run `python scripts/package.py`. It produces `dist/HalloweenHub-<VERSION>-source.zip` and an external `.zip.sha256` file. The archive also includes its per-file `SHA256SUMS`.
3. When publication is requested, publish a non-draft, non-prerelease GitHub Release tagged `vMAJOR.MINOR.PATCH` (or without `v`) and attach the correspondingly named source ZIP. GitHub's automatically generated asset SHA-256 digest is required by the downloader. The external checksum file is useful for manual verification.
4. The updater considers the highest stable semantic version in the latest 100 release records. A stable release of the same base version supersedes this prerelease. Older/equal installed stable versions, draft releases, prereleases, generic GitHub source snapshots and differently named packages are ignored.

Downloads use the authenticated release-asset API. HTTPS redirects are restricted to GitHub's API/site/asset hosts and remove authorization when leaving the API host. The size is bounded to 1 GiB; the expected size and SHA-256 must match and the file must be a valid ZIP before a `.part` file is atomically renamed to the final ZIP. Partial files are removed on failures handled by the running process; a file left by a hard crash is overwritten by the next attempt. Existing matching packages are rehashed and reused. Packages from earlier releases are retained for manual rollback/cleanup. Disabling automatic checks stops future scheduled checks; an already-running transfer can finish.

The first check is started by the normal `python -m halloween_hub` launcher. Custom WSGI hosts must call `app.extensions['updates'].start()` once for their serving process. Flask app construction alone does not start network checks, which also keeps unit tests isolated.

API: `GET /api/updates` reports status; `POST /api/updates/check` schedules a check/download; `GET /api/updates/package` serves the current verified file. `/api/health` and the packaging script share the same version constant.

Implementation follows GitHub's [release listing API](https://docs.github.com/en/rest/releases/releases#list-releases) and [release asset download API](https://docs.github.com/en/rest/releases/assets#get-a-release-asset). On November 3, 2026, the configured repository had no published releases. Live access can be checked now; the full new-release download path is tested with local fixtures until a real package is published. Nothing is published automatically.
