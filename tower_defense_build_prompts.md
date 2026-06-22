# Micro Tower Defense — Build Prompts (Pygame)

Use these in order. Each one is self-contained — it carries every constant and number it needs, so you can feed it to a coding tool or just code straight from it without flipping back and forth. Don't skip the order: step 7 depends on step 6's occupied-tile tracking, step 8 depends on step 7's projectile system, etc.

---

## Constants Reference (single source of truth — put this in `settings.py`)

**Rendering**
- `LOW_RES = (320, 180)` — all game logic happens in this coordinate space
- `SCALE = 4` → real window `WINDOW_SIZE = (1280, 720)`
- `FPS = 60`
- `BG_COLOR = (30, 30, 40)`
- `HUD_COLOR = (20, 20, 25)`
- `HUD_HEIGHT = 20` (px, low-res space, sits at the top)

**IMPORTANT GOTCHA:** `pygame.mouse.get_pos()` returns *real window* coordinates (1280×720). Always divide by `SCALE` before using mouse position for any grid/tower/click logic. Forgetting this is the #1 bug source in a scaled-render setup.

**Grid**
- `TILE_SIZE = 16`
- `GRID_COLS = 20`, `GRID_ROWS = 10` (fills the 320×160 area below the HUD bar)
- `grid_to_pixel(col, row)` → `(col*TILE_SIZE + TILE_SIZE/2, HUD_HEIGHT + row*TILE_SIZE + TILE_SIZE/2)`

**Path (grid coordinates, axis-aligned snake)**
```python
WAYPOINTS_GRID = [(0,2), (15,2), (15,5), (3,5), (3,8), (19,8)]
```
Enters left edge at row 2, exits right edge at row 8. All segments are straight horizontal/vertical — no diagonal math needed.

**Economy**
- `START_GOLD = 150`
- `START_LIVES = 10`
- Inter-wave delay: `4.0` seconds after a wave fully clears

**Tower stats**
| Type | Cost | Damage | Range | Cooldown | Proj Speed | Extra | Color |
|---|---|---|---|---|---|---|---|
| Gunner | 50 | 10 | 60 | 0.3s | 220 | — | (80,200,120) |
| Cannon | 100 | 20 | 50 | 1.2s | 140 | splash_radius=24 | (220,140,60) |
| Frost | 75 | 4 | 55 | 0.8s | 200 | slow_mult=0.5, slow_duration=2.0s | (100,180,230) |

**Enemy stats**
| Type | HP | Speed | Reward | Radius | Color |
|---|---|---|---|---|---|
| Walker | 30 | 40 | 5 | 4 | (220,60,60) |
| Armored | 90 | 25 | 12 | 5 | (150,40,40) |

**Waves**
```python
WAVES = [
    {"enemies": ["walker"]*8,                         "interval": 1.0},
    {"enemies": ["walker"]*12,                         "interval": 0.8},
    {"enemies": ["walker"]*6 + ["armored"]*4,          "interval": 0.7},
    {"enemies": ["walker"]*8 + ["armored"]*8,          "interval": 0.55},
]
```
A wave is "cleared" when its spawn queue is empty **and** zero enemies from it remain alive on screen — not just when spawning finishes.

---

## Prompt 1 — Window, Game Loop, Pixel-Scale Rendering

Set up `settings.py` with every constant above. In `main.py`: open a real window at `WINDOW_SIZE`, create a second `pygame.Surface(LOW_RES)` called `game_surface` — all drawing happens on this surface, never directly on the real screen. Main loop: `dt = clock.tick(FPS)/1000`, handle `pygame.QUIT`, fill `game_surface` with `BG_COLOR`, then at the end of the frame `scaled = pygame.transform.scale(game_surface, WINDOW_SIZE)` (use `scale`, not `smoothscale` — smoothscale blurs the pixel look), blit to the real screen, `pygame.display.flip()`.

