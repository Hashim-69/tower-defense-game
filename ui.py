import pygame
from settings import *
import tower

# Tower-button strip. Each entry is a colour swatch with its cost above and its
# remaining count below, laid out to the right of the wave counter.
# The labels used to sit outside the button rect with the main 14pt font, which
# put the cost line at y=-9 (clipped off the top of the screen) and the count
# line at y=18..29, spilling out of the 20px HUD bar onto the play field. They
# are now a smaller font stacked beside the swatch, entirely inside the bar.
BUTTON_SIZE = 14
BUTTON_Y = 3
LABEL_WIDTH = 18
LABEL_GAP = 2
GROUP_WIDTH = BUTTON_SIZE + LABEL_GAP + LABEL_WIDTH
GROUP_GAP = 4
RIGHT_MARGIN = 4
COST_LABEL_Y = 2
COUNT_LABEL_Y = 11

TOWER_ORDER = ('gunner', 'cannon', 'frost')
_strip_x = LOW_RES[0] - RIGHT_MARGIN - (len(TOWER_ORDER) * GROUP_WIDTH + (len(TOWER_ORDER) - 1) * GROUP_GAP)

BUTTONS = [
    {'type': t,
     'rect': pygame.Rect(_strip_x + i * (GROUP_WIDTH + GROUP_GAP), BUTTON_Y, BUTTON_SIZE, BUTTON_SIZE)}
    for i, t in enumerate(TOWER_ORDER)
]

CONTINUE_BUTTON = pygame.Rect(LOW_RES[0] // 2 - 40, LOW_RES[1] // 2 + 10, 80, 24)

_font = None
_label_font = None
_text_cache = {}
_TEXT_CACHE_LIMIT = 512

def get_font():
    global _font
    if _font is None:
        _font = pygame.font.Font(None, 14)
    return _font

def get_label_font():
    global _label_font
    if _label_font is None:
        _label_font = pygame.font.Font(None, 10)
    return _label_font

def render_text(text, color, font=None):
    """Rasterising the HUD every frame cost ~9 font.render calls per frame for
    strings that change a few times a second at most, so results are memoised."""
    font = font or get_font()
    key = (text, color, id(font))
    surf = _text_cache.get(key)
    if surf is None:
        if len(_text_cache) >= _TEXT_CACHE_LIMIT:
            _text_cache.clear()
        surf = font.render(text, False, color)
        _text_cache[key] = surf
    return surf

def _blit_centered(surface, text, color, center):
    text_surf = render_text(text, color)
    surface.blit(text_surf, text_surf.get_rect(center=center))

def draw_hud(surface, state, spawner, purchase_counts, frost_available=True):
    # Gold
    surface.blit(render_text(f"Gold: {state.gold}", (220, 200, 50)), (5, 5))

    # Lives
    surface.blit(render_text(f"Lives: {state.lives}", (220, 80, 80)), (60, 5))

    # Wave or Build Phase
    if state.game_state == 'build_phase':
        _blit_centered(surface, f"LEVEL {state.current_level_index + 1} — BUILD PHASE",
                       (200, 200, 200), (LOW_RES[0] // 2, LOW_RES[1] // 2 - 10))

        pygame.draw.rect(surface, (100, 150, 100), CONTINUE_BUTTON)
        pygame.draw.rect(surface, (200, 255, 200), CONTINUE_BUTTON, 1)
        _blit_centered(surface, "CONTINUE", (255, 255, 255), CONTINUE_BUTTON.center)
    else:
        wave_num = min(spawner.current_wave_index + 1, len(spawner.waves))
        surface.blit(render_text(f"Wave {wave_num}/{len(spawner.waves)}", (200, 200, 200)), (120, 5))

    # Tower buttons — show cost + remaining count, grey out if maxed or locked
    for btn in BUTTONS:
        t = btn['type']
        rect = btn['rect']
        remaining = TOWER_PURCHASE_LIMITS[t] - purchase_counts[t]
        locked = (t == 'frost' and not frost_available)
        maxed = remaining <= 0
        disabled = maxed or locked

        r, g, b = TOWER_STATS[t]['color']
        pygame.draw.rect(surface, (r // 2, g // 2, b // 2) if disabled else (r, g, b), rect)

        # Highlight if selected and not disabled
        if tower.selected_tower_type == t and not disabled:
            pygame.draw.rect(surface, (255, 255, 255), rect, 1)

        label_font = get_label_font()
        label_x = rect.right + LABEL_GAP

        # Cost
        surface.blit(render_text(f"{TOWER_STATS[t]['cost']}g",
                                 (180, 180, 180) if disabled else (220, 200, 50), label_font),
                     (label_x, COST_LABEL_Y))

        # Remaining count, or LOCK while the type is unavailable
        if locked:
            rem_text, rem_color = "LOCK", (150, 110, 110)
        else:
            rem_text = f"{remaining}/{TOWER_PURCHASE_LIMITS[t]}"
            rem_color = (120, 120, 120) if maxed else (200, 200, 200)
        surface.blit(render_text(rem_text, rem_color, label_font), (label_x, COUNT_LABEL_Y))

def handle_click(lx, ly, state, purchase_counts, frost_available=True):
    if state.game_state == 'build_phase' and CONTINUE_BUTTON.collidepoint(lx, ly):
        return 'continue'

    for btn in BUTTONS:
        if btn['rect'].collidepoint(lx, ly):
            t = btn['type']
            # Block maxed-out or locked towers
            if purchase_counts[t] >= TOWER_PURCHASE_LIMITS[t]:
                return True
            if t == 'frost' and not frost_available:
                return True
            tower.selected_tower_type = t
            return True
    return False
