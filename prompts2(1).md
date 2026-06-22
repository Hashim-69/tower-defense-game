# Multi-Level Extension — Build Prompts 2

Assumes the base game from `tower_defense_build_prompts.md` (all 14 prompts) is already built and pushed. Nothing here rewrites that logic — every prompt below is a small, targeted addition to a specific existing file, or a new file. Apply in order.

**What this adds:**
- 3 levels, each with its own map layout, its own (longer) wave list, and tougher enemy stats
- A build-phase break between levels — no timer, you place towers on the new map, then click Continue
- A minimum spacing rule so towers can't be placed right next to each other

Default scope: **3 levels**. Adding a 4th later is just appending one more entry to the `LEVELS` list in the same shape — nothing else changes.

---

## New constants (add to `settings.py` — don't remove anything existing)

```python
MIN_TOWER_DISTANCE = 24  # low-res px; blocks placement within ~1.5 tiles of another tower

# Level 1 reuses the existing WAYPOINTS_GRID and WAVES from prompts.md unchanged.

WAYPOINTS_GRID_2 = [(0,1), (16,1), (16,3), (4,3), (4,6), (16,6), (16,8), (19,8)]
WAYPOINTS_GRID_3 = [(0,0), (19,0), (19,2), (1,2), (1,4), (19,4), (19,6), (1,6), (1,9), (19,9)]

WAVES_LEVEL2 = [
    {"enemies": ["walker"]*10,                          "interval": 0.9},
    {"enemies": ["walker"]*8  + ["armored"]*4,          "interval": 0.8},
    {"enemies": ["walker"]*10 + ["armored"]*6,          "interval": 0.7},
    {"enemies": ["walker"]*8  + ["armored"]*10,         "interval": 0.6},
    {"enemies": ["walker"]*12 + ["armored"]*12,         "interval": 0.5},
]

WAVES_LEVEL3 = [
    {"enemies": ["walker"]*12 + ["armored"]*6,          "interval": 0.8},
    {"enemies": ["walker"]*10 + ["armored"]*10,         "interval": 0.7},
    {"enemies": ["walker"]*14 + ["armored"]*10,         "interval": 0.6},
    {"enemies": ["walker"]*10 + ["armored"]*16,         "interval": 0.55},
    {"enemies": ["walker"]*16 + ["armored"]*16,         "interval": 0.5},
    {"enemies": ["walker"]*14 + ["armored"]*20,         "interval": 0.45},
]

LEVELS = [
    {"path": WAYPOINTS_GRID,   "waves": WAVES,        "enemy_mult": {"hp": 1.0, "speed": 1.0}},
    {"path": WAYPOINTS_GRID_2, "waves": WAVES_LEVEL2,  "enemy_mult": {"hp": 1.4, "speed": 1.15}},
    {"path": WAYPOINTS_GRID_3, "waves": WAVES_LEVEL3,  "enemy_mult": {"hp": 1.8, "speed": 1.3}},
]
```

Gold and lives carry over between levels — they're not reset. Towers do **not** carry over: each level has a different layout, so placed towers from the previous level's map are cleared (see Prompt 5).

---

## Prompt 1 — Parameterize the grid/path builder for multiple layouts

In `grid.py`, give `build_tile_map()` a parameter instead of always reading the single global waypoints list:

```python
def build_tile_map(waypoints=WAYPOINTS_GRID):
    # exact same body as before, just walk `waypoints` instead of the hardcoded global
    ...
```

Default value keeps every existing call in the base game working unchanged. `grid_to_pixel()` is untouched.

**Done when:** calling `build_tile_map(WAYPOINTS_GRID_2)` produces a tile map tracing the level-2 path correctly, and existing no-argument calls still produce the original level-1 map.

---

## Prompt 2 — Enemy stat scaling per level

In `enemy.py`, add two optional parameters to `Enemy.__init__`:

```python
def __init__(self, enemy_type, waypoints=WAYPOINTS_GRID, hp_mult=1.0, speed_mult=1.0):
    ...
    self.hp = ENEMY_STATS[enemy_type]['hp'] * hp_mult
    self.base_speed = ENEMY_STATS[enemy_type]['speed'] * speed_mult  # base_speed already exists from the Frost-slow logic
    self.path = [grid_to_pixel(col, row) for col, row in waypoints]
    ...
```

Defaults (`1.0`, `1.0`, and the original `WAYPOINTS_GRID`) mean any existing call to `Enemy('walker')` behaves exactly as it did before. Nothing else in `Enemy` changes — movement, slow-debuff, and drawing logic are untouched.

