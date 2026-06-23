# Tower Economy Extension — Build Prompts 3

Assumes both `tower_defense_build_prompts.md` (base game, 14 prompts) and `prompts2.md` (multi-level extension, 7 prompts) are already built. Nothing here rewrites either — this only adds new pricing, purchase limits, and a HUD display on top of what's already there.

**What this adds:**
- Cannon and Frost get repriced upward — Frost becomes the expensive, scarce option
- Hard per-type purchase limits for the whole game: 4 Gunners, 2 Cannons, 1 Frost
- Each tower-select button shows live cost and remaining allowance, greying out once maxed

**Design note, read before building:** these purchase limits are tracked **per game**, not per level — they do not reset when `prompts2.md` Prompt 4 clears towers between levels. That means your single Frost purchase is burned the moment you place it anywhere, even though it disappears on the next level transition. That's intentional here (it forces a real decision about which level deserves your one Frost), not a bug — if you'd rather it refund a slot on level clear, say so and the design changes, but build it as written below first.

---

## Prompt 1 — Reprice Cannon and Frost

In `tower.py`, update the existing `TOWER_STATS` dict (no other fields change):

```python
TOWER_STATS = {
    'gunner': {'cost': 50,  ...},   # unchanged
    'cannon': {'cost': 250, ...},   # was 100
    'frost':  {'cost': 400, ...},   # was 75
}
```

**Done when:** placing a Cannon or Frost deducts the new cost; Gunner cost is unaffected.

---

## Prompt 2 — Per-type purchase limits

Add to `settings.py`:
```python
TOWER_PURCHASE_LIMITS = {'gunner': 4, 'cannon': 2, 'frost': 1}
```

In `main.py`, add a counter alongside your existing gold/lives state — declared once at game start, **not** reset on level transitions:
```python
tower_purchase_counts = {'gunner': 0, 'cannon': 0, 'frost': 0}
```

Extend your existing placement-validation function (`is_valid_placement()` if you built it per `prompts2.md` Prompt 3, or the inline checks in your `MOUSEBUTTONDOWN` handler if you didn't) with one more condition, checked alongside tile/occupancy/gold/spacing:
```python
if purchase_counts[tower_type] >= TOWER_PURCHASE_LIMITS[tower_type]:
    return False  # or: skip placement, same as any other failed check
```

On a successful placement, increment the count right where you already deduct gold:
```python
tower_purchase_counts[selected_tower_type] += 1
```

**Done when:** you're hard-blocked from placing a 5th Gunner, a 3rd Cannon, or a 2nd Frost — across the entire game, regardless of which level you're on or how much gold you have.

---

## Prompt 3 — Show cost and remaining count on each tower button

In `ui.py`, wherever you draw the three tower-select buttons (HUD during normal play, and the build-phase screen if you built `prompts2.md` Prompt 5), add two lines of small text per button instead of just the color swatch:

```python
cost_text = f"{TOWER_STATS[t]['cost']}g"
remaining = TOWER_PURCHASE_LIMITS[t] - tower_purchase_counts[t]
remaining_text = f"{remaining}/{TOWER_PURCHASE_LIMITS[t]} left"
```

Render `cost_text` and `remaining_text` under or beside each button's swatch, same small font as the rest of the HUD.

When `remaining <= 0` for a type: draw that button at reduced brightness (e.g. halve each RGB channel) and skip it entirely in your placement click-handling, so a maxed-out tower can't be selected at all, not just rejected after clicking the grid.

**Done when:** every tower button always shows its current cost and how many are left this game, updates live the instant one is placed, and a maxed-out button is visibly greyed out and unselectable.
