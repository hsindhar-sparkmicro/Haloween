# Validation record — October 14, 2026

## Completed checks

- Linux amd64, Python 3.12: 12 backend tests passed (persistence and restart, concurrent candy edits, party editing, scan/haunt stop, settings/origin validation, audio rejection and byte-range playback, offline weather cache, timezone/countdown boundaries).
- Raspberry Pi 4 ARM64, Debian 13, Python 3.13: the same 12 backend tests passed. Runtime installed from compatible offline wheels in an isolated environment.
- Chromium browser automation: all four screens at 800×480, 1280×720 and 1920×1080; no JavaScript errors, clipped controls or main-screen controls below 48×48 pixels in the final layout pass.
- Browser interactions: candy updates, haunt activate/stop, scan start/stop, task creation/check/delete, local WAV import/play/delete, saved temperature units.
- WAV, MP3 and OGG import/decoding/playback passed in both Linux Chromium and the native Pi kiosk browser; see [audio-formats.json](validation/audio-formats.json) and [pi-audio-formats.json](validation/pi-audio-formats.json).
- Start-muted, reconnect after failed polling, reduced-motion mode, live Toronto city lookup and fresh Open-Meteo weather passed on the Linux host.
- Artwork, fonts and ambience are local. User data and virtual environments are excluded from portable archives.
- Extracted-source archive: checksum manifest verified; isolated dependency installation, Linux launcher, health endpoint, artwork delivery and all 12 backend tests passed on the final extracted source package.
- Native Pi Chromium also passed the same 12 layout/browser interaction scenarios through CDP. Deployed Python, JavaScript, HTML, CSS and artwork hashes match the workspace.

Machine-readable evidence: [browser-report.json](validation/browser-report.json), [resilience-report.json](validation/resilience-report.json), [pi-final-browser/browser-report.json](validation/pi-final-browser/browser-report.json), [package-check.json](validation/package-check.json), and [screenshots](validation/screenshots/).

## Pi deployment and endurance

Deployment: `/home/spark/HalloweenHub-20261014`. Server port **8088**, bound to Pi loopback. Data: `/home/spark/HalloweenHub-20261014/data`. Server and browser PID files and logs reside inside the deployment directory. No boot service was installed. The journal reached its configured 500-row bound during the endurance run.

The physical display is Wayland DSI, 800×480 at approximately 60 Hz. Chromium uses a separate profile. The endurance test connects through SSH-forwarded loopback ports and exercises the actual kiosk page, rather than a headless substitute.

**Completed:** 3,606.73 seconds, 180 health/state samples, zero health failures and zero browser errors; all four screens observed. The initial 5-second RAF sample measured 60 FPS, and programmatic navigation feedback measured 11.9 ms. See [pi-soak-summary.json](validation/pi-soak-summary.json) and [pi-soak.jsonl](validation/pi-soak.jsonl).

The full-hour run preceded the final touch-area/error-feedback refinements and the requested selected/random playback and native minimize changes. The updated build passed backend/browser regressions and native Pi scene/minimize tests afterward; the updated build has not had a second full-hour soak. Audio was started and its native output route verified; this was not a continuous-audio endurance qualification.

Post-soak checks: all controls retain at least 48×48 pixels of effective touch area after ancestor clipping; invalid settings/audio errors appear inside the active dialog; failed checkbox edits roll back; Halloween and custom party countdowns remain independent. See [clipping-report.json](validation/clipping-report.json), [pi-clipping-report.json](validation/pi-clipping-report.json), [final-ui-report.json](validation/final-ui-report.json), and [pi-controls-report.json](validation/pi-controls-report.json).

Native minimize changed the kiosk’s Wayland state from activated/fullscreen to minimized/fullscreen, exposed the real desktop, and restored the same window. Selected scene audio and mid-sequence replacement/random selection passed. Those checks verified timed simulated controls and sound cues, **not animated scene playback**; their results are in [pi-scene-cycles.json](validation/pi-scene-cycles.json). The progress bar and tile effects did not constitute a scene player.

Reproduction, with the Pi server and diagnostic Chromium already running:

```bash
ssh -N -L 18088:127.0.0.1:8088 -L 19223:127.0.0.1:9223 spark@192.168.0.100
.venv/bin/python scripts/soak.py --minutes 60
```

Normal relaunch on the Pi:

```bash
cd /home/spark/HalloweenHub-20261014
HALLOWEEN_DATA_DIR="$PWD/data" ./run.sh --no-browser --port 8088
# In another terminal on the graphical desktop:
./kiosk.sh http://127.0.0.1:8088
```