**Done when:** `Enemy('armored', hp_mult=1.4, speed_mult=1.15)` produces an enemy with 1.4x the base armored HP and 1.15x the base speed, while a plain `Enemy('walker')` call is unaffected.

---

## Prompt 3 — Minimum tower spacing

In `tower.py`, wrap the placement checks from the base game's Prompt 6 into one reusable function — it's called from two places now (normal placement and the new build phase), so it needs to live in one spot instead of staying inline:

```python
def is_valid_placement(col, row, tower_type, tile_map, occupied, gold, towers_group):
    if tile_map[col][row] != 'buildable':
        return False
    if (col, row) in occupied:
        return False
    if gold < TOWER_STATS[tower_type]['cost']:
        return False
    candidate_pos = grid_to_pixel(col, row)
    for tower in towers_group:
        if candidate_pos.distance_to(tower.pos) < MIN_TOWER_DISTANCE:
            return False
    return True
```

Replace the inline checks in your `MOUSEBUTTONDOWN` handler with a call to this function.

**Done when:** placing a tower directly adjacent to another tower (same or neighboring tile) is rejected even though the tile itself is buildable and unoccupied; placing a couple of tiles further away still works.

---

## Prompt 4 — Level state machine

This replaces the base game's "wave 4 clears → win" logic (from prompts.md Prompt 9) with a level-aware version. Add `current_level_index = 0` and a `game_state` variable (`'playing'`, `'build_phase'`, `'game_over'`, `'game_won'`) — this can replace the separate `game_over`/`game_won` booleans, or sit alongside them, your call.

In `spawner.py`, change the constructor to take the level's data directly instead of the hardcoded global:

```python
def __init__(self, waves_list, enemy_mult=None):
    self.waves = waves_list
    self.enemy_mult = enemy_mult or {"hp": 1.0, "speed": 1.0}
    self.current_wave_index = 0
    self.spawn_queue = self.waves[0]["enemies"].copy()
    self.interval = self.waves[0]["interval"]
    self.spawn_timer = 0
    self.delay_timer = 0
    self.level_complete = False
```

In `update()`, when spawning an enemy, pass the multiplier through:
```python
enemy = Enemy(enemy_type, waypoints=current_level_path, hp_mult=self.enemy_mult['hp'], speed_mult=self.enemy_mult['speed'])
```

And change the "what happens when the last wave clears" branch — instead of assuming there's always a next wave, check against this level's own wave count:
```python
if self.current_wave_index >= len(self.waves) - 1:
    self.level_complete = True  # let main.py decide what happens next
else:
    # unchanged: advance to the next wave within this level after the delay
    ...
```

In `main.py`, each frame, check the active spawner's flag:
```python
if spawner.level_complete:
    if current_level_index + 1 >= len(LEVELS):
        game_state = 'game_won'
    else:
        current_level_index += 1
        towers_group.empty()
        occupied.clear()
        tile_map = build_tile_map(LEVELS[current_level_index]['path'])
        game_state = 'build_phase'
```

**Done when:** clearing level 1's final wave clears all towers from the screen, loads the level-2 layout, and switches to `build_phase` instead of ending the game; clearing level 3's final wave triggers `game_won`.

---

## Prompt 5 — Build-phase UI and Continue button

In `ui.py`, while `game_state == 'build_phase'`: render the new (empty) tile map and path as usual, keep the existing gold/lives HUD elements live, and draw a banner: `f"LEVEL {current_level_index + 1} — BUILD PHASE"`. Draw a `CONTINUE` button (rect + text, same font/style as the GAME OVER/YOU WIN screens) somewhere clear of the grid.

Placement clicks during `build_phase` go through the same `is_valid_placement()` check from Prompt 3 — no special-casing needed there.

On a click inside the Continue button's rect:
```python
spawner = Spawner(LEVELS[current_level_index]['waves'], LEVELS[current_level_index]['enemy_mult'])
game_state = 'playing'
```

**Done when:** during `build_phase` you can place towers on the new layout same as normal play, gold deducts correctly, and clicking Continue starts that level's first wave spawning immediately.

---

## Prompt 6 — Full playthrough check

Play start to finish. Confirm: level 1 behaves exactly as it did before this extension (same path, same 4 waves, same difficulty); after its last wave, towers clear and you land in level 2's build phase on the new layout; placing towers too close together is blocked; clicking Continue starts level 2's 5 waves with visibly tougher (higher HP, faster) enemies; the same pattern repeats into level 3; clearing level 3 triggers the win screen.

**Done when:** all of the above holds in one uninterrupted run, and lives/gold correctly persisted across all three levels the whole way through.
