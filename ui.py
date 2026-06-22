import pygame
from settings import *
import tower

BUTTONS = [
    {'type': 'gunner', 'rect': pygame.Rect(LOW_RES[0] - 60, 3, 14, 14)},
    {'type': 'cannon', 'rect': pygame.Rect(LOW_RES[0] - 40, 3, 14, 14)},
    {'type': 'frost', 'rect': pygame.Rect(LOW_RES[0] - 20, 3, 14, 14)}
]

_font = None

def get_font():
    global _font
    if _font is None:
        _font = pygame.font.Font(None, 14)
    return _font

def draw_hud(surface, state, spawner):
    font = get_font()
    
    # Gold
    gold_surf = font.render(f"Gold: {state.gold}", False, (220, 200, 50))
    surface.blit(gold_surf, (5, 5))
    
    # Lives
    lives_surf = font.render(f"Lives: {state.lives}", False, (220, 80, 80))
    surface.blit(lives_surf, (60, 5))
    
    # Wave
    wave_num = min(spawner.current_wave_index + 1, 4)
    wave_surf = font.render(f"Wave {wave_num}/4", False, (200, 200, 200))
    surface.blit(wave_surf, (120, 5))
    
    # Tower buttons
    for btn in BUTTONS:
        color = TOWER_STATS[btn['type']]['color']
        pygame.draw.rect(surface, color, btn['rect'])
        
        # Highlight if selected
        if tower.selected_tower_type == btn['type']:
            pygame.draw.rect(surface, (255, 255, 255), btn['rect'], 1)

def handle_click(lx, ly):
    for btn in BUTTONS:
        if btn['rect'].collidepoint(lx, ly):
            tower.selected_tower_type = btn['type']
            return True
    return False