Stop the deployed background server using `kill "$(cat server.pid)"` from its directory. Stop its kiosk using Alt+F4. Diagnostic remote-debugging ports are not enabled by the normal kiosk launcher.

## Explicit validation boundaries

- **Windows amd64 was unavailable:** its launcher and cross-platform runtime are provided, but native Windows installation/startup and window minimization have not been executed. X11 minimization was also unavailable for testing.
- **Pi internet is unavailable:** live weather could not be fetched from the Pi. Its loading/offline behavior was verified; live weather/search passed locally.
- **Pi clock is unsynchronized:** it reported September 12 while the client date is October 14. Countdown and timestamps on the Pi follow that host clock. Its clock/network settings were left unchanged.
- Browser playback and PipeWire routing can be inspected remotely; audible quality at the physical speaker and human touchscreen ergonomics require an observer at the Pi.
- RAF measurements describe browser frame cadence, not an instrumented GPU frame-time guarantee. Automated navigation uses the browser's pointer/DOM path; it does not measure the touchscreen controller's physical latency.
- GPIO, microphone and real EMF/temperature sensing are absent. Optional Pi camera motion detection was added in the subsequently authorized immersive-camera update below.

## Animated scene player correction

Added a large canvas player that opens when selecting, activating or randomizing a scene. Quiet Shadows renders moving shadows, bats and leaves; Purple Mist renders floating ghosts and drifting fog; Pumpkin Parade renders marching, bouncing lanterns and celebration particles. Stop cancels local animation/audio immediately and stops the backend sequence. Back/Escape hides the player and suspends its rendering; View scene reopens it. Reduced motion uses still phase compositions.

Canvas pixel signatures, sampled independently of the progress bar, verify visual motion for every scene. Controls were checked at 800×480, 1280×720 and 1920×1080; all player controls retain at least 48×48 pixels. See [Linux visual checks](validation/scene-visuals/report.json), [native Pi visual checks](validation/pi-scene-visuals/report.json), and [updated layout checks](validation/scene-update-browser/browser-report.json). The Pi check uses its native Chromium engine with a separate 800×480 browser context and temporary backend/data directory, avoiding interference with live kiosk selections. It runs each full 20-second cycle and checks all four phase labels, sound playback, changing canvas pixels, Stop freezing the scene, Random, Back/Escape and reduced motion. This update has not received another full-hour soak.

The separate 5-second Pi draw-count samples, without canvas pixel readbacks, measured **25.4–26.7 FPS** across the three scenes; see [pi-scene-fps.json](validation/pi-scene-fps.json). The 30 FPS rendering target is not yet met on this Pi. These samples measure canvas draw cadence, rather than physical touchscreen latency or audio quality.

## Immersive scenes and optional camera update

The previous player was replaced with **edge-to-edge playback and only a 48-pixel-or-larger Back overlay**. Back/Escape stops the scene; completion returns automatically to the haunt panel. Eight distinct locally generated backgrounds, scene-specific characters/audio, and per-playback seeded cloud births, wind, speed, opacity and lifetimes replace the shared-house background and repeating fog formations.

- **18 backend tests passed** on Linux Python 3.12 and Pi ARM64 Python 3.13: settings, restart-disarmed state, motion confirmation, quiet rearming, cooldown, disarm cancellation, manual-scene precedence, welcome transitions, scene seeds and prior core regressions.
- All eight scenes passed visual motion and immersive geometry checks locally; all eight passed complete four-phase natural cycles and automatic return on Pi Chromium using an isolated backend/browser context. Back/Escape, random seed variation, reduced motion and all three resolutions passed. See [local report](validation/immersive-scenes/report.json), [Pi report](validation/pi-immersive-scenes/report.json), [layout report](validation/immersive-browser/browser-report.json), and [touch clipping](validation/immersive-clipping.json).
- Pi IMX219 capture produced real 320×240 grayscale JPEG frames. Preview, left/center detection regions, delayed mirror, arming, disarming, camera-off frame clearing and worker release passed without saving camera images. See [camera report](validation/pi-camera.json). Real visitor walk-through triggering and low-light detection reliability remain **unverified**; deterministic motion samples cover the confirmation/cooldown logic.
- The labelled **Test welcome** control passed the complete browser path from fictional ghost scan to random immersive scene and Back cancellation, without starting capture, locally and on the Pi. See [local welcome](validation/welcome.json) and [Pi welcome](validation/pi-welcome.json).
- Cached static backgrounds improved short Pi canvas draw samples to **28.0–30.8 FPS**, without pixel readbacks; see [draw samples](validation/pi-immersive-fps.json). These are 5-second samples near the start of each scene, not complete-phase, camera-concurrent, GPU presentation or endurance measurements.
- The actual 800×480 kiosk was refreshed to the deployed update; a full vampire cycle and return, eight scene choices, camera-off startup and native minimize availability were checked. See [native kiosk](validation/pi-native-immersive.json) and [scene screenshot](validation/pi-immersive-native.png).

