# Roaming dog prototype

Created with the built-in image-generation tool, using a frame from the user's `dog_video.mp4` as the visual reference. No CLI/API fallback was used. This prototype covers walk, gradual stop, lower head, sniff, raise head, idle and turning; peeing and other play actions are not implemented yet.

The runtime uses unchanged generated PNGs with their alpha preserved:

- `../../halloween_hub/static/assets/sneak-peek/roaming-dog-atlas-v1.png`: 16 poses, four columns/four rows; walking 0–7, head lowering/sniffing 8–11, idle 12–15.
- `../../halloween_hub/static/assets/sneak-peek/roaming-dog-turns-v2.png`: eight turning views, four columns/two rows. Intermediate front views support gradual direction changes.
- Matching JSON files contain source rectangles, contact anchors and dimensions. They were derived by reading the PNG alpha channel; no pixels were recolored or erased in code.

Prompts are in `generation-prompt.txt` and `turn-prompt.txt`. The reference is `dog-reference.png`. `rejected-turns-haze.png` retains the first turning attempt, which had a translucent studio haze; the final v2 was corrected using the built-in image-editing tool with this instruction:

> Remove ALL pale gray/beige studio background, floor shadows, broad glow and mottled/speckled areas between the dogs. Outside dog fur the alpha must be completely zero. Keep all eight dogs, their poses, positions, scale, colors and anatomy unchanged. Preserve fine fur-edge transparency, the 2:1 aspect and exact 4x2 cell arrangement. Do not draw a checkerboard or add backgrounds, shadows, text or marks.

The app adds a cached soft contact shadow and a subtle night-scene tint. Rendering uses a single 256×256 canvas with bounded 24 fps drawing. Adjacent poses blend with additive alpha to avoid opacity pulsing. Walking gait follows distance travelled; routes accelerate and decelerate, keep feet on the foreground snow, and pause for sniffing and idle. Upper controls are excluded from paths; lower text and controls are drawn above the character and remain clickable.

On successful asset loading, the roaming character owns the settled forest interval. The Halloween arrival retains its one-minute cadence. The character fades out and freezes before/during video playback, and pauses behind dialogs, hidden pages and reduced motion. Failed assets retain the earlier dog-video visits. For comparison, `?dog=video` selects the existing video-only dog visits and `?dog=both` allows roaming in their short still gaps.

This is a sprite-based storybook prototype matching the supplied dog, not a fully rigged live 3D animal. Natural-looking gait and transitions need visual review; further behaviours require additional consistent animation assets.
