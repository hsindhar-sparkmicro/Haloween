# Graph Report - Haloween  (2026-11-03)

## Corpus Check
- 107 files · ~1,552,488 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 742 nodes · 1078 edges · 93 communities (33 shown, 60 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `04f117f9`
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
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 86|Community 86]]
- [[_COMMUNITY_Community 87|Community 87]]
- [[_COMMUNITY_Community 88|Community 88]]
- [[_COMMUNITY_Community 89|Community 89]]
- [[_COMMUNITY_Community 90|Community 90]]
- [[_COMMUNITY_Community 91|Community 91]]
- [[_COMMUNITY_Community 92|Community 92]]

## God Nodes (most connected - your core abstractions)
1. `$()` - 68 edges
2. `create_app()` - 29 edges
3. `RoamingDog` - 24 edges
4. `Visitor` - 24 edges
5. `Simulation` - 18 edges
6. `SneakArrival` - 18 edges
7. `$()` - 18 edges
8. `$()` - 18 edges
9. `arrival_media` - 18 edges
10. `CameraTests` - 18 edges

## Surprising Connections (you probably didn't know these)
- `MediaTests` --uses--> `Store`  [INFERRED]
  tests/test_media.py → halloween_hub/core.py
- `FakeGitHub` --uses--> `Store`  [INFERRED]
  tests/test_updates.py → halloween_hub/core.py
- `UpdatesTests` --uses--> `Store`  [INFERRED]
  tests/test_updates.py → halloween_hub/core.py
- `HubTests` --uses--> `Weather`  [INFERRED]
  tests/test_app.py → halloween_hub/weather.py
- `FakeGitHub` --uses--> `SafeRedirect`  [INFERRED]
  tests/test_updates.py → halloween_hub/updates.py

## Import Cycles
- None detected.

## Communities (93 total, 60 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.22
Nodes (8): create_app(), backgrounds(), cutscenes(), Discover only installed gallery media in app data., main(), import_audio(), Validated, content-addressed local audio imports; repeated imports are idempoten, MediaTests

### Community 1 - "Community 1"
Cohesion: 0.18
Nodes (7): Shared simulation boundary. No GPIO or sensor access., Shared simulation boundary. No GPIO or sensor access., Shared simulation boundary. No GPIO or sensor access., Shared simulation boundary. No GPIO or sensor access., Shared simulation boundary. No GPIO or sensor access., Shared simulation boundary. No GPIO or sensor access., Simulation

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (51): $(), action(), ambience, ambientControl(), ambientShuffle, api(), cue, discoverWindowControls() (+43 more)

### Community 4 - "Community 4"
Cohesion: 0.10
Nodes (19): Asset provenance, Audio and data, Automatic release downloads, Background and cutscene rotation, Camera haunt (optional Raspberry Pi feature), Four screens, Halloween Hub, Halloween music and offline shuffle (+11 more)

### Community 5 - "Community 5"
Cohesion: 0.29
Nodes (7): manage(), Minimize only a browser window titled Halloween Hub; never simulate global keys., read_string(), string(), uint(), WaylandWindows, windows_target()

### Community 9 - "Community 9"
Cohesion: 0.33
Nodes (5): Artwork generation, Decorative night weather, Immersive scene backgrounds, Monster reveal atlas, SPARK product showcase

### Community 20 - "Community 20"
Cohesion: 0.05
Nodes (36): Added background and cutscene rotation, Added Dracula backgrounds and cutscene, Animated scene player correction, Camera orientation correction, Clearly visible floating weather, sound details and countdown, Completed checks, Display-refresh dog rendering and video edge handoffs (2026-11-03), Dog visit between stable forest backgrounds (2026-11-03) (+28 more)

### Community 21 - "Community 21"
Cohesion: 0.29
Nodes (6): Hidden motion camera and encounters, Local API, Local scene-effect library, Optional camera, Settings, Welcome cutscene

### Community 32 - "Community 32"
Cohesion: 0.11
Nodes (12): asset(), masthead(), productImage(), products, SparkShowcase, $(), riddles, stories (+4 more)

### Community 38 - "Community 38"
Cohesion: 0.07
Nodes (13): BackgroundRotation, IdleBackgroundVideo, NightWeather, random(), smooth(), ease(), random(), selectors (+5 more)

