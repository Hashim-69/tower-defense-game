# Micro Tower Defense
 
A small, complete, pixel-art tower defense game built solo in Python/pygame.
 
One fixed map. Three towers. Two enemy types. Four waves. Built to be finished, not feature-complete.
 
## Overview
 
Enemies spawn at the edge of the map and walk a fixed snake-shaped path toward your base. You place towers along the route to kill them before they get there. Kill enemies for gold, spend gold on more towers, survive four escalating waves to win. Lose all your lives and it's game over.
 
Rendered at a native low resolution and scaled up 4x with nearest-neighbor scaling for a crisp, intentional pixel-art look — not blurry placeholder shapes.
 
## Features
 
- **3 tower types**, each with a distinct role and a distinct silhouette (no two towers look or play alike)
- **2 enemy types**, including a tougher armored variant introduced mid-game
- **4 hardcoded waves** with increasing difficulty
- **Hand-designed pixel sprites** built from layered primitive shapes (no external art assets) — color-matched directly to each entity's underlying stats
- **Towers visually track their target** — barrels and spike clusters rotate to face whatever enemy they're currently locked onto, and hold their last facing when nothing's in range
- **Full economy loop** — gold in from kills, gold out on placement, real tradeoffs between tower types
- **Audio feedback** on every core action — shoot, hit, death, wave start

## How to play
 
**Objective:** survive all 4 waves without losing all 10 lives.
 
**Controls:**
- Click a tower button in the HUD to select which tower type you're placing
- Click an empty (non-path) tile on the grid to place it, if you can afford it
- Towers fire automatically — no further input needed once placed

### Towers
 
| Tower | Cost | Damage | Range | Cooldown | Role |
|---|---|---|---|---|---|
| Gunner | 50g | 10 | 60 | 0.3s | Fast, single-target DPS |
| Cannon | 100g | 20 | 50 | 1.2s | Splash damage (radius 24) — best against clustered enemies |
| Frost | 75g | 4 | 55 | 0.8s | Low damage, slows target to 50% speed for 2s — crowd control |
 
### Enemies
 
| Enemy | HP | Speed | Gold reward | Notes |
|---|---|---|---|---|
| Walker | 30 | 40 | 5g | Basic enemy, present in every wave |
| Armored | 90 | 25 | 12g | Tougher, introduced starting wave 3 |
 
### Waves
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
 
## Project structure
 
```
main.py        # window, game loop, top-level state (gold, lives, wave index)
settings.py    # all constants — grid size, colors, rendering config
grid.py        # tile map, path baking, grid<->pixel conversion
enemy.py       # Enemy class — movement, slow-debuff handling, drawing
tower.py       # Tower class — targeting, aim rotation, stats, placement
projectile.py  # Projectile class — homing movement, hit detection, splash/slow
waves.py       # wave definitions + Spawner class
ui.py          # HUD bar, tower-select buttons, win/lose/wave-cleared text
assets/        # font, sound effects
```
 
## Design notes
 
- **Low-res-then-scale rendering:** everything draws onto a 320×180 surface, scaled 4x to a 1280×720 window using nearest-neighbor scaling (not smoothscale). This is what keeps blocky primitive shapes looking like deliberate pixel art instead of placeholder rectangles.
- **Fixed path, no pathfinding:** the route is a single baked-in set of waypoints. A* or dynamic routing would add real complexity for zero gameplay payoff at this scope.
- **Color is data-linked:** every entity's fill color is read directly from its stats dict — the visual identity and the balance numbers can never drift out of sync.
- **Silhouette over detail:** each tower/enemy is built around one exaggerated shape feature (barrel length/width, spike cluster, body size) rather than fine detail, since that's what actually reads at this resolution.

## Intentionally out of scope
 
These were deliberate cuts to keep the project finishable, not oversights:
 
- Pathfinding or dynamically generated maps
- More than 3 tower types, 2 enemy types, or 4 waves
- Tower upgrades, tower selling, or any economy beyond gold-in/gold-out
- Multiplayer, save/load, difficulty settings
- Animated sprite sheets (a hit-flash substitutes for animation)

## Author
 
Built by Hashim.
