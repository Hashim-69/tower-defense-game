import pygame
import sys
import math
import asyncio
from settings import *
import grid
import tower
import ui
from spawner import Spawner
import audio

class GameState:
    def __init__(self):
        self.lives = START_LIVES
        self.gold = START_GOLD
        self.game_state = 'playing'
        self.current_level_index = 0

def new_spawner(level_index):
    level = LEVELS[level_index]
    return Spawner(level['waves'], level['enemy_mult'])

async def main():
    pygame.init()
    audio.init()

    # Create the real window
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Micro Tower Defense")
    screen_w, screen_h = screen.get_size()

    # Create the low-res surface for drawing. convert() matches the display
    # format so the per-frame upscale never has to convert pixel formats.
    game_surface = pygame.Surface(LOW_RES).convert()

    clock = pygame.time.Clock()

    state = GameState()
    tile_map = grid.build_tile_map(LEVELS[state.current_level_index]['path'])
    background = grid.render_background(tile_map)
    tower_purchase_counts = {'gunner': 0, 'cannon': 0, 'frost': 0}
    frost_available = False  # Frost locked on level 1, unlocks from level 2 onward

    tower.occupied.clear()
    tower.selected_tower_type = 'gunner'

    enemy_group = pygame.sprite.Group()
    towers_group = pygame.sprite.Group()
    projectile_group = pygame.sprite.Group()
    spawner = new_spawner(state.current_level_index)
    audio.play('wave_start')

    font = pygame.font.Font(None, 24)  # Default font, size 24 (a bit larger for visibility)
    banner_font = pygame.font.Font(None, 16)  # Smaller, for the longer countdown line
    screen_center = (LOW_RES[0] // 2, LOW_RES[1] // 2)
    game_over_surf = font.render("GAME OVER", False, (255, 0, 0))
    game_won_surf = font.render("YOU WIN", False, (0, 255, 0))
    game_over_rect = game_over_surf.get_rect(center=screen_center)
    game_won_rect = game_won_surf.get_rect(center=screen_center)
    # One rasterised surface per whole second of the countdown, reused every frame.
    countdown_surfs = [
        banner_font.render(f"WAVE CLEARED — NEXT WAVE IN {s}s", False, (200, 200, 200))
        for s in range(int(math.ceil(WAVE_DELAY)) + 1)
    ]
    countdown_center = (LOW_RES[0] // 2, LOW_RES[1] // 2 - 20)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state.game_state in ('playing', 'build_phase'):
                    mx, my = event.pos
                    # Map through the real screen size rather than a hardcoded
                    # SCALE, so clicks stay aligned if the window differs.
                    lx = mx * LOW_RES[0] // screen_w
                    ly = my * LOW_RES[1] // screen_h

                    click_res = ui.handle_click(lx, ly, state, tower_purchase_counts, frost_available)
                    if click_res == 'continue':
                        spawner = new_spawner(state.current_level_index)
                        state.game_state = 'playing'
                        continue
                    elif click_res:
                        continue

                    col = lx // TILE_SIZE
                    row = (ly - HUD_HEIGHT) // TILE_SIZE

                    if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
                        tower_type = tower.selected_tower_type
                        if tower.is_valid_placement(col, row, tower_type, tile_map, tower.occupied,
                                                    state.gold, towers_group, tower_purchase_counts,
                                                    frost_available):
                            state.gold -= TOWER_STATS[tower_type]['cost']
                            tower.occupied.add((col, row))
                            tower_purchase_counts[tower_type] += 1
                            towers_group.add(tower.Tower(tower_type, grid.grid_to_pixel(col, row)))

        # Game update logic
        if state.game_state == 'playing':
            spawner.update(dt, enemy_group, LEVELS[state.current_level_index]['path'])

            if spawner.level_complete:
                if state.current_level_index + 1 >= len(LEVELS):
                    state.game_state = 'game_won'
                else:
                    state.current_level_index += 1
                    towers_group.empty()
                    projectile_group.empty()
                    tower.occupied.clear()
                    tile_map = grid.build_tile_map(LEVELS[state.current_level_index]['path'])
                    background = grid.render_background(tile_map)
                    # Reset purchase limits each level — Frost unlocks from level 2 onward
                    tower_purchase_counts = {'gunner': 0, 'cannon': 0, 'frost': 0}
                    frost_available = state.current_level_index >= 1
                    state.game_state = 'build_phase'

        if state.game_state in ('playing', 'build_phase'):
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
                state.lives = 0  # several enemies can leak on one frame
                state.game_state = 'game_over'

        # Drawing — the map is static within a level, so it is baked once and
        # blitted instead of re-drawing 200 tiles per frame.
        game_surface.blit(background, (0, 0))

        for t in towers_group:
            t.draw(game_surface)

        for e in enemy_group:
            e.draw(game_surface)

        for p in projectile_group:
            p.draw(game_surface)

        # HUD last so tall sprites near the top row cannot overdraw it
        ui.draw_hud(game_surface, state, spawner, tower_purchase_counts, frost_available)

        if state.game_state == 'playing' and spawner.delay_timer > 0 and not spawner.level_complete:
            seconds_left = max(0, math.ceil(WAVE_DELAY - spawner.delay_timer))
            text_surf = countdown_surfs[seconds_left]
            game_surface.blit(text_surf, text_surf.get_rect(center=countdown_center))

        if state.game_state == 'game_over':
            game_surface.blit(game_over_surf, game_over_rect)
        elif state.game_state == 'game_won':
            game_surface.blit(game_won_surf, game_won_rect)

        # Scale the low-res surface straight into the window. Passing the
        # display surface as the destination avoids allocating a fresh
        # 1280x720 surface and blitting it every single frame.
        # Nearest-neighbour scale(), not smoothscale(), preserves the pixel art.
        pygame.transform.scale(game_surface, (screen_w, screen_h), screen)

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