**Done when:** window opens at 1280×720, fills with the background color, closes cleanly on the X button, no blur/anti-aliasing artifacts.

---

## Prompt 2 — Grid + Path Rendering

In `grid.py`: write `build_tile_map()` that returns a `GRID_COLS × GRID_ROWS` 2D list of `'path'` / `'buildable'` strings. Generate it by walking each consecutive pair in `WAYPOINTS_GRID` — since every segment is axis-aligned, just step through the row range (if same col) or col range (if same row) between the two points and mark each as `'path'`. Everything else defaults to `'buildable'`.

Write `grid_to_pixel(col, row)` exactly as defined in the constants section. Write `draw_grid(surface, tile_map)`: loop every cell, draw a filled rect — path tiles `(90,70,50)`, buildable tiles `(40,70,40)`. Draw the HUD bar as a separate rect, full width, height `HUD_HEIGHT`, color `HUD_COLOR`, on top.

**Done when:** the snake path is visibly traced from the left edge to the right edge through both bends, matches `WAYPOINTS_GRID`, doesn't double back on itself oddly.

---

## Prompt 3 — Enemy Movement Along Path

In `enemy.py`: `Enemy(pygame.sprite.Sprite)`. Constructor takes `enemy_type`, pulls stats from a dict (`hp`, `speed`, `reward`, `color`, `radius`) keyed by `'walker'`/`'armored'`. Precompute `self.path` as the list of pixel-space waypoints via `grid_to_pixel` over every entry in `WAYPOINTS_GRID`. `self.pos = pygame.Vector2(self.path[0])`, `self.waypoint_index = 1`.

`update(dt)`: target = `self.path[self.waypoint_index]`. If `self.pos.distance_to(target) <= self.speed * dt`: snap `self.pos = pygame.Vector2(target)`, increment `waypoint_index`; if that now exceeds the last index, set `self.reached_end = True`. Otherwise: `direction = (target - self.pos).normalize()`, `self.pos += direction * self.speed * dt`.

`draw(surface)`: `pygame.draw.circle(surface, self.color, self.pos, self.radius)`.

For now, in `main.py`, manually spawn exactly one `Enemy('walker')` to test.

**Done when:** the enemy follows every turn of the path with no jitter, no overshoot past a corner, and disappears (or flags `reached_end`) exactly at the final waypoint.

---

## Prompt 4 — Wave Spawner

In `waves.py`: paste the `WAVES` list from the constants section. In `spawner.py`: `Spawner` class holding `current_wave_index = 0`, `spawn_timer = 0`, `spawn_queue = WAVES[0]["enemies"].copy()`, `interval = WAVES[0]["interval"]`, `delay_timer = 0` (counts down between waves).

`update(dt, enemy_group)`:
- If `spawn_queue` is non-empty: `spawn_timer -= dt`; when `spawn_timer <= 0`: pop the first enemy type off the queue, create an `Enemy`, add to `enemy_group`, reset `spawn_timer = interval`.
- If `spawn_queue` is empty **and** `enemy_group` is empty: the wave is cleared. Count up `delay_timer`; once it passes `4.0`s, advance `current_wave_index`. If that exceeds `3` (i.e. wave 4 was just cleared), this is the win condition — just set a flag for now (`Prompt 9` wires the actual win screen). Otherwise load the next wave's queue/interval and reset `delay_timer = 0`.

**Done when:** running the game with no towers placed spawns 8 walkers roughly 1s apart for wave 1, and all of them reach the end (confirms `enemy_group` drains correctly with nothing blocking them).

---

## Prompt 5 — Lives & Game Over

Track `lives = START_LIVES`, `gold = START_GOLD`, `game_over = False`, `game_won = False` — either as module-level state or a small `GameState` class, your call.

Change `Enemy.update` so reaching the end sets `self.leaked = True` instead of self-killing. In the main loop, each frame: scan `enemy_group` for any sprite with `leaked == True`, decrement `lives` for each one found, then `kill()` it explicitly.

