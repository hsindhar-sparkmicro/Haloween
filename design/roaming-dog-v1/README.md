# Roaming dog prototype

Created with the built-in image-generation tool, using a frame from the user's `dog_video.mp4` as the visual reference. No CLI/API fallback was used. This prototype covers walk, gradual stop, lower head, sniff, raise head, idle and turning; peeing and other play actions are not implemented yet.

The runtime uses unchanged generated PNGs with their alpha preserved:

- `../../halloween_hub/static/assets/sneak-peek/roaming-dog-atlas-v1.png`: 16 poses, four columns/four rows; walking 0–7, head lowering/sniffing 8–11, idle 12–15.
- `../../halloween_hub/static/assets/sneak-peek/roaming-dog-turns-v2.png`: eight turning views, four columns/two rows. Intermediate front views support gradual direction changes.
- Matching JSON files contain source rectangles, contact anchors and dimensions. They were derived by reading the PNG alpha channel; no pixels were recolored or erased in code.

Prompts are in `generation-prompt.txt` and `turn-prompt.txt`. The reference is `dog-reference.png`. `rejected-turns-haze.png` retains the first turning attempt, which had a translucent studio haze; the final v2 was corrected using the built-in image-editing tool with this instruction:

> Remove ALL pale gray/beige studio background, floor shadows, broad glow and mottled/speckled areas between the dogs. Outside dog fur the alpha must be completely zero. Keep all eight dogs, their poses, positions, scale, colors and anatomy unchanged. Preserve fine fur-edge transparency, the 2:1 aspect and exact 4x2 cell arrangement. Do not draw a checkerboard or add backgrounds, shadows, text or marks.

The app adds a cached soft contact shadow and a subtle night-scene tint. Rendering uses a single visible canvas on every display refresh, with pre-scaled, tinted, foot-anchored pose canvases cached at load time. The backing resolution matches the displayed size and pixel density: 160×160 on the 800×480 Pi, up to 256×256 on larger/high-density displays. Adjacent poses blend with additive alpha to avoid opacity pulsing. State changes carry the last displayed blend into a 300 ms crossfade; walking retains its distance-based gait phase between routes. Intentional pauses reset the animation clock so resuming cannot jump forward. Walking gait follows distance travelled; routes accelerate and decelerate, keep feet on the foreground snow, and pause for sniffing and idle. Upper controls are excluded from paths; lower text and controls are drawn above the character and remain clickable.

The roaming character and the original dog video are both enabled by default. The Halloween arrival retains its one-minute cadence; a twelve-second still interval before the dog film leaves room for roaming. Before scheduled films, the character runs off the nearest edge without an opacity fade, waits outside the viewport, and re-enters from that side once the still returns. Manual Halloween returns trigger the exit during the background dissolve. Entry/exit use the existing gait poses with a faster, longer stride; these are not new motion-captured running assets. Dialogs, hidden pages and reduced motion suspend the character. Failed assets retain the earlier five-second-gap dog-video visits. Comparison modes: `?dog=video`, `?dog=roaming`, and the default `?dog=both`.

This is a sprite-based storybook prototype matching the supplied dog, not a fully rigged live 3D animal. Natural-looking gait and transitions need visual review; further behaviours require additional consistent animation assets.