Camera frames stay in RAM (a bounded four-JPEG mirror buffer). Pi capture uses the existing system Picamera2/NumPy/Pillow through a separate process, keeping portable backend dependencies unchanged. Camera errors do not prevent core screens from operating. No boot, clock or networking configuration was changed. The updated camera build has not undergone a new 60-minute soak; Windows remains untested.

### Camera orientation correction

Capture now rotates 90° clockwise **before** motion analysis and JPEG encoding, yielding 240×320 portrait frames for preview and the delayed mirror. Detection rectangles use the corrected frame dimensions and match the portrait calibration overlay; mirror fitting preserves the full frame. Live Pi capture dimensions and clockwise direction with an asymmetric synthetic input were verified. The camera's previous off/disarmed state was restored after testing. See [rotation check](validation/pi-camera-rotation.json).

## Hidden camera and visitor adventures (supersedes preview/mirror behavior above)

- All **20 backend tests** passed locally and on the Pi: physical capture shutdown, cooldown after every scan, board-temperature hysteresis, encounter lease ownership, duplicate suppression, settings, and unavailable image export are covered.
- The real Pi IMX219 completed two 8-second scans separated by a configured 20-second test rest. No camera worker remained during rest; no camera imagery was saved. Production default remains 45 seconds resting. See [physical duty-cycle report](validation/pi-hidden-camera.json). Physical visitor walk-through and low-light reliability remain unqualified.
- On local Chromium and Pi Chromium, all three games and all three story paths completed at **800×480, 1280×720, and 1920×1080**, with reachable minimum 48-pixel touch controls and no JavaScript errors. Keyboard activation, reduced motion, Surprise-to-scene, and denied camera preview/image requests passed. See [Pi visitor report](validation/pi-visitor/report.json).
- Core four-screen browser regression checks passed without layout overflow or JavaScript errors. See `validation/visitor-core-browser/`.
- The actual 800×480 Pi kiosk was refreshed and verified for pumpkin spin, game completion, test welcome/story opening, and hidden camera controls. See [native report](validation/pi-native-visitor.json) and [native adventure screenshot](validation/pi-native-visitor.png). Camera was left off; Montreal location and existing application data were preserved. No boot configuration was changed.
- The 70°C pause / 65°C resume guard is an application policy using **Pi board/SoC** temperature, not a camera sensor temperature or manufacturer-specified camera cooldown. Rest periods can miss arriving visitors; touch activation remains available.
- New artwork, original stories and games work offline. No new Windows installation test or 60-minute soak was performed for this update.

### Longer motion scan default

The default and the main Pi's saved configuration are now **180 seconds scanning / 45 seconds resting**, with configurable scan windows of 6–600 seconds. The worker's independent time limit matches that range. All 20 backend tests passed, including long-duration settings and supervisor deadlines; native Pi settings were verified. A complete 180-second capture/rest cycle was not measured in this change. The earlier physical lifecycle checks used 8-second scans. Hidden capture, early termination on motion, and the board-temperature guard remain active. See [Pi settings evidence](validation/pi-long-scan.json).

### Offline Halloween playlist shuffle

- Local isolated-browser checks imported three bundled WAV fixtures, verified shuffled Next and automatic track completion without immediate repeats, verified sequential mode and saved preference after reload, and confirmed playback does not resume on reload. All three screen sizes retain a 48-pixel source link. See [playlist report](validation/playlist.json).
- All 20 backend tests passed. The actual Pi 800×480 library was refreshed and verified with the official Pixabay link and Shuffle enabled; existing application data and 180/45-second camera timing were preserved. See [Pi library](validation/pi-playlist.json) and [screenshot](validation/pi-playlist.png).
- **No Pixabay music was downloaded or added.** Direct access returned HTTP 403, no enabled browser was available for manual download, and the public API documents no music endpoint. The delivered workflow is official-site download followed by local import; there is no automated search-page scraper or background song fetcher. Tests used original bundled audio solely in an isolated database, not the user's playlist. Windows installation and new endurance testing remain untested.

### User-provided music and random scene effects

