# After the haunt — Christmas sneak peek

Created November 3, 2026 on the separate local `christmas-sneak-peek` branch, based on SPARK `main` at `7168675`. The complete Christmas design/references/Grok guide remain on `generic` at `4fd046f`. Neither base branch is merged or advanced by this preview.

## What works

- A snowy forest based on the supplied background, with elves preparing the tree, wrapped SPARK gifts, Santa-hat pumpkins and a playful Mariah Carey ice cameo. The fused still is `halloween_hub/static/assets/sneak-peek/forest-preparing.png`.
- Christmas countdown uses the configured timezone, with Christmas-day and post-Christmas copy. The original Halloween API countdown remains available, and custom party dates/records/imports are preserved.
- Three interactive SPARK gift packs reveal the chip, headset and gaming mouse with existing product artwork and links to SPARK.
- The full-version teaser opens local forest and SPARK Christmas House artwork. It describes the arrival film, workshop, party and simulated Santa Tracker as upcoming, not implemented features.
- Mariah's playful defrost meter advances from November 1 to December 1. This is a calendar joke, not live artist information.
- Quiet original bell motifs play only after **Enable festive jingles**. They respect global mute and volume. Repeats are spaced randomly 32–60 seconds apart, pause for dialogs/other screens/hidden tabs, and start disabled on reload.
- Decorative flurries start after a random 5–12-second opening calm. Later 18–42-second calm gaps alternate with a random choice favoring snow over autumn leaves. The canvas uses bounded particles and a 30 FPS ceiling; dialogs, hidden tabs and reduced motion suppress it. Forecast data is independent.
- The bottom row now holds the Christmas House preview, the wrapped-gifts button and a SPARK Christmas Party card: **Dîner de fin d’année**, Wednesday, December 9, 2026 at 5:00 PM Montréal time. Its days/hours/minutes/seconds countdown is independent of saved custom party dates. The Black Friday and Boxing Day cards have been removed.
- The supplied SPARK wordmark sits beneath the countdown, blending into the forest with a gentle seven-second float and glow. It stays visible but pauses during video playback, dialogs, hidden tabs and reduced motion. Its original transparent PNG is kept unchanged.
- Dashboard cards are transparent, including weather, Mariah’s defrost meter, jingles and the bottom row. Text shadows keep labels readable without panel fills, panel shadows or background blur covering the forest. Touch targets and keyboard focus outlines are retained.
- Four two-line headlines rotate every 12 active seconds with a gentle fade: Halloween fades / Christmas stirs; Santa’s on his way / With gifts for you; More festive magic / Stay for the reveal; The Christmas app / Arrives December 1. Rotation pauses for dialogs, hidden tabs, other screens and reduced motion.
- The existing Halloween adventures, haunted controls, party management and simulated detector remain available. The main branch's backend and kiosk controls are retained.

## Local preview

Use a separate data directory for a review session so production records are not modified:

```sh
HALLOWEEN_DATA_DIR=/tmp/halloween-sneak-peek-preview .venv/bin/python -m halloween_hub --no-browser --port 8092
```

Open <http://127.0.0.1:8092>. The standard `run.sh` / `run.ps1` launchers also work. Internet is only needed for optional real forecast/location lookup, GitHub release downloads and external product links; all teaser art and synthesized bells are local. This is the Python kiosk branch, not a new browser-only release.