### Community 52 - "Community 52"
Cohesion: 0.67
Nodes (3): main(), quoted(), Install per-user Raspberry Pi desktop autostart; no root access required.

### Community 55 - "Community 55"
Cohesion: 0.07
Nodes (11): GitHub, newer(), Download verified GitHub release packages; never execute or replace running code, ReleaseUpdates, SafeRedirect, sha256(), stable_version(), Update this version before packaging a release. (+3 more)

### Community 57 - "Community 57"
Cohesion: 0.50
Nodes (3): assets, images_unmodified, retrieved

### Community 60 - "Community 60"
Cohesion: 0.21
Nodes (4): $(), gifts, SneakAtmosphere, SneakPeek

### Community 63 - "Community 63"
Cohesion: 0.11
Nodes (18): arrival_media, audio, browser_playback_rate, delivery_duration_seconds, delivery_sha256, encode, file, filter (+10 more)

### Community 65 - "Community 65"
Cohesion: 0.17
Nodes (11): After the haunt — Christmas sneak peek, Checks, Dates and artwork sources, Dog video between the main transitions, Dog-video fallback between the main transitions, Dog visits between the main transitions, Immersive dashboard bars, Local preview (+3 more)

### Community 67 - "Community 67"
Cohesion: 0.50
Nodes (3): GitHub release downloads, Private repository access, Release contract

### Community 68 - "Community 68"
Cohesion: 0.53
Nodes (5): Check real background video, a real one-minute repeat, and interruption recovery, replay(), start(), state(), still()

### Community 73 - "Community 73"
Cohesion: 0.21
Nodes (4): clamp(), random(), RoamingDog, smooth()

### Community 74 - "Community 74"
Cohesion: 0.04
Nodes (45): background_wordmark, file, notes, sha256, source, base, branch, created (+37 more)

### Community 76 - "Community 76"
Cohesion: 0.67
Nodes (3): Check natural dog/still cycles and main-film priority, locally or in the native, still(), wait_state()

### Community 79 - "Community 79"
Cohesion: 0.24
Nodes (4): countdown(), fetch(), search_locations(), Weather

### Community 80 - "Community 80"
Cohesion: 0.31
Nodes (3): Calendar facts for the isolated November sneak-peek edition., sneak_peek_calendar(), SneakPeekCalendarTests

### Community 81 - "Community 81"
Cohesion: 0.38
Nodes (3): data_directory(), Copy local PNG backgrounds into application data, deduplicated by content., Copy browser-compatible cutscene files into app data; preserve source files.

### Community 82 - "Community 82"
Cohesion: 0.15
Nodes (12): animations, idle, lower, raise, sniff, walk, frames, height (+4 more)

### Community 83 - "Community 83"
Cohesion: 0.14
Nodes (13): 1. Happy, attentive idle — `idle-happy-right`, 2. Genuine gentle run — `run-right`, 3. Calm walk — `walk-right`, 4. Planted turn — `turn-right-to-left`, 5. Sniff and look up — `sniff-right`, 6. Notice the next scene — `alert-right`, 7. Start and settle — `start-run-right`, `run-stop-right`, Delivery (+5 more)

### Community 84 - "Community 84"
Cohesion: 0.40
Nodes (4): frames, height, image, width

### Community 85 - "Community 85"
Cohesion: 0.40
Nodes (4): frames, height, image, width

## Knowledge Gaps
- **186 isolated node(s):** `image`, `width`, `height`, `frames`, `lastRotation` (+181 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **60 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `$()` connect `Community 2` to `Community 32`, `Community 3`, `Community 38`, `Community 90`, `Community 60`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Why does `$()` connect `Community 60` to `Community 73`, `Community 2`, `Community 38`, `Community 70`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `create_app()` connect `Community 0` to `Community 1`, `Community 5`, `Community 78`, `Community 79`, `Community 80`, `Community 81`, `Community 55`, `Community 88`, `Community 26`, `Community 27`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **What connects `image`, `width`, `height` to the rest of the system?**
  _253 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.059322033898305086 - nodes in this community are weakly interconnected._
- **Should `Community 4` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Should `Community 20` be split into smaller, more focused modules?**
  _Cohesion score 0.05405405405405406 - nodes in this community are weakly interconnected._