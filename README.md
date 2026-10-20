# Halloween Hub

A four-screen, offline-first Halloween kiosk for **Windows amd64**, **Linux amd64**, and **Raspberry Pi ARM64**. Python serves a locally bundled browser UI; no Node build, GPIO, microphone, or camera is required.

![Pumpkin dashboard](validation/screenshots/dashboard-800x480.png)

## Start

Install Python **3.11–3.13** with pip and venv, and use a current Chromium, Chrome, Edge, or Firefox browser.

Linux / Raspberry Pi:

```bash
./run.sh
```

Windows PowerShell (Python launcher `py` must be installed):

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

Open **http://127.0.0.1:8080**. Launchers create `.venv`, install pinned requirements when needed, and open your default browser. Internet is needed for the first dependency installation, weather and city search; all artwork, fonts, ambience, recipes, simulation and party records work offline afterward. On Debian, install `python3-venv` if environment creation is unavailable.

Server without automatically opening a browser:

```bash
./run.sh --no-browser
```

On the Pi's graphical desktop, launch the server in one terminal and kiosk in another:

```bash
./kiosk.sh
```

The kiosk has its own Chromium profile and does not require creating a desktop keyring. The header **−** button minimizes the native kiosk window to the desktop; restore it from the desktop task switcher. The **⛶** button separately toggles browser document fullscreen. Use **Alt+F4** to close it. Use **Ctrl+C** in the server terminal to stop the server.

## Raspberry Pi autostart on boot

Run once as the Pi's normal desktop user (without `sudo`), after preparing dependencies with `./run.sh`:

```bash
.venv/bin/python scripts/pi_autostart.py install --port 8088
```

Enable **Desktop Autologin** in Raspberry Pi Configuration (or `sudo raspi-config`, System Options → Boot / Auto Login → Desktop Autologin). On boot, the user service starts the server and the desktop opens Chromium in kiosk mode after the server responds. The installer starts the server immediately; Chromium opens at the next desktop login. No dependency downloads occur during boot. The app uses the deployment's `data/` folder, preserving existing Pi records and media. Run the installer from a permanent location; reinstall after moving the folder. The server stays on loopback.

Check status and logs:

```bash
systemctl --user status halloween-hub
journalctl --user -u halloween-hub -b
```

Remove autostart and stop its server:

```bash
.venv/bin/python scripts/pi_autostart.py remove
```

Close any open kiosk with **Alt+F4**. Removing autostart preserves application data and the Pi's desktop login settings. Stop any manually launched Halloween Hub server before installing to avoid a port conflict. For a different port, supply `--port` when installing; the browser uses the same port.

## Remote / headless

Explicitly enable trusted-LAN access:

```bash
./run.sh --lan --no-browser --port 8088
```

Open `http://<host-ip>:8088` on another computer. This is a household LAN interface without accounts; everyone who can reach it can modify party records, settings and the music library. Default launch binds to loopback only. Audio plays on the **viewing device**, including when the server is a headless Pi.

An SSH tunnel retains loopback-only access:

```bash
ssh -L 18088:127.0.0.1:8088 spark@192.168.0.100
```

Then open `http://127.0.0.1:18088` locally.

## Four screens

- **Dashboard:** immersive haunted background, countdown and floating weather. Tap the pumpkin for adventures. Play spooky sounds shuffles your imported effects.
- **Haunted House:** simulated lights, fog and motion, effect-level controls and eight distinct animated scenes. Selecting or randomizing opens immersive playback with only a small Back overlay. Back/Escape stops immediately; completion returns automatically to the panel. Each replay gets new smooth fog formations and wind, and each scene has its own background, characters and sound. Activate replays the selection. Reduced motion uses still phase compositions. Hardware controls remain simulated.
- **Party Hub:** editable tasks and guests, attendance, three rotating recipe cards, local playlist, real audio-reactive equalizer, and optional floating ghosts.
- **Ghost Detector:** start/stop the simulated scan, choose sensitivity, watch room activity and readings, inspect the journal or export CSV. Readings are fictional entertainment, not measurements.