## Checks

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/check_sneak_peek.py --url http://127.0.0.1:8092
```

The calendar tests cover Toronto dates, timezone boundaries, daylight saving, December 25/26, passed events, next year and independent party settings. The browser check covers 800×480, 1280×720, 1920×1080 and phone layouts; gift reveals and preview images; keyboard dismissal/focus; no initial/reload autoplay; actual oscillator activation, mute/dialog cancellation; randomly starting visible flurries; reduced motion; and navigation through all four screens. Screenshots/results are written to ignored `validation/sneak-peek/`.

The transition is deployed on the physical Pi 4 with preserved settings and media. Native playback, transparent overlays, controls and ten-minute frame measurements are documented in [VALIDATION.md](VALIDATION.md#pi-transition-deployment-and-transparent-overlays-2026-11-03). Audible speaker review and a new cold-boot test remain pending. The supplied short Halloween transition is integrated; the separate full Christmas arrival film remains upcoming. This edition shares one decoder between the arrival film and the dog visit; both return to the same static forest. The old looping Halloween video player stays inactive.

Validated November 3, 2026: all 28 Python tests passed; the existing `scripts/check_browser.py` regression passed with zero page errors, no overflow and 48-pixel action targets; the new sneak-peek check passed at all four sizes, including simulated visibility pause, opt-in jingles, global mute, random visible flurries and reduced motion. Browser checks used Chromium through Playwright on this desktop, not physical Pi hardware.

## Dates and artwork sources

The SPARK event date and the December 1 full-app teaser were supplied by the user. The event is fixed to `2026-12-09T17:00:00-05:00` (`America/Toronto`), even if another display timezone is selected. It does not roll forward to another year. At the start time the card says “It’s time to celebrate!”; after the event day it says “Thank you for celebrating!”.

The original generated prompt and asset provenance are in [sneak-peek-artwork.json](sneak-peek-artwork.json). The full-version preview images come from the committed review package, while product photos remain the existing main assets. No copied Mariah recording, song melody or generated singing is included.

Keep this branch local until publication or deployment is explicitly requested. Full Christmas development can continue independently from its saved branches/references.

## Supplied Halloween transition and fused forest

The supplied `haloweenfading_video.mp4` is encoded at **0.5× source speed** into a local 1280×720, 24 fps H.264 clip, 10.25 seconds including a brief last-frame hold. The first two seconds of the earlier half-speed delivery are removed to skip the glitch-prone opening; its poster is extracted from the new opening frame. Motion interpolation fills the slowed frames; the browser plays the prepared file at 1×. The video is muted, with the existing opt-in original jingles independent. No external video service is used.

The muted film starts when the dashboard first loads, then **once every 60 seconds, measured start to start**. Every headline, countdown, card and control remains visible and usable in front of it. Headline rotation does not fade the text away while a film/return/dissolve is active. There are no Restart, Replay or Skip controls, no transition status text and no “The old magic is still here” caption. Legacy first-visit completion flags no longer suppress playback.

**One last Halloween adventure** now fades the current background to the matching haunted forest opening over 4.8 seconds, then plays the trimmed Halloween-to-Christmas film from its first frame. The matching opening still stays visible until the film presents a frame. This action does not open the old showcase or enable sound. Repeated clicks during the return fade are ignored; the automatic minute cadence restarts when the film begins. All dashboard content remains in front.

The stable forest stays beneath the video until a frame is presented. The film fades in over 4.8 seconds; its last decoded frame then holds through the **4.8-second dissolve** back to the forest. The decoder is unloaded between cycles. Existing decorative flurries pause during the film and dissolve; opt-in jingles remain independent.

Dialogs, hidden tabs, navigation away and reduced motion suppress the film and cancel its scheduled repeat. Returning to an eligible dashboard starts a fresh quiet minute, with no catch-up burst. Loading failures or stalls fall back to the still and retry on the next minute. The film never steals keyboard focus or intercepts touches. All assets are local; forecast data stays independent.

The final still preserves the supplied forest composition while blending in the earlier illustrated characters; it is not pixel-identical to the source final frame.

The built-in image-generation prompt is saved in [design-sneak-fusion-prompt.txt](design-sneak-fusion-prompt.txt). Media source hash, transformation settings and provenance are recorded in [sneak-peek-artwork.json](sneak-peek-artwork.json). The supplied forest still, matching trimmed opening frame and extracted final frame are retained alongside the delivery clip.

Additional media lifecycle checks:

```sh
.venv/bin/python scripts/check_sneak_arrival.py --browser /usr/bin/brave-browser
```

The `--browser` path is optional and should point to an installed H.264-capable Chromium, Chrome or Brave executable. The bundled Playwright Chromium on this desktop lacks H.264 and exercised the unavailable-media fallback instead. On November 3, the installed Brave completed all 294 frames of the 12.25-second film with zero reported dropped frames in a headless run. Completion/reload, Skip/Replay, hidden tabs, dialogs/navigation, stalled/missing video and reduced motion passed, along with the existing browser regression, four-size teaser checks and all 28 backend tests. This short desktop check does not establish physical Pi or long-run performance.

Latest background-cycle validation: the trimmed film contains 246 frames over 10.25 seconds; the measured desktop start-to-start interval was 59.98 seconds. Text/cards remained visible and interactive at 800×480, 1280×720, 1920×1080 and phone size. The 4.8-second entry and exit fades, dialogs/hidden tabs/navigation/reduced motion, and stalled/missing video checks passed. Brave reported one dropped frame out of 246 in the short run. The physical Pi deployment, native controls, final animated logo and ten-minute measurements are documented in [VALIDATION.md](VALIDATION.md#pi-transition-deployment-and-transparent-overlays-2026-11-03).

The adventure-link sequence is checked with `.venv/bin/python scripts/check_halloween_return.py --browser /usr/bin/brave-browser`. The return took 4.917 seconds before presenting the new film. Resting/mid-film clicks, repeated clicks, foreground controls/focus, dialogs and reduced motion passed with no page errors or old encounter API requests.

Party/headline validation: all 29 Python tests passed, including the fixed Montréal event timestamp, its Wednesday weekday, the start-time boundary, display-timezone independence and preservation of custom party dates. `scripts/check_sneak_party.py` verified the live countdown and all four naturally rotating headlines at 800×480, 1280×720, 1920×1080 and phone size, including reduced-motion pause. The teaser and existing app browser regressions passed without page errors or overflow.

## Immersive dashboard bars

The header and navigation are hidden on the dashboard, giving the scene the full viewport. Tap/click anywhere outside a dialog, or press Tab/Escape, to reveal both as overlays. They hide after seven seconds without another interaction; keyboard focus within a bar keeps it available. Other screens retain their normal bars. On phones the dashboard itself scrolls so the gift/party cards remain reachable while the bars stay anchored to the viewport.


## Dog-video fallback between the main transitions

The supplied `dog_video.mp4` is delivered as `dog-eight-tenths-speed.mp4`: 1280×720, 24 fps CFR, silent H.264, **0.80× source speed encoded into the file** (12.625 seconds, browser playback at 1×). Motion interpolation fills the slowed frames. The supplied original remains unchanged.

When the roaming character is unavailable or video mode is selected, once the main arrival has completely faded back to `forest-preparing.png`, the scene rests for five seconds, fades into the dog clip over 2.4 seconds, then fades back to **that same still** over 2.4 seconds. It can repeat after another five-second still interval if there is room before the next main arrival. Normal timing allows two dog visits between main transitions. It never starts over the Halloween return, an arrival film, or an unfinished fade.

The main Halloween transition retains its 60-second start-to-start schedule and existing 4.8-second fades. Dog playback never resets that timer. A reserve window and deadline fade keep the single shared decoder available for the main transition; the manual Halloween adventure takes priority too. All text/cards remain in front. Muted dog audio, independent opt-in jingles, paused decorative motion, reduced motion, hidden tabs, dialogs, navigation, missing media and stalled media follow the same playback safeguards.

Check with `.venv/bin/python scripts/check_sneak_dog.py` and `.venv/bin/python scripts/check_sneak_dog.py --faults-only`; use `--cdp http://127.0.0.1:19223 --output validation/dog-loop/pi` for the actual kiosk through a temporary loopback SSH tunnel. The native ten-minute observer now distinguishes dog and main clips and measures the main cadence separately.


