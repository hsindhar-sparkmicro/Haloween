# Graph Report - Haloween  (2026-10-15)

## Corpus Check
- 66 files · ~288,421 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 389 nodes · 573 edges · 52 communities (15 shown, 37 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.65)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 51|Community 51]]

## God Nodes (most connected - your core abstractions)
1. `$()` - 62 edges
2. `Visitor` - 24 edges
3. `create_app()` - 23 edges
4. `Simulation` - 18 edges
5. `CameraTests` - 18 edges
6. `ScenePlayer` - 17 edges
7. `Hidden camera and visitor adventures (supersedes preview/mirror behavior above)` - 17 edges
8. `$()` - 16 edges
9. `HubTests` - 16 edges
10. `Camera` - 14 edges

## Surprising Connections (you probably didn't know these)
- `MediaTests` --uses--> `Store`  [INFERRED]
  tests/test_media.py → halloween_hub/core.py
- `HubTests` --uses--> `Weather`  [INFERRED]
  tests/test_app.py → halloween_hub/weather.py
- `main()` --calls--> `create_app()`  [EXTRACTED]
  halloween_hub/__main__.py → halloween_hub/app.py
- `create_app()` --calls--> `Camera`  [EXTRACTED]
  halloween_hub/app.py → halloween_hub/camera.py
- `create_app()` --calls--> `Simulation`  [EXTRACTED]
  halloween_hub/app.py → halloween_hub/core.py

## Import Cycles
- None detected.

## Communities (52 total, 37 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (16): create_app(), countdown(), data_directory(), backgrounds(), cutscenes(), Discover only installed gallery media in app data., main(), import_audio() (+8 more)

### Community 1 - "Community 1"
Cohesion: 0.15
Nodes (8): Shared simulation boundary. No GPIO or sensor access., Shared simulation boundary. No GPIO or sensor access., Shared simulation boundary. No GPIO or sensor access., Shared simulation boundary. No GPIO or sensor access., Shared simulation boundary. No GPIO or sensor access., Shared simulation boundary. No GPIO or sensor access., Simulation, Store

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (48): $(), action(), ambience, ambientControl(), ambientShuffle, api(), cue, discoverWindowControls() (+40 more)

### Community 4 - "Community 4"
Cohesion: 0.12
Nodes (15): Asset provenance, Audio and data, Background and cutscene rotation, Camera haunt (optional Raspberry Pi feature), Four screens, Halloween Hub, Halloween music and offline shuffle, Hidden camera and visitor adventures (+7 more)

### Community 5 - "Community 5"
Cohesion: 0.29
Nodes (7): manage(), Minimize only a browser window titled Halloween Hub; never simulate global keys., read_string(), string(), uint(), WaylandWindows, windows_target()

### Community 9 - "Community 9"
Cohesion: 0.50
Nodes (3): Artwork generation, Immersive scene backgrounds, Monster reveal atlas

### Community 20 - "Community 20"
Cohesion: 0.08
Nodes (24): Added background and cutscene rotation, Added Dracula backgrounds and cutscene, Animated scene player correction, Camera orientation correction, Clearly visible floating weather, sound details and countdown, Completed checks, Explicit validation boundaries, Floating welcome overlays and spooky messages (+16 more)

### Community 21 - "Community 21"
Cohesion: 0.29
Nodes (6): Hidden motion camera and encounters, Local API, Local scene-effect library, Optional camera, Settings, Welcome cutscene

### Community 32 - "Community 32"
Cohesion: 0.16
Nodes (7): $(), riddles, stories, icon(), icons, monsterNames, Visitor

### Community 38 - "Community 38"
Cohesion: 0.09
Nodes (10): BackgroundRotation, WelcomeAtmosphere, ease(), random(), selectors, WelcomeFloat, EFFECTS, MESSAGES (+2 more)

## Knowledge Gaps
- **61 isolated node(s):** `lastRotation`, `player`, `ambience`, `effect`, `cue` (+56 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **37 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `$()` connect `Community 2` to `Community 32`, `Community 3`, `Community 38`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `create_app()` connect `Community 0` to `Community 1`, `Community 26`, `Community 27`, `Community 5`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `Visitor` connect `Community 32` to `Community 2`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **What connects `Halloween Hub: offline-first entertainment kiosk.`, `Hidden motion scans with physical capture shutdown between scan windows.`, `Hidden Pi motion scan. Only numerical scores leave this process.` to the rest of the system?**
  _105 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.07678075855689177 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.14624505928853754 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.06265664160401002 - nodes in this community are weakly interconnected._