If `lives <= 0`: set `game_over = True`. While `game_over`, stop updating enemies/towers/spawner — just keep rendering. Draw "GAME OVER" centered, using `pygame.font.Font` (Press Start 2P once you have it, default font is fine for now) at size ~16, red.

**Done when:** letting walkers leak through unopposed drops lives to 0, GAME OVER renders, and gameplay visibly freezes (no more movement or spawns).

---

## Prompt 6 — Tower Placement (Visual Only)

In `tower.py`: `TOWER_STATS` dict with the three towers' full stat blocks from the constants table. A module-level `selected_tower_type = 'gunner'` for now (Prompt 10 wires real selection). Track placed towers in a `occupied = set()` of `(col, row)` tuples.

On `pygame.MOUSEBUTTONDOWN`: take `pygame.mouse.get_pos()`, **divide both by `SCALE`** to get low-res coordinates, subtract `HUD_HEIGHT` from the y before converting to grid (`col = x // TILE_SIZE`, `row = (y - HUD_HEIGHT) // TILE_SIZE`). Validate: `tile_map[col][row] == 'buildable'`, `(col,row) not in occupied`, `gold >= TOWER_STATS[selected_tower_type]['cost']`. If all true: instantiate `Tower(selected_tower_type, grid_to_pixel(col,row))`, deduct cost from gold, add `(col,row)` to `occupied`, add sprite to a `towers` group.

`Tower(pygame.sprite.Sprite)`: stores `type`, `pos`, `stats`. `draw`: filled circle or square, radius ~6, using `stats['color']`.

**Done when:** clicking valid buildable tiles drops a colored marker and deducts gold each time; clicking path tiles, occupied tiles, or without enough gold does nothing and doesn't crash.

---

## Prompt 7 — Targeting, Shooting, Projectiles, Damage, Currency

Gunner only for now (Cannon/Frost extras come in Prompt 8). In `projectile.py`: `Projectile(pygame.sprite.Sprite)` — constructor takes `start_pos`, `target` (an `Enemy` reference), `stats`. `self.pos = pygame.Vector2(start_pos)`.

`update(dt)`: if `target` is no longer alive (check `target.alive()`), `kill()` immediately. Otherwise `direction = (target.pos - self.pos).normalize()`, `self.pos += direction * stats['proj_speed'] * dt`. If `self.pos.distance_to(target.pos) < 4`: apply `target.hp -= stats['damage']`; if `target.hp <= 0`: `gold += target.reward`, `target.kill()`; either way, `self.kill()` (projectile is consumed on arrival).

In `Tower`, add `self.cooldown_timer = 0`. `update(dt, enemy_group, projectile_group)`: `self.cooldown_timer -= dt`; if `<= 0`, scan `enemy_group`, find the closest enemy with `self.pos.distance_to(enemy.pos) <= self.stats['range']` (track min distance manually — no spatial partitioning needed at this scale); if found, spawn a `Projectile`, add to `projectile_group`, reset `cooldown_timer = self.stats['cooldown']`.

**Done when:** placing a couple of Gunner towers along the path visibly damages and kills enemies before they reach the end (with decent placement), and gold increases on each kill.

---

## Prompt 8 — Cannon & Frost Behaviors

