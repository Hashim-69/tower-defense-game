import pygame

def draw_part(surface, cx, cy, rel_x, rel_y, w, h, color):
    pygame.draw.rect(surface, color, (cx + rel_x, cy + rel_y, w, h))

def draw_poly(surface, cx, cy, rel_points, color, outline_color=None):
    pts = [(cx + x, cy + y) for x, y in rel_points]
    pygame.draw.polygon(surface, color, pts)
    if outline_color:
        pygame.draw.polygon(surface, outline_color, pts, 1)
