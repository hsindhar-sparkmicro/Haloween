# Graph Report - Haloween  (2026-10-21)

## Corpus Check
- 21 files · ~375,128 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 282 nodes · 451 edges · 16 communities (11 shown, 5 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `71686759`
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
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]

## God Nodes (most connected - your core abstractions)
1. `$()` - 60 edges
2. `Visitor` - 24 edges
3. `BrowserHub` - 19 edges
4. `Halloween Hub` - 19 edges
5. `Hidden camera and visitor adventures (supersedes preview/mirror behavior above)` - 18 edges
6. `ScenePlayer` - 17 edges
7. `$()` - 16 edges
8. `WebTests` - 15 edges
9. `Validation record — October 14, 2026` - 14 edges
10. `render()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `renderEffects()` --calls--> `mediaUrl()`  [EXTRACTED]
  web/app.js → web/browser-service.js
- `setupWelcomeChrome()` --calls--> `sync()`  [INFERRED]
  web/welcome-chrome.js → web/app.js
- `nextAmbientEffect()` --calls--> `mediaUrl()`  [EXTRACTED]
  web/app.js → web/browser-service.js
- `playRandomCue()` --calls--> `mediaUrl()`  [EXTRACTED]
  web/app.js → web/browser-service.js
- `playTrack()` --calls--> `mediaUrl()`  [EXTRACTED]
  web/app.js → web/browser-service.js

## Import Cycles
- None detected.

## Communities (16 total, 5 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (44): $(), action(), ambience, ambientControl(), ambientShuffle, api(), cue, effect (+36 more)

### Community 1 - "Community 1"
Cohesion: 0.13
Nodes (13): BrowserHub, clone(), countdown(), DEFAULTS, formatters, hub, parseParty(), parts() (+5 more)

### Community 2 - "Community 2"
Cohesion: 0.09
Nodes (9): BackgroundRotation, IdleBackgroundVideo, NightWeather, random(), smooth(), ease(), random(), selectors (+1 more)

### Community 3 - "Community 3"
Cohesion: 0.16
Nodes (7): $(), riddles, stories, icon(), icons, monsterNames, Visitor

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (21): Asset provenance, Audio and data, Background and cutscene rotation, Camera haunt (optional Raspberry Pi feature), Four screens, Halloween Hub, Halloween music and offline shuffle, Hidden camera and visitor adventures (+13 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (3): Handler, Behavior checks against a static server with the actual Pages project prefix., WebTests

### Community 7 - "Community 7"
Cohesion: 0.13
Nodes (14): Animated scene player correction, Camera orientation correction, Completed checks, Explicit validation boundaries, Half-speed idle video and longer fades (2026-10-20), Idle background video replay (2026-10-20), Idle video visibility correction (2026-10-20), Immersive scenes and optional camera update (+6 more)

### Community 8 - "Community 8"
Cohesion: 0.22
Nodes (4): EFFECTS, MESSAGES, ShuffleBag, WelcomeMessages

### Community 9 - "Community 9"
Cohesion: 0.29
Nodes (6): Artwork generation, Asset credits, Decorative night weather, Immersive scene backgrounds, Monster reveal atlas, SPARK product showcase

### Community 20 - "Community 20"
Cohesion: 0.11
Nodes (18): Added background and cutscene rotation, Added Dracula backgrounds and cutscene, Clearly visible floating weather, sound details and countdown, Floating welcome overlays and spooky messages, Hidden camera and visitor adventures (supersedes preview/mirror behavior above), Immersive welcome screen, Imported background clarity correction, Independent slow line motion and asynchronous fade schedules (+10 more)

### Community 21 - "Community 21"
Cohesion: 0.29
Nodes (6): Hidden motion camera and encounters, Local API, Local scene-effect library, Optional camera, Settings, Welcome cutscene

## Knowledge Gaps
- **80 isolated node(s):** `lastRotation`, `player`, `ambience`, `effect`, `cue` (+75 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `$()` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 6`, `Community 10`?**
  _High betweenness centrality (0.362) - this node is a cross-community bridge._
- **Why does `Visitor` connect `Community 3` to `Community 0`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `ScenePlayer` connect `Community 6` to `Community 0`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **What connects `Stage the static site and version its offline cache by content. No dependencies.`, `Behavior checks against a static server with the actual Pages project prefix.`, `lastRotation` to the rest of the system?**
  _82 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06821480406386067 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.13012477718360071 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._