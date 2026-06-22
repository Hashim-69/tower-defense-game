import pygame
import sys
from settings import *
import grid
import enemy
import tower
import ui
from spawner import Spawner
import audio

class GameState:
    def __init__(self):
        self.lives = START_LIVES
        self.gold = START_GOLD
        self.game_over = False
        self.game_won = False

def main():
    pygame.init()
    audio.init()
    
    # Create the real window
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Micro Tower Defense")
    
    # Create the low-res surface for drawing
    game_surface = pygame.Surface(LOW_RES)
    
    clock = pygame.time.Clock()
    
    tile_map = grid.build_tile_map()
    
    enemy_group = pygame.sprite.Group()
    towers_group = pygame.sprite.Group()
    projectile_group = pygame.sprite.Group()
    spawner = Spawner()
    audio.play('wave_start')
    
    state = GameState()
    font = pygame.font.Font(None, 24) # Default font, size 24 (a bit larger for visibility)
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not state.game_over and not state.game_won:
                    mx, my = pygame.mouse.get_pos()
                    lx, ly = mx // SCALE, my // SCALE
                    
                    if ui.handle_click(lx, ly):
                        continue
                    
                    col = int(lx // TILE_SIZE)
                    row = int((ly - HUD_HEIGHT) // TILE_SIZE)
                    
                    if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
                        if tile_map[col][row] == 'buildable' and (col, row) not in tower.occupied:
                            cost = TOWER_STATS[tower.selected_tower_type]['cost']
                            if state.gold >= cost:
                                state.gold -= cost
                                tower.occupied.add((col, row))
                                new_tower = tower.Tower(tower.selected_tower_type, grid.grid_to_pixel(col, row))
                                towers_group.add(new_tower)
                
        # Game update logic
        if not state.game_over and not state.game_won:
            spawner.update(dt, enemy_group)
            if spawner.current_wave_index > 3:
                state.game_won = True
                
            for t in towers_group:
                t.update(dt, enemy_group, projectile_group)
                
            for e in enemy_group:
                e.update(dt)
                if e.leaked:
                    state.lives -= 1
                    e.kill()
                    
            for p in projectile_group:
                p.update(dt, state, enemy_group)
                    
            if state.lives <= 0:
                state.game_over = True
        
        # Drawing
        game_surface.fill(BG_COLOR)
        grid.draw_grid(game_surface, tile_map)
        ui.draw_hud(game_surface, state, spawner)
        
        for t in towers_group:
            t.draw(game_surface)
            
        for e in enemy_group:
            e.draw(game_surface)
            
        for p in projectile_group:
            p.draw(game_surface)
            
        if spawner.delay_timer > 0 and not state.game_won and spawner.current_wave_index <= 3:
            time_left = max(0, int(4.0 - spawner.delay_timer) + 1)
            # Use smaller font for this long text
            small_font = pygame.font.Font(None, 16)
            text_surf = small_font.render(f"WAVE CLEARED — NEXT WAVE IN {time_left}s", False, (200, 200, 200))
            text_rect = text_surf.get_rect(center=(LOW_RES[0] // 2, LOW_RES[1] // 2 - 20))
            game_surface.blit(text_surf, text_rect)
            
        if state.game_over:
            text_surf = font.render("GAME OVER", False, (255, 0, 0))
            text_rect = text_surf.get_rect(center=(LOW_RES[0] // 2, LOW_RES[1] // 2))
            game_surface.blit(text_surf, text_rect)
        elif state.game_won:
            text_surf = font.render("YOU WIN", False, (0, 255, 0))
            text_rect = text_surf.get_rect(center=(LOW_RES[0] // 2, LOW_RES[1] // 2))
            game_surface.blit(text_surf, text_rect)
            
        # Scale up the low-res surface to the real window size and blit
        # Using scale() instead of smoothscale() to preserve the blocky pixel-art look
        scaled = pygame.transform.scale(game_surface, WINDOW_SIZE)
        screen.blit(scaled, (0, 0))
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
