import pygame
from settings import *

PATH_COLOR = (90, 70, 50)
BUILDABLE_COLOR = (40, 70, 40)

def build_tile_map(waypoints=WAYPOINTS_GRID):
    # Initialize grid with 'buildable'
    tile_map = [['buildable' for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]

    # Walk through each consecutive pair of waypoints
    for i in range(len(waypoints) - 1):
        col1, row1 = waypoints[i]
        col2, row2 = waypoints[i + 1]

        if col1 == col2:
            # Vertical segment
            for r in range(min(row1, row2), max(row1, row2) + 1):
                tile_map[col1][r] = 'path'
        elif row1 == row2:
            # Horizontal segment
            for c in range(min(col1, col2), max(col1, col2) + 1):
                tile_map[c][row1] = 'path'
        else:
            # Enemies walk straight between waypoints, so a diagonal pair would
            # leave the tiles it crosses marked buildable and let the player wall
            # off a route enemies ignore. Fail loudly instead of drawing a lie.
            raise ValueError(
                f"Waypoints {i} -> {i + 1} ({col1},{row1}) -> ({col2},{row2}) "
                "are not axis-aligned; path segments must be horizontal or vertical."
            )

    return tile_map

def grid_to_pixel(col, row):
    return (col * TILE_SIZE + TILE_SIZE / 2, HUD_HEIGHT + row * TILE_SIZE + TILE_SIZE / 2)

def render_background(tile_map):
    """Bake the static map (tiles + empty HUD bar) into a surface.

    The tiles never change within a level, so drawing all 200 of them every
    frame was pure waste; main.py blits this once per frame instead.
    """
    surface = pygame.Surface(LOW_RES)
    surface.fill(BG_COLOR)

    for col in range(GRID_COLS):
        column = tile_map[col]
        x = col * TILE_SIZE
        for row in range(GRID_ROWS):
            color = PATH_COLOR if column[row] == 'path' else BUILDABLE_COLOR
            pygame.draw.rect(surface, color, (x, HUD_HEIGHT + row * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    pygame.draw.rect(surface, HUD_COLOR, (0, 0, LOW_RES[0], HUD_HEIGHT))
    return surface.convert()
