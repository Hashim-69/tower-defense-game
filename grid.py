import pygame
from settings import *

def build_tile_map():
    # Initialize grid with 'buildable'
    tile_map = [['buildable' for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]
    
    # Walk through each consecutive pair of waypoints
    for i in range(len(WAYPOINTS_GRID) - 1):
        col1, row1 = WAYPOINTS_GRID[i]
        col2, row2 = WAYPOINTS_GRID[i + 1]
        
        if col1 == col2:
            # Vertical segment
            start = min(row1, row2)
            end = max(row1, row2)
            for r in range(start, end + 1):
                tile_map[col1][r] = 'path'
        elif row1 == row2:
            # Horizontal segment
            start = min(col1, col2)
            end = max(col1, col2)
            for c in range(start, end + 1):
                tile_map[c][row1] = 'path'
                
    return tile_map

def grid_to_pixel(col, row):
    return (col * TILE_SIZE + TILE_SIZE / 2, HUD_HEIGHT + row * TILE_SIZE + TILE_SIZE / 2)

def draw_grid(surface, tile_map):
    # Draw tiles
    for col in range(GRID_COLS):
        for row in range(GRID_ROWS):
            rect = pygame.Rect(col * TILE_SIZE, HUD_HEIGHT + row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            
            if tile_map[col][row] == 'path':
                color = (90, 70, 50)
            else:
                color = (40, 70, 40)
                
            pygame.draw.rect(surface, color, rect)
            
    # Draw HUD bar
    hud_rect = pygame.Rect(0, 0, LOW_RES[0], HUD_HEIGHT)
    pygame.draw.rect(surface, HUD_COLOR, hud_rect)
