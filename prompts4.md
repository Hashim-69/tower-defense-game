# New Enemies Extension — Build Prompts 4

Assumes `tower_defense_build_prompts.md` (base game), `prompts2.md` (levels), and `prompts3.md` (tower economy) are already built. Nothing here rewrites any of them — two new enemy types are added to the existing `ENEMY_STATS` dict and `Enemy.draw()` if/elif chain, and only `WAVES_LEVEL2`/`WAVES_LEVEL3` get new enemy entries mixed in. Level 1 is untouched — these two enemies never appear there.

**Design intent:** Walker and Armored sit in the middle of the stat range. These two sit at the extremes, and exist specifically to make Frost and Cannon worth their new higher prices:
- **Runner** — fast, fragile, low reward. Counters towers that fire slowly (Cannon's 1.2s cooldown struggles to land a hit before it's past). Frost's slow is the clean answer.
- **Brute** — slow, huge HP pool, high reward. A damage sponge that punishes single-target Gunner spam and rewards Cannon's splash or sustained focus fire.

---

## Prompt 1 — Add stats for both new types

Extend the existing `ENEMY_STATS` dict in `enemy.py` with two new keys (same shape as `walker`/`armored` — `color` is the fill):

```python
ENEMY_STATS['runner'] = {
    'hp': 18, 'speed': 70, 'reward': 8,
    'color': (235, 195, 60), 'outline_color': (141, 117, 36), 'highlight_color': (245, 225, 140),
}
ENEMY_STATS['brute'] = {
    'hp': 180, 'speed': 18, 'reward': 25,
    'color': (110, 70, 150), 'outline_color': (60, 38, 82), 'highlight_color': (170, 140, 200),
}
```

Because the per-level `hp_mult`/`speed_mult` scaling from `prompts2.md` Prompt 2 reads generically from `ENEMY_STATS[enemy_type]`, both new types automatically scale correctly on levels 2 and 3 — nothing else needs to change for that to work.

**Done when:** `Enemy('runner')` and `Enemy('brute')` instantiate without errors and report the stats above.

---

## Prompt 2 — Sprite geometry

Add two more branches to the if/elif chain in `Enemy.draw()` (from `tower_defense_build_prompts.md` Prompt 13), using the same `draw_part`/`draw_poly` helpers and the same "offset from `pos`" convention. Draw order: outline first, then fill/details, highlight last.

**Runner** — low, wide, finned:
1. outline rect `(-7,-5,14,8)` → outline_color
2. top tier rect `(-4,-4,8,2)` → fill
3. middle tier rect `(-6,-2,12,3)` → fill
4. bottom tier rect `(-4,1,8,2)` → fill
5. fin polygons via `draw_poly` (fill only): `[(-7,-1),(-10,0),(-7,1)]` and `[(7,-1),(10,0),(7,1)]`
6. highlight rect `(-4,-3,3,2)` → highlight_color
7. eye rects `(-2,-3,1,1)` and `(1,-3,1,1)` → EYE_COLOR

**Brute** — tall, bulky, side-plated:
1. outline rect `(-9,-9,18,18)` → outline_color
2. bump (head) rect `(-4,-9,8,6)` → fill
3. body rect `(-7,-5,14,12)` → fill
4. stud polygons via `draw_poly` (fill only): `[(-7,-5),(-4,-2),(-7,1),(-10,-2)]` and `[(7,-5),(10,-2),(7,1),(4,-2)]`
5. highlight rect `(-6,-3,5,5)` → highlight_color
6. eye rects `(-2,-7,1,1)` and `(1,-7,1,1)` → EYE_COLOR

**Done when:** placing one of each manually renders the low finned Runner silhouette and the bulky studded Brute silhouette, both distinguishable at a glance from Walker and Armored.

---

## Prompt 3 — Wire into levels 2 and 3 only

Replace `WAVES_LEVEL2` and `WAVES_LEVEL3` from `prompts2.md`'s constants with these updated versions — same shape, just with `runner`/`brute` mixed into the existing walker/armored counts. `WAVES` (level 1) is not touched.

```python
WAVES_LEVEL2 = [
    {"enemies": ["walker"]*10,                                              "interval": 0.9},
    {"enemies": ["walker"]*8  + ["armored"]*4  + ["runner"]*4,              "interval": 0.8},
    {"enemies": ["walker"]*10 + ["armored"]*6  + ["runner"]*6,              "interval": 0.7},
    {"enemies": ["walker"]*8  + ["armored"]*10 + ["runner"]*4 + ["brute"]*1, "interval": 0.6},
    {"enemies": ["walker"]*12 + ["armored"]*12 + ["runner"]*6 + ["brute"]*2, "interval": 0.5},
]

WAVES_LEVEL3 = [
    {"enemies": ["walker"]*12 + ["armored"]*6  + ["runner"]*6,               "interval": 0.8},
    {"enemies": ["walker"]*10 + ["armored"]*10 + ["runner"]*8  + ["brute"]*1, "interval": 0.7},
    {"enemies": ["walker"]*14 + ["armored"]*10 + ["runner"]*8  + ["brute"]*2, "interval": 0.6},
    {"enemies": ["walker"]*10 + ["armored"]*16 + ["runner"]*10 + ["brute"]*2, "interval": 0.55},
    {"enemies": ["walker"]*16 + ["armored"]*16 + ["runner"]*10 + ["brute"]*3, "interval": 0.5},
    {"enemies": ["walker"]*14 + ["armored"]*20 + ["runner"]*12 + ["brute"]*4, "interval": 0.45},
]
```

No changes needed to `Spawner`, `LEVELS`, or anything in `prompts3.md` — they already work generically off whatever enemy type strings appear in a wave's list.

**Done when:** level 1 plays exactly as before (walker/armored only); levels 2 and 3 spawn visible Runners and Brutes alongside walker/armored, with Brutes only starting from each level's 4th wave onward.
