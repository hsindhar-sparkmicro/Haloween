# Natural dog replacement

The current 60 FPS canvas implementation passed rendering cadence checks, but visual review rejected its accelerated walking exit, crossfaded turn and unexpressive face. Those are asset/animation problems, not proof that a higher draw rate is needed.

The supplied `dog_video.mp4` was inspected as a reference: it includes walking, sniffing and turning in a moving full scene. It is not an isolated, reusable running cycle or an expressive idle library.

[Copy-ready Grok animation brief](GROK-DOG-ANIMATION-BRIEF.md) uses the [existing puppy reference](../roaming-dog-v1/dog-reference.png). Begin with an expressive idle and a genuine gentle run; review moving footage before building the remaining set or replacing the live character.

A rigged 3D asset is the other route. It needs distinct walk/run animations, planted turning, and facial controls or expression clips. A body skeleton alone does not establish facial support, and an animated animal advertised as low-poly is not automatically a match for this puppy. No third-party asset has been purchased or integrated.

Research checked on 2026-11-03:

- [Blender Studio Dog rig](https://studio.blender.org/characters/dog/v1/): an expressive character under CC-BY, but its author requires Blender 3.6 and describes it as complex. It would require a new visual treatment and animation/export work.
- [Blender Studio DOGWALK animation process](https://studio.blender.org/blog/animations-for-dogwalk/): its deliberately held, stop-motion poses conflict with the requested fluid motion unless re-authored; do not adopt it unchanged as a smoothness fix.
- [Border collie puppy model by Jack.LaLonde](https://sketchfab.com/3d-models/puppy-border-collie-poly-art-0a0b504f51a94d95a2d492d3c372ebe5): lists walk, run and idle under CC Attribution, but the listing does not establish facial controls or a matching appearance.

No new animation quality claim or Pi qualification is made by this brief. The roaming overlay is now disabled at the user’s request; only the original dog video is active. This replacement brief is retained for later work.