- Imported **6 music MP3s and 10 effect MP3s** from the supplied local folders to the main Pi. Sources were copied, not moved. All 16 served-file SHA-256 hashes and byte counts match the originals; a second import reused all 16 existing entries without duplicates. See [Pi import report](validation/pi-audio-import.json) and [checksums](validation/pi-audio-checksums.json).
- All **21 backend tests** passed locally and on Pi, including effect/music separation, repeated imports, rejected audio, file serving/removal and persisted library rows.
- Local and Pi Chromium decoded/played all 16 MP3s. Four randomly selected scene starts, follow-up cues, immediate Back cancellation, Mute cancellation and muted reload passed without JavaScript errors. See [Pi scene audio report](validation/pi-scene-audio.json).
- The actual 800×480 kiosk played Party Hub music, switched to another track, played a random imported scene effect, and stopped it with Back. Both libraries show 6/10 entries. It was left muted on Dashboard, with the hidden camera off. See [native audio check](validation/pi-native-local-audio.json) and [music screenshot](validation/pi-native-music.png).
- Shared four-screen browser checks passed at the three target resolutions without layout overflow or JavaScript errors; see `validation/scene-audio-core-browser/`. Physical speaker output was not independently measured; browser decoding and playback were verified. No new soak or Windows installation test was performed.
- External user audio is stored in Pi application data and **excluded from the portable source archive**. Earlier no-download statements describe the blocked automated-download attempt; this update uses the explicitly supplied local files.

### Immersive welcome screen

- Replaced the Dashboard cards with one haunted background: emerging/fading Halloween countdown, large tappable pumpkin, floating live weather and bottom ambience text/control. Candy controls are absent; existing stored data remains intact.
- At 800×480, 1280×720 and 1920×1080, local and Pi Chromium verified no cards/candy UI, readable essential controls, minimum 48-pixel touch areas and no overflow. Weather Settings, ambience playback, keyboard pumpkin activation, reduced motion, hidden-screen pause and dialog pause passed without JavaScript errors. See [Pi welcome report](validation/pi-immersive-welcome/report.json).
- Short Pi canvas draw samples were approximately 30 FPS at 800×480 and 29.5 FPS at 1280×720; full-HD high-detail sampling was 22.4 FPS. These measure canvas draw calls over 2.1 seconds, not GPU presentation or endurance. The Pi's primary 800×480 view uses nine cached fog sprites, fewer particles and at most two ghosts; quality can also be set to Low for larger screens.
- Shared four-screen browser regression checks passed without overflow/JavaScript errors; see `validation/welcome-core-browser/`. All 21 backend tests passed; backend behavior is unchanged.
- The native 800×480 kiosk was refreshed. Weather Settings, ambience and the pumpkin adventure passed; its 6-track music library, 10 effects, Montreal location and hidden-camera-off state were preserved. See [native welcome check](validation/pi-native-welcome.json) and [screenshot](validation/pi-native-immersive-welcome.png).
- Fog speeds/phases and ghost interval/direction/height/size are randomized locally. Motion stops off-screen and in reduced-motion mode. No new 60-minute soak or Windows installation test was performed.

### Welcome Spooky Sounds shuffle

The main sound control now uses the imported effects library, not the bundled midnight WAV loop. A shuffled bag plays every saved effect once per cycle and prevents adjacent duplicates across cycles when alternatives exist. One media element plays clips sequentially, advancing only on completion; Pause/Mute invalidate pending playback, and reload starts muted. An empty library opens import guidance without a default fallback.

Local and Pi Chromium verified two complete **selection** cycles covering all ten effects, no adjacent duplicates, Pause, Mute, rapid play/pause cancellation and muted reload. Cycle coverage uses synthetic ended events; one real seek-to-end completion also verifies browser auto-advance. These are not two full-duration listening cycles. See [Pi shuffle report](validation/pi-spooky-shuffle.json).

The native 800×480 kiosk played imported effects, advanced on completion and paused successfully, preserving all ten effects and six music tracks. It was left muted. See [native shuffle check](validation/pi-native-spooky-shuffle.json). Welcome layout/lifecycle checks passed again at all three resolutions. Backend behavior is unchanged; no new soak or Windows installation test was performed.

### Pumpkin welcome cutscene — October 15, 2026

