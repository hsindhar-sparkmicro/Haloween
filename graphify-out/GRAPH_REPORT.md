# Graph Report - Haloween  (2026-11-03)

## Corpus Check
- 89 files · ~1,186,045 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 554 nodes · 808 edges · 72 communities (22 shown, 50 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.65)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `16ccd0f7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

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
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]

## God Nodes (most connected - your core abstractions)
1. `$()` - 66 edges
2. `create_app()` - 26 edges
3. `Visitor` - 24 edges
4. `Simulation` - 18 edges
5. `$()` - 18 edges
6. `CameraTests` - 18 edges
7. `Hidden camera and visitor adventures (supersedes preview/mirror behavior above)` - 18 edges
8. `ScenePlayer` - 17 edges
9. `$()` - 16 edges
10. `HubTests` - 16 edges

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

## Communities (72 total, 50 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (19): create_app(), countdown(), data_directory(), backgrounds(), cutscenes(), Discover only installed gallery media in app data., main(), import_audio() (+11 more)

### Community 1 - "Community 1"
Cohesion: 0.15
Nodes (8): Shared simulation boundary. No GPIO or sensor access., Shared simulation boundary. No GPIO or sensor access., Shared simulation boundary. No GPIO or sensor access., Shared simulation boundary. No GPIO or sensor access., Shared simulation boundary. No GPIO or sensor access., Shared simulation boundary. No GPIO or sensor access., Simulation, Store

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (49): $(), action(), ambience, ambientControl(), ambientShuffle, api(), cue, discoverWindowControls() (+41 more)

### Community 4 - "Community 4"
Cohesion: 0.11
Nodes (18): Asset provenance, Audio and data, Background and cutscene rotation, Camera haunt (optional Raspberry Pi feature), Four screens, Halloween Hub, Halloween music and offline shuffle, Hidden camera and visitor adventures (+10 more)

### Community 5 - "Community 5"
Cohesion: 0.29
Nodes (7): manage(), Minimize only a browser window titled Halloween Hub; never simulate global keys., read_string(), string(), uint(), WaylandWindows, windows_target()

### Community 9 - "Community 9"
Cohesion: 0.33
Nodes (5): Artwork generation, Decorative night weather, Immersive scene backgrounds, Monster reveal atlas, SPARK product showcase

### Community 20 - "Community 20"
Cohesion: 0.06
Nodes (32): Added background and cutscene rotation, Added Dracula backgrounds and cutscene, Animated scene player correction, Camera orientation correction, Clearly visible floating weather, sound details and countdown, Completed checks, Explicit validation boundaries, Floating welcome overlays and spooky messages (+24 more)

### Community 21 - "Community 21"
Cohesion: 0.29
Nodes (6): Hidden motion camera and encounters, Local API, Local scene-effect library, Optional camera, Settings, Welcome cutscene

### Community 32 - "Community 32"
Cohesion: 0.16
Nodes (7): $(), riddles, stories, icon(), icons, monsterNames, Visitor

### Community 38 - "Community 38"
Cohesion: 0.07
Nodes (13): BackgroundRotation, IdleBackgroundVideo, NightWeather, random(), smooth(), ease(), random(), selectors (+5 more)

### Community 52 - "Community 52"
Cohesion: 0.67
Nodes (3): main(), quoted(), Install per-user Raspberry Pi desktop autostart; no root access required.

### Community 55 - "Community 55"
Cohesion: 0.39
Nodes (5): asset(), masthead(), productImage(), products, SparkShowcase

### Community 57 - "Community 57"
Cohesion: 0.50
Nodes (3): assets, images_unmodified, retrieved

### Community 60 - "Community 60"
Cohesion: 0.21
Nodes (4): $(), gifts, SneakAtmosphere, SneakPeek

### Community 63 - "Community 63"
Cohesion: 0.07
Nodes (28): arrival_media, audio, browser_playback_rate, delivery_duration_seconds, encode, file, filter, fps (+20 more)

### Community 65 - "Community 65"
Cohesion: 0.25
Nodes (7): After the haunt — Christmas sneak peek, Checks, Dates and artwork sources, Immersive dashboard bars, Local preview, Supplied Halloween transition and fused forest, What works

### Community 68 - "Community 68"
Cohesion: 0.53
Nodes (5): Check real background video, a real one-minute repeat, and interruption recovery, replay(), start(), state(), still()

## Knowledge Gaps
- **111 isolated node(s):** `lastRotation`, `player`, `ambience`, `effect`, `cue` (+106 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **50 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `$()` connect `Community 2` to `Community 32`, `Community 3`, `Community 70`, `Community 38`, `Community 60`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `$()` connect `Community 60` to `Community 2`, `Community 67`, `Community 38`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `Visitor` connect `Community 32` to `Community 2`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **What connects `Halloween Hub: offline-first entertainment kiosk.`, `Hidden motion scans with physical capture shutdown between scan windows.`, `Hidden Pi motion scan. Only numerical scores leave this process.` to the rest of the system?**
  _169 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06412583182093164 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.14624505928853754 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.06110102843315184 - nodes in this community are weakly interconnected._