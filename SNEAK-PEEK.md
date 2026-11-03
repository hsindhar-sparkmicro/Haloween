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
- Black Friday and Boxing Day are calendar teasers, not live offers or guaranteed discounts. The current-year dates become “today” or “wrapped for this year” instead of showing stale negative countdowns.
- The existing Halloween adventures, haunted controls, party management and simulated detector remain available. The main branch's backend and kiosk controls are retained.

## Local preview

Use a separate data directory for a review session so production records are not modified:

```sh
HALLOWEEN_DATA_DIR=/tmp/halloween-sneak-peek-preview .venv/bin/python -m halloween_hub --no-browser --port 8092
```

Open <http://127.0.0.1:8092>. The standard `run.sh` / `run.ps1` launchers also work. Internet is only needed for optional real forecast/location lookup and external product links; all teaser art and synthesized bells are local. This is the Python kiosk branch, not a new browser-only release or deployment.

## Checks

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/check_sneak_peek.py --url http://127.0.0.1:8092
```

The calendar tests cover Toronto dates, timezone boundaries, daylight saving, December 25/26, passed events, next year and independent party settings. The browser check covers 800×480, 1280×720, 1920×1080 and phone layouts; gift reveals and preview images; keyboard dismissal/focus; no initial/reload autoplay; actual oscillator activation, mute/dialog cancellation; randomly starting visible flurries; reduced motion; and navigation through all four screens. Screenshots/results are written to ignored `validation/sneak-peek/`.

Physical Pi qualification, ten-minute ambient measurements and audible speaker review remain pending. The supplied short Halloween transition is integrated; the separate full Christmas arrival film remains upcoming. This edition has one arrival-video decoder, followed by a static forest; the old looping Halloween video player stays inactive.

Validated November 3, 2026: all 28 Python tests passed; the existing `scripts/check_browser.py` regression passed with zero page errors, no overflow and 48-pixel action targets; the new sneak-peek check passed at all four sizes, including simulated visibility pause, opt-in jingles, global mute, random visible flurries and reduced motion. Browser checks used Chromium through Playwright on this desktop, not physical Pi hardware.

## Dates and artwork sources

Black Friday is the Friday after the fourth Thursday of November: November 27 in 2026, as listed by [Best Buy Canada](https://www.bestbuy.ca/en-ca/collection/black-friday/413517). Boxing Day is December 26; use the calendar date rather than a substitute bank closure date. See [Time and Date's Canadian Boxing Day calendar](https://www.timeanddate.com/holidays/canada/boxing-day). Dates checked November 3, 2026.

The original generated prompt and asset provenance are in [sneak-peek-artwork.json](sneak-peek-artwork.json). The full-version preview images come from the committed review package, while product photos remain the existing main assets. No copied Mariah recording, song melody or generated singing is included.

Keep this branch local until publication or deployment is explicitly requested. Full Christmas development can continue independently from its saved branches/references.

## Supplied Halloween transition and fused forest

The supplied `haloweenfading_video.mp4` is encoded at **0.5× source speed** into a local 1280×720, 24 fps H.264 clip, 12.25 seconds including a brief last-frame hold. Motion interpolation fills the slowed frames; the browser plays the prepared file at 1×. The video is muted, with the existing opt-in original jingles independent. No external video service is used.

On first visit, the film runs once with a **Skip transition** control. Completion or Skip is remembered per browser. Use the subtle glowing **Restart video** charm beside the tree to replay the whole scene from the beginning, including during playback. **The Christmas House → Replay Halloween → Christmas · ½ speed** also remains available. Reduced motion uses the stable scene directly. Errors, stalls, dialogs, hidden tabs and navigation return to the still without marking an interrupted viewing complete.

A matching first-frame poster stays beneath the video until a frame is presented. At completion the last decoded frame remains while a 4.8-second dissolve reveals the fused forest. Then the video is unloaded; the scene does not loop or pan. Existing occasional decorative flurries resume after the transition. Forecast data remains independent. The final still preserves the supplied forest composition while blending in the earlier illustrated characters; it is not pixel-identical to the source final frame.

The built-in image-generation prompt is saved in [design-sneak-fusion-prompt.txt](design-sneak-fusion-prompt.txt). Media source hash, transformation settings and provenance are recorded in [sneak-peek-artwork.json](sneak-peek-artwork.json). The supplied original still and extracted first/last video frames are retained alongside the delivery clip.

Additional media lifecycle checks:

```sh
.venv/bin/python scripts/check_sneak_arrival.py --browser /usr/bin/brave-browser
```

The `--browser` path is optional and should point to an installed H.264-capable Chromium, Chrome or Brave executable. The bundled Playwright Chromium on this desktop lacks H.264 and exercised the unavailable-media fallback instead. On November 3, the installed Brave completed all 294 frames of the 12.25-second film with zero reported dropped frames in a headless run. Completion/reload, Skip/Replay, hidden tabs, dialogs/navigation, stalled/missing video and reduced motion passed, along with the existing browser regression, four-size teaser checks and all 28 backend tests. This short desktop check does not establish physical Pi or long-run performance.