- Installed the supplied `generated_video.mp4` as the welcome intro in Pi application data. The original remains unchanged. The MP4 was stream-copied with fast-start layout; an 800-pixel VP8/Opus WebM fallback supports the local Chromium build without H.264 decoding. See [asset inventory](validation/cutscene-assets.json). Both media files are also available in the separate private `dist/HalloweenHub-cutscene-media.zip`; they are excluded from the source archive.
- Touch/keyboard pumpkin activation plays the intro with only Back, then opens the adventure menu. Camera/test welcomes retain their existing reveal/preferences. Reduced motion skips the intro. Missing/failed assets return to the menu with an explanation; a HEAD availability check and watchdog avoid a stuck player.
- Local Chromium (WebM) and Pi Chromium (MP4) each played the complete 15-second clip at 800×480, 1280×720 and 1920×1080, then reached the menu. Back released the media, missing-file recovery worked, simulated browser audio restrictions fell back to muted playback across state polls, and reduced motion opened the menu directly. See [local report](validation/cutscene/report.json) and [Pi report](validation/pi-cutscene/report.json). These runs used natural video completion, not seeking or synthetic ended events.
- The actual 800×480 kiosk played all 15.041667 seconds: 361 total frames, 1 dropped. Background Spooky Sounds paused and resumed; story selection, Back resource release and immediate global video mute passed. Six music tracks, ten effects, Montreal and camera-off state were preserved. It was left muted on Dashboard. See [native report](validation/pi-native-cutscene.json), [video screenshot](validation/pi-native-cutscene.png) and [menu](validation/pi-native-cutscene-menu.png).
- All **22 backend tests** passed locally and on Pi, including optional video availability and byte-range serving. The unchanged camera/test welcome-to-story path also passed locally. No Windows installation test or new 60-minute soak was performed.

### Added background and cutscene rotation

- Added the supplied WebP alongside the existing haunted-house background; 20 seconds still / 3 seconds crossfade. Real-time original→WebP→original cycles, dialog pause and reduced-motion freeze passed locally and on Pi. Screenshots at 800×480, 1280×720 and 1920×1080 are in [Pi background evidence](validation/pi-background-rotation/report.json).
- Retained Welcome and added **Nun** and **Pumpkin Scare**, each with MP4 and WebM fallback. Full natural playback rotated across all three at the three target viewports, followed by the menu. Back, missing-file recovery, muted autoplay fallback and reduced motion passed locally and on Pi. See [Pi cutscene rotation](validation/pi-gallery-cutscenes/report.json).
- All **23 backend tests** passed locally and on Pi, including gallery discovery, preservation of Welcome, whitelisted media serving and byte ranges. The original supplied media files were copied rather than modified. User audio/video/background files remain in app data and are excluded from the source archive; the private media archive includes the new items.
- The actual native kiosk verified all three selections, menu transitions (seeked near the end for this short native check) and the new fully faded-in background. Existing six-track music and ten-effect libraries were preserved, and it was left muted with the camera off. See [native gallery check](validation/pi-native-gallery.json) and [screenshot](validation/pi-native-gallery.png).
- The supplied WebP is 256×256 and is used as an atmospheric backdrop. No new Windows installation test or 60-minute soak was performed.

### Pumpkin placement with imported WebP backgrounds

The foreground pumpkin moves down by half its rendered height during the same three-second background crossfade, and returns when the original background reappears. The caption and touch target remain anchored. Pi Chromium measured the art and SVG face displacement at 800×480, 1280×720 and 1920×1080, checked the visible pumpkin's hit target, and verified a natural return cycle with no JavaScript errors. See [position measurements](validation/pi-pumpkin-drop/report.json). This is a frontend layout change; no new backend, Windows or soak qualification was performed.

### Touch-revealed welcome controls

The welcome scene now occupies the full viewport. Background taps reveal compact 56-pixel header/navigation overlays for seven seconds, with 48-pixel minimum touch targets. Pumpkin taps retain their adventure action without revealing the bars. Tab/Escape reveals keyboard-accessible controls; keyboard focus keeps them available. Other screens retain visible navigation. Pi Chromium checks passed at 800×480, 1280×720 and 1920×1080, including timed hiding, screen transitions and pumpkin activation without JavaScript errors. See [touch navigation evidence](validation/pi-welcome-chrome/report.json). Native kiosk reloaded. Backend and launchers are unchanged; no new Windows installation or soak test was performed.

### Floating welcome overlays and spooky messages

Welcome countdown, weather and sound overlays drift slowly by a few pixels. Six headings cycle every 12 seconds through fades; pumpkin instructions and the sound-library caption periodically disappear. Mouse hover/keyboard focus steadies interactive overlays. Animation uses the existing visible-screen clock, so headings pause behind dialogs/off-screen; reduced-motion mode displays steady, fully visible text. Pi Chromium checks cover a natural first heading transition, measured weather movement, fading instructions, dialog pause, reduced motion and all six message layouts at 800×480, 1280×720 and 1920×1080. See [welcome message evidence](validation/pi-welcome-messages/report.json). No backend, Windows installation or new soak qualification was performed.

### Randomized reference-inspired welcome text effects

