# Natural dog animation — replacement asset brief

Status: asset request, not an implemented or visually approved replacement. The current sprite prototype has no true running cycle or facial rig. Rendering it at 60 FPS does not fix its gait, turn, or expression.

## Reference to attach

Attach `../roaming-dog-v1/dog-reference.png` (the puppy in the user's original `dog_video.mp4`). Use the dog alone as the identity reference. Keep its brown-and-white coat markings, white facial blaze, large dark eyes, floppy brown ears, curled fluffy tail, red collar and proportions. Do not reproduce the forest, people, gifts, pumpkins or camera movement from that image.

Generate the following as separate continuous videos. Do not generate sprite sheets or a slideshow of poses. First make the happy idle and gentle run as a small review batch; check those at dashboard size before generating the remaining clips.

## Shared direction — prepend to every prompt

> One consistent brown-and-white puppy matching the attached reference, cinematic 3D storybook rendering, believable canine anatomy and weight. Expressive eyes, natural blinking, soft ears and subtle breathing. Locked camera and exposure, no zoom, orbit, cuts, shake or motion blur. Full body, tail and every paw visible throughout, with ample empty margins. The animal occupies roughly the central half of the frame. Its standing height, ground line and camera angle stay identical between clips. Use a slightly elevated side/three-quarter camera matching the reference so the face remains readable. Render against a flat, evenly lit saturated green background with no scenery, floor texture, particles, props, lettering, watermark or green light reflected onto the fur. No painted checkerboard. A transparent export is preferable if the workflow genuinely supports alpha; otherwise keep the solid green background for later matting. No dialogue or music. Normal-speed motion, never fast-forward or slow motion. Keep the same dog, fur markings, eye placement, muzzle and limb count in every frame.

Format: landscape 16:9 working plates. The overlay will be cropped and composited later; this is not a full-screen scene. Ask for native 60 FPS where available, otherwise supply the highest native frame rate without changing motion speed. Do not claim that a 60 FPS container or repeated frames creates 60 distinct poses. Exact output duration/frame rate depends on the generation workflow; the durations below are creative targets.

Use the approved idle ending frame as the starting reference for compatible actions, and reuse the same character reference for every generation. Keep original downloaded files.

## 1. Happy, attentive idle — `idle-happy-right`

Target 6–8 seconds, loop candidate.

> The puppy stands comfortably facing right, in the agreed three-quarter view. It breathes quietly, looks toward the viewer with soft curious eyes, blinks naturally once, gives a small head tilt, then relaxes. Its ears respond subtly to the head movement. A friendly, relaxed open mouth and a tiny tongue movement suggest gentle panting; no human grin or speech. The tail gives two unhurried wags. Its paws stay planted and its body does not drift or change size. Finish in the same calm neutral stance and gaze as the opening, and hold that pose briefly. Make the expression readable without exaggerating the entire body.

## 2. Genuine gentle run — `run-right`

Target 4–6 seconds, repeating cycle candidate.

> The puppy performs a relaxed, playful canter facing right, staying centred as an in-place animation. This must be a distinct running gait, not walking played faster. Show a coordinated hind-leg push, gathering and extension of the body, a brief light airborne phase and controlled forepaw landing. The shoulders and hips respond to contact and weight transfer; the head stays comfortably stable while the ears and tail follow with soft inertia. The expression is happy and attentive with relaxed eyes and a slightly open mouth. Keep the motion unhurried and readable, with consistent stride length and cycle timing. No scrambling legs, sliding stance feet, frantic sprinting, frozen face or rubbery limb stretching. Finish at the same gait phase as the opening for a loop.

The in-place clip needs application translation matched to the backward motion of planted paws. Supplying a known-distance travelling take as a reference is useful; do not independently speed up the legs to meet a video deadline.

## 3. Calm walk — `walk-right`

Target 4–6 seconds, repeating cycle candidate.

> The puppy walks calmly facing right, centred in place. Show a clear four-beat walking gait, deliberate paw placement and gentle shoulder/hip movement. Each planted paw moves consistently backward relative to the body during its stance, then lifts and swings forward. No skating, bouncing run or repeated frozen poses. The puppy occasionally glances slightly ahead with alert eyes; ears and tail move subtly. Keep its body size, head proportions and baseline stable. Finish at the same gait phase as the opening.

## 4. Planted turn — `turn-right-to-left`

Target 3–4 seconds, non-looping action.

> Start in the same neutral right-facing stance as the approved idle, and hold for half a second. The puppy notices something to its left: eyes and head look first, then its front paws step around a small arc while its hind paws reposition naturally. Its shoulders and hips follow as one continuous solid animal until it faces left. It must take small supporting steps and transfer its weight; never spin on a vertical axis, slide sideways, mirror suddenly, dissolve between views or morph into another dog. The face remains curious, with an ear perk and a natural blink. Finish in a balanced left-facing neutral stance and hold for half a second. Keep the camera fixed and preserve the same standing height throughout.

Generate `turn-left-to-right` as a separate reversed action with the same constraints, not by reversing video time. Preserve the actual coat markings.

## 5. Sniff and look up — `sniff-right`

Target 5–7 seconds, complete action.

> Start from the approved neutral right-facing stance. The puppy notices an interesting scent, lowers its head with its neck and shoulders following naturally, makes two or three small nose movements near the ground, then raises its head. Its eyes track the scent and then look up toward the viewer with a curious expression. Add one small ear flick and a soft blink. The paws remain planted except for one plausible settling step; no whole-body drift, feet sliding or changing proportions. Finish in the same neutral stance as the opening, holding briefly.

## 6. Notice the next scene — `alert-right`

Target 2–3 seconds, complete action.

> The puppy is standing in its approved neutral pose. Its eyes notice something offscreen to the right; the ears perk, the head follows, and the body leans forward slightly in anticipation. Give it a bright, interested expression and a small tail wag. It does not start running yet. Finish in a poised, balanced stance ready to take a first step. Keep the movement small and natural, with no dramatic startled jump.

## 7. Start and settle — `start-run-right`, `run-stop-right`

Target 2–3 seconds each, separate actions.

> Start-run: from the alert stance, the puppy shifts its weight, pushes off and takes its first two relaxed canter strides, settling into the same gait and tempo as the approved run loop. No sudden speed jump, long slide or acceleration of a walking loop.

> Run-stop: begin at the same gait and tempo as the approved run loop. The puppy takes shorter landing steps, settles its weight and comes to a comfortable stand. It looks pleased, gives a soft blink and a small tail wag. No abrupt freeze, backward sliding or reversal of a starting clip.

## Left-facing versions

After the first batch is approved, generate left-facing versions of idle, walk, run, sniff, alert, start and stop using the same character and camera. A mirrored right-facing image would also mirror the coat markings; prefer actual left-facing takes for the finished animal.

## Visual acceptance before app integration

Review moving footage at normal speed, both enlarged and at approximately the real on-screen dog size. A frame-rate counter is not a substitute for this review.

- Run is visibly different from walk; no fast-forward walk masquerading as a run.
- Turns show planted steps, a consistent torso and continuous face orientation.
- Eyes, blink, mouth, ears and head convey friendly/curious/alert states without a human talking face.
- No changing muzzle, drifting eyes, growing paws, extra legs, changing coat patches or tail deformation.
- Compare the first and last loop frames and inspect the motion across the seam; similar stills alone do not prove a clean loop.
- Check contact points and stride travel before assigning screen speed. Give the dog enough time to exit; do not accelerate the clip just to beat a film timer.
- Check the alpha/matte over both light snow and dark trees for green spill, haloing and lost fur. Keep the contact shadow separate where practical.
- Reject abrupt pose changes rather than hiding them with whole-body image dissolves.

## Delivery

Supply the original video files, the reference/seed or adjacent reference frames used where available, and the intended action names. Do not bake the forest, dashboard, titles or music into these clips. A small proof batch of `idle-happy-right` and `run-right` is enough to judge whether this workflow can deliver the required motion before investing in the full set.

Final delivery encodes or frame atlases should be created only after visual approval. Normal playback speed must preserve the approved performance. The Pi implementation should retain offline assets, foreground controls, reduced-motion handling and one active background decoder; use measured memory/render budgets when selecting an overlay format.
