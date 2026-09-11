# Micro Tower Defense
 
A small, complete, pixel-art tower defense game built solo in Python/pygame.
 
Three maps. Three towers. Four enemy types. Fifteen waves. Built to be finished, not feature-complete.
 
## Overview
 
Enemies spawn at the edge of the map and walk a fixed snake-shaped path toward your base. You place towers along the route to kill them before they get there. Kill enemies for gold, spend gold on more towers, clear every wave on all three levels to win. Lose all your lives and it's game over.
 
Rendered at a native low resolution and scaled up 4x with nearest-neighbor scaling for a crisp, intentional pixel-art look — not blurry placeholder shapes.
 
## Features
 
- **3 tower types**, each with a distinct role and a distinct silhouette (no two towers look or play alike)
- **4 enemy types**, from a fast fragile runner to a slow 180hp brute
- **3 levels**, each with its own path, its own wave table, and stat multipliers on every enemy
- **15 hardcoded waves** with increasing difficulty
- **Per-type tower limits** that reset each level, so every level is a fresh build puzzle rather than a gold pile
- **Hand-designed pixel sprites** built from layered primitive shapes (no external art assets) — color-matched directly to each entity's underlying stats
- **Towers visually track their target** — barrels and spike clusters rotate to face whatever enemy they're currently locked onto, and hold their last facing when nothing's in range
- **Full economy loop** — gold in from kills, gold out on placement, real tradeoffs between tower types
- **Audio feedback** on every core action — shoot, hit, death, wave start

## How to play
 
**Objective:** clear every wave on all three levels without losing all 10 lives.

**Controls:**
- Left-click a tower button in the HUD to select which tower type you're placing
- Left-click an empty (non-path) tile on the grid to place it, if you can afford it
- Towers fire automatically — no further input needed once placed
- Between levels the game pauses on a build phase; place towers, then click CONTINUE

Towers cannot be placed within ~1.5 tiles of another tower, and each type has a
per-level purchase cap. Gold and lives carry across levels; towers do not.

### Towers
 
| Tower | Cost | Damage | Range | Cooldown | Max per level | Role |
|---|---|---|---|---|---|---|
| Gunner | 50g | 10 | 60 | 0.3s | 4 | Fast, single-target DPS |
| Cannon | 250g | 20 | 50 | 1.2s | 2 | Splash damage (radius 24) — best against clustered enemies |
| Frost | 400g | 4 | 55 | 0.8s | 1 | Low damage, slows target to 50% speed for 2s — crowd control |

Frost is locked on level 1 and unlocks from level 2 onward.
 
### Enemies
 
| Enemy | HP | Speed | Gold reward | Notes |
|---|---|---|---|---|
| Walker | 30 | 40 | 5g | Basic enemy, present in every wave |
| Armored | 90 | 25 | 12g | Tougher, introduced starting wave 3 |
| Runner | 18 | 70 | 8g | Fragile but fast enough to slip past thin coverage |
| Brute | 180 | 18 | 25g | Slow damage sponge, introduced on level 2 |

### Levels

| Level | Waves | Enemy HP | Enemy speed |
|---|---|---|---|
| 1 | 4 | ×1.0 | ×1.0 |
| 2 | 5 | ×1.4 | ×1.15 |
| 3 | 6 | ×1.8 | ×1.3 |

Level 1 waves:
1. 8× Walker
2. 12× Walker
3. 6× Walker + 4× Armored
4. 8× Walker + 8× Armored

You start with **150 gold** and **10 lives**. Each enemy that reaches the end costs 1 life.
 
## Tech stack
 
- Python 3
- pygame (only dependency)

No game engine, no external art pipeline, no asset files beyond a font and a handful of short sound effects.
 
## Running it
 
```bash
pip install pygame
python main.py
```
 
## Building a standalone executable
 
For demo day, in case you need a binary that runs without the source files present:
 
```bash
pip install pyinstaller
pyinstaller --onefile --add-data "assets;assets" main.py
```
(On Mac/Linux, use `assets:assets` — colon instead of semicolon.)

## Web build (GitHub Pages)

The playable build lives on the `gh-pages` branch and is served at
<https://hashim-69.github.io/tower-defense-game/>.

`web/index.html` is the **source of truth** for the pygbag loader page. It is a
pygbag 0.9.3 template with hand-made changes that a plain `pygbag --build` does
not produce and *will overwrite*:

- the canvas is letterboxed to 16:9 and centred, instead of being stretched to
  the viewport's shape (which distorted the game badly in portrait)
- `touch-action: none` and `overscroll-behavior: none`, so double-tap zoom and
  pull-to-refresh don't eat taps meant for the game
- a portrait "rotate your device" hint, non-interactive so it can never swallow
  the tap pygbag needs to unlock audio
- one coherent viewport meta tag, and dark letterbox bars

To deploy, package the runtime files into the two archives the loader fetches
(`tower.defence.tar.gz` for the web, `tower.defence.apk` for itch.io), each
containing the `.py` files under `assets/` and the audio under `assets/assets/`,
then copy them and `web/index.html` onto `gh-pages`.

Only the `-pygbag.ogg` audio ships to the web: `audio.py` switches extension on
`sys.platform == "emscripten"`. The `.wav` files are desktop-only.
 
## Project structure
 
```
main.py        # window, game loop, top-level state (gold, lives, level index)
settings.py    # all constants — grid size, colors, stats, levels, rendering config
grid.py        # tile map, path baking, grid<->pixel conversion, baked background
enemy.py       # Enemy class — movement, slow-debuff handling, drawing
tower.py       # Tower class — targeting, aim rotation, stats, placement rules
projectile.py  # Projectile class — homing movement, hit detection, splash/slow
waves.py       # level 1 wave definitions
spawner.py     # Spawner class — wave queue, spawn timing, level completion
ui.py          # HUD bar, tower-select buttons, build-phase banner
audio.py       # sound loading and playback (degrades to silent if unavailable)
utils.py       # small pixel-drawing primitives
assets/        # sound effects (wav for desktop, ogg for the pygbag build)
```
 
## Design notes
 
- **Low-res-then-scale rendering:** everything draws onto a 320×180 surface, scaled 4x to a 1280×720 window using nearest-neighbor scaling (not smoothscale). This is what keeps blocky primitive shapes looking like deliberate pixel art instead of placeholder rectangles.
- **Fixed path, no pathfinding:** the route is a single baked-in set of waypoints. A* or dynamic routing would add real complexity for zero gameplay payoff at this scope.
- **Color is data-linked:** every entity's fill color is read directly from its stats dict — the visual identity and the balance numbers can never drift out of sync.
- **Silhouette over detail:** each tower/enemy is built around one exaggerated shape feature (barrel length/width, spike cluster, body size) rather than fine detail, since that's what actually reads at this resolution.
- **Bake anything static:** the tile map, the rotated tower barrels and the HUD text are all rendered once and reused. Nothing that hasn't changed gets re-rasterised on a frame.

## Intentionally out of scope
 
These were deliberate cuts to keep the project finishable, not oversights:
 
- Pathfinding or dynamically generated maps
- More than 3 tower types, 2 enemy types, or 4 waves
- Tower upgrades, tower selling, or any economy beyond gold-in/gold-out
- Multiplayer, save/load, difficulty settings, restart-without-relaunch
- Animated sprite sheets (a hit-flash substitutes for animation)

## Author
 
Built by Hashim.