Added six local effects: passing ghost with exclusion blending, wavy letters, mist fade, staggered rotating title words with shimmer, typewriter reveal/caret, and subdued city-night neon. Eight messages and the six effects use independent Fisher-Yates shuffle bags, covering each bag before repeating and preventing adjacent repeats across bag boundaries. All effects use the existing paused welcome clock; reduced motion renders complete, steady text. Heading labels expose the complete message to assistive technology during partial reveals.

Pi Chromium exercised all 48 message/effect combinations at each of 800×480, 1280×720 and 1920×1080; readable hold, typewriter partial reveal, accessible labels, reduced motion and multiple complete shuffle bags passed. Screenshots capture each effect at all three resolutions. See [effect matrix](validation/pi-welcome-effects/report.json). These are original adaptations inspired by the linked Prismic examples, with no runtime external assets. Backend, Windows installation and soak qualification were not repeated.

The natural heading-transition, drifting weather, disappearing instruction, dialog pause and reduced-motion checks also passed again on Pi with the randomized renderer and all eight messages; see [updated live welcome check](validation/pi-welcome-messages/report.json). The native kiosk was reloaded after validation.

### Clearly visible floating weather, sound details and countdown

Live Pi inspection showed that the previous 5–8-pixel drift over 17–21 seconds was running but too subtle, and `:focus-within` could keep a touched weather/sound group paused. Increased the independent group paths to 18–32 pixels vertically over 10–12 seconds, added staggered 5-pixel waves to countdown digits and detail lines, and limited focus-based pausing to visible keyboard focus. Pointer hover can still steady a control for use; touch no longer leaves the group paused.

Measured every weather value/detail/location/status, sound title/description/control and countdown digits over eight seconds on Pi Chromium: each traveled more than eight pixels, remained within the 800×480 viewport, and weather resumed after opening/closing Settings by touch. Dialog pause and reduced motion passed; screenshots cover all three target sizes. See [actual text movement measurements](validation/pi-overlay-float/report.json). Native kiosk reloaded. Backend/launcher, Windows installation and soak tests were not repeated.

### Independent slow line motion and asynchronous fade schedules

Replaced shared group paths and repeating CSS waves with a local per-line controller. Nineteen lines/elements have independent random waypoints, 28–50 second travel times, starting offsets and fade schedules. Some keep drifting while others fade out and return with independently selected fade, haze, rise or slide transitions, avoiding immediate transition repeats for that line. Play/location controls remain visible; keyboard focus steadies its line. Tight rows have smaller travel bounds to preserve spacing.

Pi Chromium verified natural line movement and dialog pause, then exercised 240 seconds of lifecycle using an accelerated animation clock: distinct line positions, mixed visible/hidden lines, all four re-entry types, visible controls, and reduced motion passed. This accelerated check is not a four-minute wall-clock soak. Screen-bound checks and screenshots passed at all three target viewports. See [independent motion evidence](validation/pi-independent-float/report.json). Native kiosk reloaded; no backend, Windows installation or soak qualification was repeated.

### Added Dracula backgrounds and cutscene

Imported `dracula_bg.webp`, `dracula_bg1.webp`, and a wide WebP copy of `videoframe_2893.png`; retained the existing Nun WebP and original bundled backdrop. The gallery now contains five backgrounds including the original. Added `dracula_scene.mp4` as **Dracula** alongside Welcome, Nun and Pumpkin Scare. Prepared a fast-start MP4 without its attached cover-image stream plus an 800-pixel VP8/Opus WebM fallback. Original source hashes were preserved, including the prior gallery files; see [source inventory and local fallback](validation/dracula-assets.json).

Pi Chromium played Dracula naturally to the adventure menu at all three target sizes, with only Back visible during playback. Byte-range serving passed for both video formats. The local Chromium build naturally played the WebM fallback. A full real-time five-background cycle was checked on Pi; see [expanded gallery evidence](validation/pi-dracula-gallery/report.json). Existing music and effects were preserved. User media remains outside the source archive; the private `dist/HalloweenHub-cutscene-media.zip` was rebuilt with all four video pairs and four imported backgrounds, with CRC and manifest checks.

The actual native 800×480 kiosk also played Dracula through to its menu. It was left muted on the main screen, with Dracula selected for the next pumpkin tap and the camera still off. See [native check](validation/pi-dracula-native.json). No Windows installation or new soak test was performed.

### Imported background clarity correction

Imported images previously combined 84% opacity, an additional dark gradient, a heavy vignette and generated fog. Imported images now display at 100% opacity without the dark gradient; vignette opacity interpolates to 35% and generated fog strength to 55% for imported artwork. The original scene retains its opacity, gradient, vignette and fog treatment. Crossfade timing and pumpkin displacement are retained.

