# PRD — Micro Tower Defense (Hackathon Build)

## 1. Overview
A small, complete, pixel-art tower defense game built in Python/pygame for a software-category hackathon. Single fixed map, one path, 3 tower types, 2 enemy types, 4 waves. Scope is deliberately minimal — the goal is a finished, polished, demoable game, not a feature-complete one.

## 2. Goals & constraints
- Built solo, under hackathon time pressure. Every design decision below already trades "interesting" for "shippable."
- Must run as a standalone desktop app (no install steps for a judge beyond opening it, ideally a packaged executable).
- Must be visually readable and understandable within seconds of watching it played — no onboarding/tutorial text.
- No scope creep: anything not explicitly listed in this document is out of scope (see Section 9).

## 3. Core loop
Enemies spawn at the start of the path and walk it toward the player's base. The player spends gold to place towers on buildable tiles along the route; towers auto-target and damage enemies in range. Killing enemies earns gold. Letting enemies reach the end costs a life. Survive 4 escalating waves to win; hit 0 lives to lose.

## 4. Technical stack
- Python 3 + `pygame` (only dependency).
- Rendering: draw everything to a low-res `pygame.Surface` of `320×180`, then `pygame.transform.scale()` (not `smoothscale`) up to a `1280×720` window each frame. This is what produces the crisp pixel-art look.
- 60 FPS, delta-time game loop (`clock.tick(60)/1000`) — no fixed-step assumptions, no `time.sleep`.
- **Critical gotcha to encode:** `pygame.mouse.get_pos()` returns real window coordinates. Every click handler must divide by the scale factor (4) before converting to grid coordinates.

## 5. Game world spec
- Grid: 20 columns × 10 rows, `TILE_SIZE = 16`.
- HUD bar: 20px strip across the top of the low-res surface, above the grid.
- Path: one fixed, axis-aligned snake route baked into the map as a list of grid waypoints — no pathfinding algorithm, ever (see non-goals).
- Tiles are either `path` (enemies walk here, not buildable) or `buildable` (towers can be placed here, if unoccupied and affordable).

## 6. Entities

### Towers
| Type | Cost | Damage | Range | Cooldown | Special | Role |
|---|---|---|---|---|---|---|
| Gunner | 50 | 10 | 60 | 0.3s | — | Fast single-target DPS |
| Cannon | 100 | 20 | 50 | 1.2s | Splash radius 24 | Area damage on clustered enemies |
| Frost | 75 | 4 | 55 | 0.8s | Slows target to 50% speed for 2s | Crowd control, low damage |

### Enemies
| Type | HP | Speed | Reward | Role |
|---|---|---|---|---|
| Walker | 30 | 40 | 5 gold | Basic, appears every wave |
| Armored | 90 | 25 | 12 gold | Tougher, introduced wave 3 |

Towers auto-target the closest enemy in range. Cannon damages everything within its splash radius of the impact point. Frost applies a slow debuff that refreshes on repeat hits rather than stacking.

## 7. Wave system
4 hardcoded waves, increasing in size and introducing the armored enemy partway through:
1. 8× Walker
2. 12× Walker
3. 6× Walker + 4× Armored
4. 8× Walker + 8× Armored

A wave is "cleared" only when its spawn queue is empty **and** no enemies from it remain alive — not merely when spawning finishes. A 4-second delay separates cleared waves before the next one starts.

## 8. Economy & win/lose
- Start: 150 gold, 10 lives.
- Lives -1 per enemy that reaches the end of the path.
- 0 lives → game over.
- Wave 4 cleared → win.

## 9. Out of scope (non-goals)
Explicitly do not implement any of the following — they are common "obvious next steps" that would blow the time budget:
- Pathfinding / dynamically generated maps (path is fixed and baked in)
- More than 3 tower types or 2 enemy types
- More than 4 waves, or randomized/infinite wave generation
- Multiplayer, save/load, settings menu, difficulty levels
- Tower upgrades, tower selling, or any economy beyond gold-in/gold-out
- Animated sprites or sprite sheets — static shapes with a simple hit-flash is sufficient (see Section 10)
- Any UI beyond the HUD bar and 3 tower-select buttons described below

## 10. Visual & art direction
Style: blocky, flat-color pixel art, rendered natively at low resolution (don't draw at a large size and scale down — design at the actual in-game pixel size).

Shading convention: every entity uses 3 tones — a darker outline/back color, the main fill color, and a small lighter highlight square in the upper-left corner (consistent light source). This alone is what makes flat rectangles read as "pixel art" rather than placeholder shapes.

Design principle: silhouette over detail. At this resolution, one exaggerated defining shape feature communicates more than fine detail. Concretely:
- **Gunner** — narrow, tall barrel on a compact base. Reads as fast/precise.
- **Cannon** — short, wide barrel on a bulkier base. Reads as heavy/area.
- **Frost** — three jagged crystal spikes instead of a barrel. Reads as elemental/control.
- **Walker** — small, three-tier stacked-rect "blob" silhouette. Reads as basic/weak.
- **Armored** — larger rectangular body with two small diamond-shaped studs at the top corners. Reads as tanky/armored.

Color is data-linked, not decorative: each entity's fill color is exactly its `stats['color']` value from the game data (see Section 6 tables), so the visual identity and the underlying balance numbers never drift apart.

## 11. Audio
4 short SFX, triggered at: tower fires (`shoot.wav`), projectile lands (`hit.wav`), enemy dies (`death.wav`), new wave starts (`wave_start.wav`). Generated quickly via jsfxr or any free SFX source — not a focus area.

## 12. File/code architecture
```
main.py        # window, game loop, top-level state (gold, lives, wave index)
settings.py    # every constant in this document
grid.py        # tile map, path baking, grid<->pixel conversion
enemy.py       # Enemy class, movement, slow-debuff handling
tower.py       # Tower class, targeting, stats, placement validation
projectile.py  # Projectile class, hit detection, splash/slow application
waves.py       # WAVES data + Spawner class
ui.py          # HUD bar, tower-select buttons, win/lose/wave-cleared text
assets/        # fonts, sfx
```

## 13. Definition of done
- [ ] Game launches to a playable state with no errors, runs at a stable 60 FPS.
- [ ] All 3 towers placeable, each behaving per Section 6 (single-target, splash, slow).
- [ ] All 4 waves play out correctly, armored enemies appear starting wave 3.
- [ ] Gold and lives update correctly; game-over and win screens both trigger at the right moment.
- [ ] HUD shows gold, lives, and wave number live; tower-select buttons work.
- [ ] Audio plays on all 4 trigger events.
- [ ] Packaged into a standalone executable that runs without the source files present.

## 14. Implementation reference
A full step-by-step build sequence (12 ordered prompts, each carrying the exact numbers from this document) already exists in `tower_defense_build_prompts.md` — follow that file in order for actual implementation; this PRD is the source of truth for *what* is being built and *why* each scope line was drawn where it was.