Settings include IANA timezone, Celsius/Fahrenheit, volume, animation quality, party date, rotation, reduced motion, optional scares and flicker. Rotation is off by default; when enabled it waits two minutes after your most recent interaction, then changes screens every 30 seconds. Open dialogs pause rotation. Audio always starts paused, even after restart. Haunt sequences and scans also start stopped.

The dashboard countdown always targets local **October 31 at midnight**; throughout Halloween it reads zero, then targets the next year. The Party Hub uses a custom party date in the configured timezone when set, without changing the Halloween dashboard; it reads zero after the party starts. The backend host's clock must be correct.

Weather uses Open-Meteo with attribution and a 15-minute cache. Previously fetched forecasts remain visible as stale when offline. City selection is saved immediately; other settings use Save. Set location once rather than shipping a misleading default forecast.

Native minimize is shown in desktop/kiosk launch mode and acts on the server’s own Halloween Hub browser window. Pi Wayland support is verified; Windows support uses the native window API, and X11 requires `xdotool`. Other desktop compositors can report unavailable. Ordinary remote browser views use their own browser window controls.

The free API is intended here for personal/non-commercial use; see [Open-Meteo terms](https://open-meteo.com/en/terms).

## Audio and data

Import MP3, WAV or OGG files from Party Hub → Library. Maximum file size is 100 MB. Imports remain on the server; incompatible codecs report a playback error. Click the header music button to enable audio, or Play music/Play spooky sounds. Click the header button again to pause all audio. Automatic playback is never forced past browser restrictions.

Data defaults to `%LOCALAPPDATA%\HalloweenHub` on Windows and `~/.local/share/HalloweenHub` on Linux. `HALLOWEEN_DATA_DIR` overrides it. The SQLite database stores settings, candy, tasks, guests, tracks, cached weather, and the newest 500 detections. Music is copied into the data directory. Back up this directory with the server stopped.

```bash
HALLOWEEN_DATA_DIR="$PWD/my-data" ./run.sh
```

For offline setup, prepare compatible wheels and set `HALLOWEEN_WHEEL_DIR`. The ARM64 wheel bundle in the release is specifically for the tested Pi's Python **3.13**:

```bash
HALLOWEEN_WHEEL_DIR="$PWD/pi-wheels" ./run.sh --no-browser
```

## Validation and development

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Optional browser QA requires `requirements-dev.txt` and `python -m playwright install chromium`. Start the server first, then:

```bash
.venv/bin/python scripts/check_browser.py
.venv/bin/python scripts/check_resilience.py
.venv/bin/python scripts/check_immersive.py
.venv/bin/python scripts/check_welcome.py
```

Browser checks create screenshots at 800×480, 1280×720 and 1920×1080, check layout/control visibility, and exercise editing, audio, scan and haunt controls. The resilience check uses live city search/weather and verifies reconnect, reduced motion and muted startup. These checks modify test app data; use `HALLOWEEN_DATA_DIR` to isolate it.

Public JSON endpoints are documented in [API.md](API.md).

See [VALIDATION.md](VALIDATION.md) for actual results, platform boundaries, Pi deployment details and the endurance record. Build portable source releases using `python scripts/package.py`; archives include instructions, all runtime assets, and SHA256SUMS, never user data or environments.

## Asset provenance

`halloween_hub/static/assets/art-sheet.png` was generated with the built-in imagegen tool, then bundled locally. It contains six moody black-background illustrations: an uncarved pumpkin, Edison bulb, fog machine, lavender ghost, purple speaker, and moonlit house; SVG overlays animate the pumpkin's face. Full generation prompt: [ARTWORK.md](ARTWORK.md). Fonts are DejaVu with the bundled license. Ambient WAV files are original deterministic synthesis from `scripts/generate_audio.py`.

## Hidden camera and visitor adventures

Tap/click the Dashboard pumpkin (or press Enter when focused) to play the installed welcome cutscene, then choose **Play**, **Story**, or **Surprise**. Play includes Find the Ghosts, Pumpkin Painter, and Candy Quest. Story includes three original branching tales. Surprise chooses a game, story, or immersive scene. Only the small Back overlay exits the adventure; completed stories/games also offer Done. Reduced-motion mode skips the touch intro and opens the menu directly. Camera/test welcomes retain their monster reveal and configured follow-up. Rewards are virtual and do not change the physical candy inventory.

Open **Haunted House → Camera** or Settings to configure the optional Pi motion trigger. **Arm welcome** enables short motion scans; **Disarm** stops capture. **Test welcome** runs the same monster reveal without opening the camera. Choose what follows the reveal: visitor choice, Play, Story, or Surprise. Existing manual scenes are not interrupted. Camera arming and active adventures never resume after restart.

The camera is completely hidden: no video elements, previews, mirror, JPEG export, recordings, or image archives. Frames exist only briefly inside the capture worker for motion analysis; only numerical motion scores reach the server. The retired frame endpoint returns 410. Capture rotates 90° clockwise before analysis. Motion can include pets or lighting changes; it does not identify people or measure distance.

Defaults are **180 seconds scanning, then 45 seconds resting**, configurable to 6–600 and 20–300 seconds respectively. Every scan physically stops/closes the camera and ends its worker before resting, including scans with no motion. A confirmed trigger ends capture early. Visitors may be missed during rest; pumpkin touch remains available. Worker time limits and parent-process checks prevent unattended continuous capture.

A conservative app policy pauses scans at **70°C Pi board temperature** and resumes at **65°C**. This is not a camera sensor reading or manufacturer-prescribed camera cooldown. The [Picamera2 manual](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf) documents stop/close lifecycle operations; it does not prescribe an IMX219 scan/rest interval. [Raspberry Pi thermal documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#frequency-management-and-thermal-control) describes the board's separate thermal throttling. Keep normal ventilation and board cooling appropriate to the enclosure.

Pi capture uses a separate **system Python** process with Picamera2/libcamera and NumPy, keeping portable dependencies unchanged. Install missing camera packages through the OS package manager. `HALLOWEEN_CAMERA_PYTHON` overrides `/usr/bin/python3`. Windows and ordinary Linux retain all touch adventures; CSI motion capture is Pi-specific.

Visitor UI checks: `.venv/bin/python scripts/check_visitor.py`. Pi-only physical scan/rest checks use `scripts/check_hidden_camera.py` against a separate test server on port 8092, never the main kiosk data.

## Halloween music and offline shuffle

Party Hub → Library → **Find Halloween music on Pixabay** opens the official Halloween search in a separate tab. Download MP3s there, then use **Import local music** to upload them to this app. A remote browser's uploads are stored on the Pi when connected to the Pi server. They remain available after restart and without Internet. Tap Play music to enable audio; Shuffle saved songs is enabled by default and persisted, with no immediate repeats when more than one song exists. Next and track completion choose another random saved song; disabling Shuffle restores sequential playback. No playlist playback starts automatically after a restart.

Pixabay's [public API](https://pixabay.com/api/docs/) documents images/videos, not music. Its [terms](https://pixabay.com/service/terms/) prohibit unauthorized automatic collection and systematic copying. This app therefore does not scrape the search page or perform background Pixabay downloads. Direct download attempts in this environment returned HTTP 403; user-supplied downloaded MP3s can be imported without contacting Pixabay. Keep downloaded tracks for the app's soundtrack and retain their source/license information; external songs are not included in the portable source package.

## Imported scene sound effects

Party Hub → Library includes separate music and **Random scene sound effects** lists. MP3/WAV/OGG imports are copied into the server's application-data folder and persist offline. Duplicate content in the same library is reused rather than inserted twice. Music and effects remain separate even if they contain the same audio.

Each scene chooses a random saved effect, avoiding the previous effect when alternatives exist, over its bundled soundtrack. A short clip can be followed by another after a random 1–4-second gap. Longer clips are cut off at scene completion. Back, Stop, and Mute cancel both playback and queued effects. The scene sound slider and shared volume apply; audio remains muted until an explicit gesture. Library Listen buttons preview effects when no scene is active.

For batch imports from your own folders into a running server:

```sh
python3 scripts/import_audio.py --url http://127.0.0.1:8080 --music /path/to/music --effects /path/to/soundeffects
```

On the test Pi the music and effects are stored under `/home/spark/HalloweenHub-20261014/data/music` and `data/effects`; names and playlist entries live in SQLite. Original source files remain in place. User-supplied external audio is not redistributed in the portable source package.

## Immersive welcome screen

The main screen is a single haunted-house backdrop with a large tappable pumpkin, an emerging/fading Halloween countdown, floating weather, and a bottom ambience control. Dashboard cards and candy controls have been removed; existing stored data is preserved. The four screens and Settings remain in the navigation.

Locally drawn fog drifts at randomized speeds, lighting slowly breathes, embers rise, and ghosts cross at random intervals, directions, sizes and heights. The Pi uses reduced particle density and cached glow/ghost sprites. The welcome canvas and countdown pause off-screen or behind any dialog. Reduced motion keeps the scene static and the countdown visible. Weather remains live with explicit loading/stale/offline status and a location button; ambience still requires an explicit tap.

### Spooky Sounds uses your imported effects

The welcome screen's **Play spooky sounds** control plays the saved effect library, not the bundled midnight loop. Every effect plays once in a shuffled cycle before the next cycle begins; the boundary avoids an immediate repeat when alternatives exist. Each clip finishes before the next starts, including longer recordings. Pause and header Mute stop playback immediately; startup remains muted. With an empty effects library, the control opens Library with import guidance. Scene effects and Party Hub music remain separate.

## Pumpkin welcome cutscene

The supplied 15-second clip replaces the spinning reveal for manual pumpkin/Trick or Treat activation. It plays full-screen with one small Back overlay, then fades into the adventure menu. The menu always appears after a manual intro, regardless of the automatic camera follow-up setting. Back/Escape stops and releases the video. Background music and Spooky Sounds pause during the intro, then resume if still enabled. Video audio follows shared volume and Mute; browser audio restrictions fall back to muted video. Reduced motion skips the clip. A missing/unplayable intro opens the menu instead.

Videos are stored privately in app data as `cutscenes/welcome.mp4` and optional `welcome.webm`, and are excluded from the source archive. The original `/home/hsindhar/Music/cutscenes/generated_video.mp4` was preserved. The installed MP4 is stream-copied with fast-start metadata; a smaller 800-pixel VP8/Opus WebM supports browsers without H.264 decoding. No ffmpeg installation is needed at playback time.

To install already browser-compatible files:

```sh
python3 scripts/import_cutscene.py /path/to/welcome.mp4 --webm /path/to/welcome.webm --data-dir /path/to/app-data
```

Omit `--webm` if unavailable. On the Pi, app data is `/home/spark/HalloweenHub-20261014/data`. The importer copies files atomically and leaves sources untouched. Without an installed clip, manual activation opens the adventure menu directly.

## Background and cutscene rotation

When the Dashboard has had no touch, mouse movement, keypress or scrolling for **20 seconds**, its current settled background can briefly come alive. Wicked Nun plays **Nun**, Dracula plays **Dracula**, and the original pumpkin scene plays **Pumpkin Scare**. Replays are silent and leave the countdown, weather, caption and controls in front. A decoded video frame fades in smoothly. For the six-second clips, fades last about 1.2 seconds and the return to the image begins about 1.6 seconds before the end, leaving the middle of the clip clearly visible. Longer clips use fades up to two seconds. The decorative foreground pumpkin artwork fades away during replay so it does not cover the moving character; its touch target and caption remain available, and the artwork returns with the still. The matching image remains mounted and background rotation holds throughout, then resumes from the same point. There is a random **45–75 second** wait before another replay becomes eligible, and interaction must again have been quiet for 20 seconds.

Touch, mouse movement, a keypress or scrolling fades the replay away in 0.6 seconds without intercepting the action. Opening a dialog, leaving the Dashboard, hiding the page or enabling reduced motion releases playback immediately. Missing, blocked or stalled media keeps the image visible and skips the replay. Only one background video is decoded at a time and its resources are released after the fade. Imported images without an explicit video pairing continue as stills. Manual pumpkin adventures keep their existing behavior and audio.

The welcome background keeps the original haunted-house scene and rotates through imported PNG images: 20 seconds still, then a 3-second crossfade. Rotation pauses off-screen, behind dialogs, and in reduced-motion mode. New images preload before entering rotation; unavailable images are skipped. The foreground pumpkin lowers by 30% of its own height as an imported PNG fades in and returns as the original scene reappears; its touch target and caption stay anchored.

Pumpkin taps cycle the installed cutscenes in order, returning to the adventure menu after each. The last selection is remembered in that browser, so reloading does not reset the cycle. The Pi currently has **Welcome**, **Dracula**, **Nun**, and **Pumpkin Scare**, plus two full-size imported PNG backgrounds (Dracula and Wicked Nun) alongside the original scene. The former WebP backgrounds have been removed.

Import additional media without replacing Welcome:

```sh
python3 scripts/import_cutscene.py /path/to/new.mp4 --webm /path/to/new.webm --name new-scene --data-dir /path/to/app-data
python3 scripts/import_backgrounds.py /path/to/background-folder --data-dir /path/to/app-data
```

Use lowercase letters, digits, hyphens or underscores for cutscene names. Background imports deduplicate by content. Original files are preserved; imported media stays in application data and works offline.

On the welcome screen, the scene fills the display. Tap outside the pumpkin to reveal compact top and bottom controls for seven seconds. Tab or Escape reveals them for keyboard use. Other screens retain their visible navigation.

Welcome text lines drift independently along randomized 28–50 second routes, with separate fade schedules and mist/rise/slide/fade re-entry effects. Eight spooky headings change every 12 seconds. Messages and effects use independent shuffled bags without adjacent repeats. Effects include wavy letters, fading mist, a passing ghost, rotating title words with shimmer, typewriter reveals, and subdued city-night neon. Pumpkin instructions and the sound-library caption fade away between appearances. Messages pause behind dialogs/off-screen; reduced-motion mode keeps text steady and readable.

Welcome text effects are original adaptations inspired by [Prismic’s text-animation examples](https://prismic.io/blog/css-text-animations), including Ghosts and Ghouls, Schitt’s Creek title animation, Typewriter Effect and City Nights. No external scripts or media are loaded for these effects.

The welcome overlay containers stay anchored; individual headings, countdown values, weather lines, sound lines and pumpkin instructions move separately. Some remain visible while others fade. Playback/location buttons remain visible, and keyboard focus steadies the focused line. Dialogs, hidden screens and reduced motion pause the shared animation clock.

Imported backgrounds display at full opacity without the additional dark gradient, with lighter edge shading and reduced generated fog. The original scene keeps its existing rendering. Background PNGs are imported directly at their original resolution.

Idle-video browser checks (use an isolated server with the three paired clips and two PNGs installed):

```bash
.venv/bin/python scripts/check_idle_video.py --url http://127.0.0.1:8094
.venv/bin/python scripts/check_idle_video_natural.py --url http://127.0.0.1:8094
```

The first check backdates inactivity in an isolated browser fixture but plays the real clips and fades in real time. The second checks the natural idle schedule in the full Dashboard, then backdates inactivity for interruption checks. Both support `--cdp` for a Raspberry Pi Chromium instance and `--output` for evidence.

For native display verification, temporarily enable Chromium's loopback remote-debugging port, forward it over SSH, then run `.venv/bin/python scripts/check_idle_video_native.py --cdp http://127.0.0.1:19223`. This checks the existing kiosk tab and its real idle schedule, advancing decoded frames, decorative-art fade and return to the still. Normal kiosk startup does not expose a debugging port.