Captured every imported image before/after at 800×480 on Pi Chromium, with the wide background also checked at 1280×720 and 1920×1080. End states, midpoint pumpkin displacement and return to the original treatment passed, with no JavaScript errors. A background-only sample region is brighter for every imported image; see [comparison](validation/pi-background-clarity/comparison.json), [rendered states](validation/pi-background-clarity/after/report.json) and [transition checks](validation/pi-background-clarity/after/transition.json). These previews used fixed animation phases for comparison. The native kiosk was reloaded. Original images remain unchanged; the 256×256 images retain their source-resolution limits. No backend, Windows installation or new soak qualification was performed.

### PNG-only background gallery

Replaced the imported WebP gallery with the user's original `dracula_stand.png` (1232×736) and `wicked_nun.png` (1280×720). PNG files are copied atomically without resizing, recompression or conversion; original hashes are preserved. Discovery and the serving whitelist now accept PNG backgrounds only, with `image/png` responses. Removed all installed WebP backgrounds and staging copies from the Pi and excluded them from the rebuilt private media archive. WebM video fallbacks remain intact because they are video files, not WebP images.

All **23 backend tests** passed locally and on Pi, including PNG catalog/serving and rejection of an installed WebP file. Browser checks verified both full-resolution PNG decodes, response MIME/content hashes, an old WebP URL returning 404, a natural original→Wicked Nun→Dracula→original cycle, and screenshots at all three target sizes. See [PNG gallery evidence](validation/pi-png-backgrounds/report.json) and [original file inventory](validation/png-background-assets.json). Existing four cutscenes, six music tracks and ten effects remain present, and the camera remains off. Native kiosk reloaded; no Windows installation or new soak test was performed.

### Raise pumpkin on imported backgrounds

Raised the foreground pumpkin by 20% of its own rendered height from its previous imported-background position: the conditional offset is now 30% below default instead of 50%. The original/default background position is unchanged. Pi Chromium measured the artwork and face at all three target sizes, checked the halfway crossfade position and default return, and confirmed the touch target stays anchored. See [position evidence](validation/pi-pumpkin-raised/report.json). This is a frontend positioning change; backend, Windows installation and soak tests were not repeated.


## Raspberry Pi boot autostart (2026-10-20)

Installed the per-user `halloween-hub.service` and XDG desktop autostart entry on the existing Pi deployment at `/home/spark/HalloweenHub-20261014`, using port 8088 and its existing `data/` directory. Desktop autologin was already enabled for `spark` in LightDM. The systemd unit and desktop entry passed `systemd-analyze --user verify` and `desktop-file-validate`; the service is enabled and active, listens only on `127.0.0.1:8088`, and returned HTTP 200. The readiness launcher opened the native Chromium kiosk in the existing Wayland desktop session. All 23 local backend tests passed. No reboot was performed, so the complete boot sequence remains unverified. Earlier statements about manual startup describe previous validation snapshots.


## Idle background video replay (2026-10-20)

Added explicit Nun → Nun, Dracula → Dracula and original pumpkin → Pumpkin Scare relationships. After 45 seconds without interaction, a settled background may play its matching silent clip behind the existing dashboard content. The still remains mounted, image rotation holds throughout playback, the first presented video frame gates a two-second fade-in, and the two-second fade-out begins about 3.2 seconds before the end. A random 90–150 second cooldown prevents frequent repeats. Touch/mouse/keyboard/scroll input fades playback away; dialogs, other screens, hidden pages and reduced motion release it immediately. Missing, blocked or stalled media leaves the still visible.

All **24 backend tests** passed locally and on the Pi, including hash-to-video pairing and unpaired-image behavior. Browser lifecycle checks exercised all three actual clips, decoder release, cooldown, touch interruption, disabled playback, missing/stalled media and foreground hit testing in local Chromium and Pi Chromium. Screenshots cover 800×480, 1280×720 and 1920×1080. The lifecycle fixture backdates inactivity while video decoding and fades run in real time. See [local lifecycle evidence](validation/idle-video/checks/report.json) and [Pi lifecycle evidence](validation/idle-video/pi-checks/report.json).