## Roaming dog prototype

The default settled forest now has an independent dog that walks across the foreground snow, gradually stops, lowers its head to sniff, raises it, idles, and turns before choosing another route. Positions, distances and pause lengths vary. Feet stay planted while sniffing; walking gait follows travel distance. A soft cached ground shadow and gentle depth scaling help it sit in the scene. It stays beneath all text and controls, with pointer events disabled. Routes avoid the upper controls; footer text remains above the foreground animal.

The new transparent sprite assets match the supplied brown-and-white puppy. They are generated storybook 3D poses, not a live 3D animal. This first prototype implements walk/stop/sniff/idle/turn only. Additional playful behaviours, peeing and entering the house need further animation assets.

On successful asset loading the roaming dog takes over the still interval, leaving the existing dog movie as fallback. The main Halloween film retains its one-minute schedule and fades. The dog fades away 700 ms before the scheduled main transition, freezes during all films, and resumes after the main forest is restored. It pauses for dialogs, page hiding/navigation and reduced motion. One 256×256 canvas draws at a maximum of 24 fps, with no second background-video decoder.

For comparisons, `?dog=video` selects the previous dog-video visits and `?dog=both` permits roaming in their short still gaps. Missing animation assets automatically use dog-video fallback. No saved settings or imported data are changed.

[Asset reference, prompts and provenance](design/roaming-dog-v1/README.md) are saved alongside the prototype. Checks: `scripts/check_roaming_dog.py` and `scripts/check_roaming_dog.py --fallback-only`; the first also accepts `--cdp` for a native Pi session.
