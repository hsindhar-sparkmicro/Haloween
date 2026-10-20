# Local API

The browser and Python server share one origin. JSON endpoints are rooted at `/api`; no CORS access is enabled. Mutations with a different `Origin` are rejected. LAN mode is intended for a trusted household network and has no account system.

| Endpoint | Method | Input / result |
|---|---|---|
| `/window` | GET | Native window-control capabilities (local desktop only). |
| `/window/minimize` | POST | Minimize the server’s own Halloween Hub browser window; loopback requests only. |
| `/health` | GET | `{status, version, hardware}`; hardware is `simulated`. |
| `/state` | GET | Settings, candy, Halloween `countdown`, `party_countdown`, party records, tracks, weather, haunt, scan, newest 20 detections. |
| `/settings` | PATCH | Partial settings object; returns saved settings. |
| `/candy` | POST | `{delta: integer}`; returns `{candy}`. Counter cannot fall below zero. |
| `/records` | POST | `{kind: "guest" or "task", name: string}`; returns `{id}` with HTTP 201. |
| `/records/<id>` | PATCH / DELETE | PATCH accepts `name` and/or boolean `done`. |
| `/haunt` | POST | `{action: "activate"}`, `{action: "stop"}`, `{action: "motion"}`, or `{action: "set", key, value}`. `{action: "play", scene}` starts/replaces a selected scene; `{action: "random"}` starts a different scene. |
| `/scan` | POST | `{active: boolean}`. |
| `/logs` | GET | `{detections: [...]}` with up to 500 simulated events, newest first. |
| `/logs/export` | GET | CSV attachment with timestamps, room, simulated event and EMF. |
| `/locations?q=Toronto` | GET | `{results: [{name, latitude, longitude}]}` from Open-Meteo. |
| `/tracks` | POST | Multipart `file`: valid MP3, WAV or OGG, maximum request size 100 MiB; returns `{id,name}`. |
| `/tracks/<id>` | GET / DELETE | Audio with HTTP byte-range support, or removal from library and disk. |

Errors return JSON `{error: message}` with an appropriate HTTP status. Invalid settings/commands return 400, unknown records/tracks return 404, upload-limit violations return 413, and unavailable city search returns 503.

## Settings

Defaults: `timezone="America/Toronto"`, `units="C"`, `location=null`, `volume=40`, `rotation=false`, `reduced_motion=false`, `jumpscares=false`, `flicker=false`, `quality="auto"`, `party_date=""`, and `sensitivity="medium"`.

`location` contains `name`, `latitude` and `longitude`. `timezone` is an IANA identifier. `party_date` accepts a local ISO datetime (interpreted in the configured timezone), an explicitly offset ISO datetime, or an empty string for Halloween. It affects `party_countdown`; the dashboard `countdown` remains October 31. `quality` accepts `auto`, `low`, or `high`; sensitivity accepts `low`, `medium`, or `high`.

Haunt slider keys are `room`, `porch`, `fog`, and `sound` (0–100). Scene values are supplied by `scenes` in `/api/state` (eight scenes). Haunt state includes transient `run_id`, random `seed`, and `source` (manual/camera/test). During a sequence, only sound level remains editable; Stop restores the previous room/porch brightness and turns fog off. Activation is transient; scans and audio also never resume automatically after restart.

Weather is fetched asynchronously. Its status is `unset`, `loading`, `fresh`, `stale`, or `offline`. Cached temperatures are Celsius; the browser converts display units. State polling does not wait for upstream network responses.

Native Wayland window management follows the [wlr foreign-toplevel protocol](https://github.com/swaywm/wlr-protocols/blob/master/unstable/wlr-foreign-toplevel-management-unstable-v1.xml). Windows uses [ShowWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow).

## Hidden motion camera and encounters

`POST /api/camera` accepts `{action: "arm" | "disarm" | "stop" | "test"}`. Arm enables scan/rest duty cycles; disarm/stop release capture. Test queues a visitor reveal without camera use. Unsupported preview/mirror commands return 400. `GET /api/camera/frame` always returns 410, including delay queries. No endpoint provides camera imagery.

`/api/state.camera` contains numerical status, motion percentage, scan/trigger counts, capture-active flag, scan/rest timers, and Pi board temperature. Settings: `camera_area` (center/full/left/right), `camera_threshold` (integer 1–30, default 4), `camera_scan_seconds` (6–600, default 180), `camera_cooldown` (20–300, default 45), and `visitor_mode` (choose/play/story/surprise, default choose). Camera arming is transient.

`POST /api/encounter` accepts `{action: "start"}` for touch activation and `{action: "finish" | "heartbeat", id: <welcome-id>}` for that encounter. Welcome state identifies the active encounter, source, and lease deadline. Heartbeat refreshes a 120-second lease; stale IDs cannot cancel a newer encounter. Camera, touch, and test share this path. A busy encounter/haunt suppresses duplicate triggers. Automatic welcomes do not start the simulated detector. Visitor-launched scenes use haunt source `encounter`; manual scene commands take precedence.

`music_shuffle` is a persistent boolean setting (default true). Random selection occurs in the viewing browser from locally stored `/api/tracks`; there is no external scraping or online music-fetch endpoint. Audio still requires an explicit gesture.

## Local scene-effect library

`POST /api/effects` accepts the same multipart `file` format and validated MP3/WAV/OGG formats as `/api/tracks`. `GET /api/effects/<id>` serves local audio; DELETE removes it. `/api/state.effects` supplies effect IDs/names separately from music tracks. Content-addressed imports in each library return 201 for a new file or 200 with `duplicate: true` for existing content. Scene cue selection is local to the viewing browser; active audio and pending cue timers do not persist after restart.

## Welcome cutscene

`/api/state.cutscene` exposes availability, MP4 URL `/api/cutscene`, and an optional WebM fallback URL `/api/cutscene/webm`. Both GET routes serve only the fixed installed file from application data and support byte-range requests for video playback. Missing files return 404. Installation uses `scripts/import_cutscene.py`; there is no arbitrary-file browsing or camera footage endpoint. Touch encounters play the intro before showing the menu; camera/test encounters retain their existing reveal/preferences.

`/api/state.cutscene.items` lists installed named MP4s and optional WebM fallbacks. `GET /api/cutscenes/<filename>` serves only catalogued cutscene files, including byte ranges. Legacy `/api/cutscene` URLs retain Welcome compatibility. `/api/state.backgrounds` lists imported PNG images (served as `image/png`; WebP backgrounds are excluded) served by `GET /api/backgrounds/<filename>`; the original built-in background is retained by the client. Named files and backgrounds reside in application data, separately from music/effects and source assets.