The full Dashboard's natural idle schedule and early fade-out were also checked locally and on Pi Chromium; interruption checks then backdated inactivity to exercise touch, dialog, screen-change, reduced-motion and hidden-page paths. See [local Dashboard checks](validation/idle-video/natural/report.json) and [Pi Dashboard checks](validation/idle-video/pi-natural/report.json). Pi browser automation used a separate headless Chromium process; the actual Wayland kiosk was restarted onto the update and its native 800×480 display captured separately in [native screen evidence](validation/idle-video/pi-native.png). The existing six music tracks, ten effects, four cutscenes, two PNGs, Montreal location and camera-off state were retained. The server remains loopback-only on port 8088 with its existing boot autostart. No Windows execution or new endurance soak was performed.


## Idle video visibility correction (2026-10-20)

The prior playback did start in the native kiosk, but the static foreground pumpkin covered its central action, and a fade beginning 3.2 seconds before the end hid much of each six-second clip. Native diagnostics confirmed playback and no input events resetting the timer during the observed run.

The decorative pumpkin art now fades away with video entry and returns with the still; the caption and adventure button remain available above the moving scene. Fades adapt to clip length (about 1.2 seconds for these clips), with fade-out beginning about 1.6 seconds before the end. Idle eligibility is now 20 seconds, followed by waiting for a settled image; cooldown is 45–75 seconds.

Verified directly in the existing **native Wayland kiosk tab**, using a temporary loopback CDP connection and its unmodified idle schedule. Nun reached full opacity with decorative artwork hidden, remained fully visible past three seconds of playback, advanced through 141 decoded frames, and released back to the still with the artwork restored. No pointer/keyboard/wheel events occurred in that run. See [native report](validation/idle-video/native-fix/report.json) and [native video screenshot](validation/idle-video/native-fix/native-playing.png). The reproducible check is `scripts/check_idle_video_native.py`. Local three-pair lifecycle/fallback checks and all 24 backend tests passed again. Normal kiosk startup is restored without the temporary debugging port.


## Half-speed idle video and longer fades (2026-10-20)

Idle background videos now play at **0.5× speed** with **3.5-second incoming and outgoing fades**. Six-second source clips run for approximately twelve seconds. The fade-out trigger converts remaining media time to wall time using the playback rate; it starts with about 3.9 wall-clock seconds remaining, preserving a small margin before the clip ends. The decorative pumpkin art follows the same fade duration. Input interruptions retain their quick response.

The native-kiosk check verifies the actual playback rate, both CSS transition durations, advancing decoded frames over more than ten wall-clock seconds, late fade-out, full video visibility and restoration of the still/foreground artwork. Evidence: [half-speed native report](validation/idle-video/half-speed-native/report.json). All three paired clips are also covered by the updated local lifecycle/fallback check: [local report](validation/idle-video/half-speed-local/report.json). No backend behavior changed.


## SPARK Halloween product showcase (2026-10-20)

Replaced the manual visitor Play / Story / Surprise menu with a locally bundled SPARK showcase. The existing pumpkin intro leads into four touchable exhibits (SR1120, mouse reference design, keyboard reference design and headset demo), each with a larger image, themed caption and two source-backed product highlights. The SPARK logo and product/application PNGs were fetched from the official website without modifying their bytes; direct image/page URLs and SHA-256 digests are in `halloween_hub/static/assets/spark/sources.json`. Halloween framing is rendered in HTML/CSS/SVG. Back/Escape exits; All products returns focus to the selected card.

All **24 backend tests** passed. The replacement visitor check passed at 800×480, 1280×720 and 1920×1080, checking all four details, full image decode, touch targets of at least 48×48 pixels, no scrolling at these sizes, keyboard entry/exit, reduced motion, failed-intro fallback, offline product images and Party Hub entry. No requests to sparkmicro.com were made by the UI. See [visitor report](validation/spark-showcase/checks/report.json). The updated cutscene regression check passed at all three sizes with natural clip completion, Back cancellation, unavailable-video recovery, muted autoplay fallback and reduced-motion bypass; see [cutscene report](validation/spark-showcase/cutscene/report.json).

The existing **native Wayland Pi kiosk** completed its intro naturally and displayed all four locally decoded product exhibits and detail views, then returned to the Dashboard with the encounter ended. Its six music tracks, ten effects and camera-off state remained intact. See [native Pi report](validation/spark-showcase/native/report.json), [native overview](validation/spark-showcase/native/overview.png) and [SR1120 detail](validation/spark-showcase/native/sr1120.png). The native check used a temporary loopback debugging port; normal kiosk startup is restored without it. Product specifications describe SPARK's reference designs/demo and are not live performance measurements from this application. Windows installation and a new endurance soak were not repeated.

The camera's **Test welcome** path also passed its updated check without opening capture, reached the headset exhibit and exited with scan, camera, welcome and haunt inactive: [camera test report](validation/spark-showcase/camera-welcome.json).
