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
    
    # Wave or Build Phase
    if state.game_state == 'build_phase':
        banner_surf = font.render(f"LEVEL {state.current_level_index + 1} — BUILD PHASE", False, (200, 200, 200))
        banner_rect = banner_surf.get_rect(center=(LOW_RES[0]//2, LOW_RES[1]//2 - 10))
        surface.blit(banner_surf, banner_rect)
        
        btn_rect = pygame.Rect(LOW_RES[0]//2 - 40, LOW_RES[1]//2 + 10, 80, 24)
        pygame.draw.rect(surface, (100, 150, 100), btn_rect)
        pygame.draw.rect(surface, (200, 255, 200), btn_rect, 1)
        btn_surf = font.render("CONTINUE", False, (255, 255, 255))
        btn_surf_rect = btn_surf.get_rect(center=btn_rect.center)
        surface.blit(btn_surf, btn_surf_rect)
    else:
        wave_num = min(spawner.current_wave_index + 1, len(spawner.waves))
        total_waves = len(spawner.waves)
        wave_surf = font.render(f"Wave {wave_num}/{total_waves}", False, (200, 200, 200))
        surface.blit(wave_surf, (120, 5))
        
    
    # Tower buttons
    for btn in BUTTONS:
        color = TOWER_STATS[btn['type']]['color']
        pygame.draw.rect(surface, color, btn['rect'])
        
        # Highlight if selected
        if tower.selected_tower_type == btn['type']:
            pygame.draw.rect(surface, (255, 255, 255), btn['rect'], 1)

def handle_click(lx, ly, state):
    if state.game_state == 'build_phase':
        btn_rect = pygame.Rect(LOW_RES[0]//2 - 40, LOW_RES[1]//2 + 10, 80, 24)
        if btn_rect.collidepoint(lx, ly):
            return 'continue'
            
    for btn in BUTTONS:
        if btn['rect'].collidepoint(lx, ly):
            tower.selected_tower_type = btn['type']
            return True
    return False