**Cannon:** on impact, instead of damaging only the direct target, loop `enemy_group` and damage every enemy within `stats['splash_radius']` of the *impact point* (the target's position at the moment of the hit) — including the original target.

**Frost:** give `Enemy` a `self.base_speed` (set once at creation, never changes) and `self.slow_timer = 0`. In `Enemy.update`, the effective speed used for movement is `self.base_speed * stats['slow_mult'] if self.slow_timer > 0 else self.base_speed`; decrement `slow_timer` by `dt` each frame. On a Frost hit, apply the (low) direct damage and **reset** `target.slow_timer = stats['slow_duration']` (resetting, not stacking, keeps this from breaking balance if multiple Frost towers hit the same enemy).

**Done when:** Cannon hits visibly damage a whole cluster of enemies at once (test where the path bends and enemies bunch up); Frost-hit enemies are visibly slower than unaffected neighbors.

---

## Prompt 9 — Wave Wiring + Win State

Wire `Spawner`'s wave-4-cleared flag (from Prompt 4) to set `game_won = True` instead of loading a nonexistent 5th wave. While `game_won`, freeze gameplay the same way `game_over` does, and draw a "YOU WIN" screen — same layout as GAME OVER but green text.

During the 4-second inter-wave delay, draw "WAVE CLEARED — NEXT WAVE IN {n}s" using a countdown derived from `delay_timer`.

**Done when:** a full playthrough advances the wave counter 1→4 correctly, and the win screen triggers immediately after wave 4's last enemy is gone — not before, not several seconds late.

---

## Prompt 10 — HUD

In `ui.py`: render the HUD bar's contents — Gold (left), Lives (center-left), "Wave X/4" (center-right) — using a small font (try rendering at size 8–10 directly onto the low-res surface; the 4x scale-up makes it readable without you needing a huge font file).

Add 3 small tower-select buttons (square, ~14px, tower's stat color) somewhere in or near the HUD bar. Clicking one sets `selected_tower_type` (the variable from Prompt 6) and draws a highlight border around whichever is currently active.

**Done when:** gold/lives/wave numbers update live and stay accurate, and clicking each button visibly changes which tower type gets placed on the next grid click.

---

## Prompt 11 — Sound + Visual Polish

`pygame.mixer.init()` at startup. Source or generate 4 short sounds (jsfxr is the fastest route if you're not recording anything): `shoot.wav`, `hit.wav`, `death.wav`, `wave_start.wav`. Play each at its trigger point — tower fires, projectile lands, enemy dies, new wave begins. `pygame.mixer.Sound.play()` is fire-and-forget, won't block your loop.

Optional cheap juice: give `Enemy` a `hit_flash_timer`; on taking damage set it to `0.1`, and while it's `>0` draw the enemy in white instead of its normal color, decrementing each frame. Reads as "hit feedback" for almost no code.

**Done when:** every core action — shoot, hit, death, wave start — has audible feedback, and nothing stutters from the sound calls.

---

## Prompt 12 — PyInstaller Packaging

`pip install pyinstaller`. Build with:
```
pyinstaller --onefile --add-data "assets;assets" main.py
```
(On Mac/Linux, use `assets:assets` — colon, not semicolon.)

Asset paths need to resolve both when running from source and when frozen into the executable — use the standard `sys._MEIPASS` pattern:
```python
import sys, os
def resource_path(rel_path):
    base = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base, rel_path)
```
Use `resource_path(...)` everywhere you currently hardcode an `assets/...` path.

**Done when:** the binary in `dist/` runs standalone from a clean folder with no source files alongside it, and fonts/sounds load without `FileNotFoundError`.

---

## Prompt 13 — Real Sprite Designs for Towers & Enemies

Replaces the placeholder circle/square from Prompt 3 and Prompt 6 with the actual designed pixel sprites — same shape language designed earlier (thin barrel / wide barrel / crystal spikes for towers, small blob / bigger plated body for enemies), resized to fit the real 16px tile grid.

Add `outline_color` and `highlight_color` to every entry in `TOWER_STATS`, and build an equivalent `ENEMY_STATS` dict (the existing `color` field becomes the fill color):

```python
TOWER_STATS = {
    'gunner': {..., 'color': (80,200,120),  'outline_color': (43,111,68),  'highlight_color': (163,232,192)},
    'cannon': {..., 'color': (220,140,60),  'outline_color': (138,85,31),  'highlight_color': (245,200,150)},
    'frost':  {..., 'color': (100,180,230), 'outline_color': (51,110,143), 'highlight_color': (185,226,250)},
}

ENEMY_STATS = {
    'walker':  {..., 'color': (220,60,60), 'outline_color': (140,36,36), 'highlight_color': (242,155,155)},
    'armored': {..., 'color': (150,40,40), 'outline_color': (92,23,23),  'highlight_color': (197,101,101)},
}
EYE_COLOR = (26, 26, 26)
```

Write one shared helper, used by both `Tower.draw()` and `Enemy.draw()`:
```python
def draw_part(surface, cx, cy, rel_x, rel_y, w, h, color):
    pygame.draw.rect(surface, color, (cx + rel_x, cy + rel_y, w, h))

def draw_poly(surface, cx, cy, rel_points, color, outline_color=None):
    pts = [(cx + x, cy + y) for x, y in rel_points]
    pygame.draw.polygon(surface, color, pts)
    if outline_color:
        pygame.draw.polygon(surface, outline_color, pts, 1)
```

Every coordinate below is an **offset from the entity's own `pos`** — already in the 320×180 low-res space, no extra scaling needed (the render pipeline scales the whole frame once). Draw each entity in the listed order: outline first, then fill/details, highlight last.

**Gunner** — thin, tall barrel:
1. outline rect `(-7,-7,14,14)` → outline_color
2. base rect `(-5,-5,10,10)` → fill
3. barrel outline rect `(-3,-14,6,10)` → outline_color
4. barrel rect `(-2,-13,4,8)` → fill
5. highlight rect `(-4,-4,4,4)` → highlight_color

**Cannon** — short, wide barrel:
1. outline rect `(-8,-7,16,14)` → outline_color
2. base rect `(-6,-5,12,10)` → fill
3. barrel outline rect `(-5,-10,10,6)` → outline_color
4. barrel rect `(-4,-9,8,4)` → fill
5. highlight rect `(-5,-4,4,4)` → highlight_color

**Frost** — three crystal spikes instead of a barrel:
1. outline rect `(-7,-7,14,14)` → outline_color
2. base rect `(-5,-5,10,10)` → fill
3. spike polygons via `draw_poly` (fill, with 1px outline_color border):
   - `[(-5,-5), (-2,-5), (-3,-10)]`
   - `[(-2,-5), (2,-5), (0,-12)]`
   - `[(2,-5), (5,-5), (4,-10)]`
4. highlight rect `(-4,-4,4,4)` → highlight_color

**Walker** — small, stacked-tier blob:
1. outline rect `(-5,-6,10,11)` → outline_color
2. top tier rect `(-3,-5,6,3)` → fill
3. middle tier rect `(-4,-2,8,4)` → fill
4. bottom tier rect `(-3,2,6,3)` → fill
5. highlight rect `(-3,-1,3,3)` → highlight_color
6. eye rects `(-2,-4,1,1)` and `(1,-4,1,1)` → EYE_COLOR

**Armored** — bigger body, two corner studs:
1. outline rect `(-7,-7,14,14)` → outline_color
2. body rect `(-5,-5,10,10)` → fill
3. stud polygons via `draw_poly` (fill only, no outline): `[(-4,-8),(-1,-5),(-4,-2),(-7,-5)]` and `[(4,-8),(7,-5),(4,-2),(1,-5)]`
4. highlight rect `(-4,-4,3,3)` → highlight_color
5. eye rects `(-2,0,1,1)` and `(1,0,1,1)` → EYE_COLOR

Update `Enemy.draw()` from Prompt 3 and `Tower.draw()` from Prompt 6 to call these sequences instead of `pygame.draw.circle`/a plain square. Apply this once placement and movement both work — it's a visual swap, not a new system.

**Done when:** towers and enemies render as their distinct designed silhouettes — not generic circles or squares — correctly centered and sized on the grid, with all five types visually distinguishable at a glance.
