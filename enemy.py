import pygame
from settings import *
import grid
import utils

FLASH_COLOR = (255, 255, 255)

# Waypoint lists are shared by every enemy on a level, so bake each one into
# pixel-space Vector2s exactly once instead of per spawn.
_path_cache = {}

def _pixel_path(waypoints):
    key = tuple(waypoints)
    path = _path_cache.get(key)
    if path is None:
        path = tuple(pygame.Vector2(grid.grid_to_pixel(c, r)) for c, r in key)
        _path_cache[key] = path
    return path

class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type, waypoints=WAYPOINTS_GRID, hp_mult=1.0, speed_mult=1.0):
        super().__init__()
        self.type = enemy_type
        stats = ENEMY_STATS[enemy_type]
        self.hp = stats['hp'] * hp_mult
        self.base_speed = stats['speed'] * speed_mult
        self.reward = stats['reward']
        self.radius = stats['radius']
        self.color = stats['color']
        self.outline_color = stats['outline_color']
        self.highlight_color = stats['highlight_color']
        self.slow_timer = 0
        self.current_slow_mult = 1.0
        self.hit_flash_timer = 0

        # Shared, treated as read-only — never mutate an entry of self.path.
        self.path = _pixel_path(waypoints)
        self.pos = pygame.Vector2(self.path[0])
        self.waypoint_index = 1
        self.reached_end = False
        self.leaked = False

    def update(self, dt):
        if self.reached_end:
            return

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        if self.slow_timer > 0:
            self.slow_timer -= dt
            speed = self.base_speed * self.current_slow_mult
        else:
            speed = self.base_speed

        # Spend the frame's travel budget across as many segments as it covers.
        # Snapping to a corner and stopping there discarded the leftover
        # distance, which made corners cost speed and got worse the faster the
        # enemy (runners on level 3 visibly stuttered at every turn).
        remaining = speed * dt
        path = self.path
        while remaining > 0:
            to_target = path[self.waypoint_index] - self.pos
            distance = to_target.length()

            if distance > remaining:
                self.pos += to_target * (remaining / distance)
                return

            self.pos.update(path[self.waypoint_index])
            remaining -= distance
            self.waypoint_index += 1
            if self.waypoint_index >= len(path):
                self.reached_end = True
                self.leaked = True
                return

    def draw(self, surface):
        if self.reached_end:
            return

        cx, cy = int(self.pos.x), int(self.pos.y)
        if self.hit_flash_timer > 0:
            fill_color = out_color = high_color = FLASH_COLOR
        else:
            fill_color = self.color
            out_color = self.outline_color
            high_color = self.highlight_color

        if self.type == 'walker':
            utils.draw_part(surface, cx, cy, -5, -6, 10, 11, out_color)
            utils.draw_part(surface, cx, cy, -3, -5, 6, 3, fill_color)
            utils.draw_part(surface, cx, cy, -4, -2, 8, 4, fill_color)
            utils.draw_part(surface, cx, cy, -3, 2, 6, 3, fill_color)
            utils.draw_part(surface, cx, cy, -3, -1, 3, 3, high_color)
            utils.draw_part(surface, cx, cy, -2, -4, 1, 1, EYE_COLOR)
            utils.draw_part(surface, cx, cy, 1, -4, 1, 1, EYE_COLOR)
        elif self.type == 'armored':
            utils.draw_part(surface, cx, cy, -7, -7, 14, 14, out_color)
            utils.draw_part(surface, cx, cy, -5, -5, 10, 10, fill_color)
            utils.draw_poly(surface, cx, cy, [(-4, -8), (-1, -5), (-4, -2), (-7, -5)], fill_color)
            utils.draw_poly(surface, cx, cy, [(4, -8), (7, -5), (4, -2), (1, -5)], fill_color)
            utils.draw_part(surface, cx, cy, -4, -4, 3, 3, high_color)
            utils.draw_part(surface, cx, cy, -2, 0, 1, 1, EYE_COLOR)
            utils.draw_part(surface, cx, cy, 1, 0, 1, 1, EYE_COLOR)
        elif self.type == 'runner':
            # Low, wide, finned silhouette
            utils.draw_part(surface, cx, cy, -7, -5, 14, 8, out_color)
            utils.draw_part(surface, cx, cy, -4, -4, 8, 2, fill_color)
            utils.draw_part(surface, cx, cy, -6, -2, 12, 3, fill_color)
            utils.draw_part(surface, cx, cy, -4, 1, 8, 2, fill_color)
            utils.draw_poly(surface, cx, cy, [(-7, -1), (-10, 0), (-7, 1)], fill_color)
            utils.draw_poly(surface, cx, cy, [(7, -1), (10, 0), (7, 1)], fill_color)
            utils.draw_part(surface, cx, cy, -4, -3, 3, 2, high_color)
            utils.draw_part(surface, cx, cy, -2, -3, 1, 1, EYE_COLOR)
            utils.draw_part(surface, cx, cy, 1, -3, 1, 1, EYE_COLOR)
        elif self.type == 'brute':
            # Tall, bulky, side-plated silhouette
            utils.draw_part(surface, cx, cy, -9, -9, 18, 18, out_color)
            utils.draw_part(surface, cx, cy, -4, -9, 8, 6, fill_color)
            utils.draw_part(surface, cx, cy, -7, -5, 14, 12, fill_color)
            utils.draw_poly(surface, cx, cy, [(-7, -5), (-4, -2), (-7, 1), (-10, -2)], fill_color)
            utils.draw_poly(surface, cx, cy, [(7, -5), (10, -2), (7, 1), (4, -2)], fill_color)
            utils.draw_part(surface, cx, cy, -6, -3, 5, 5, high_color)
            utils.draw_part(surface, cx, cy, -2, -7, 1, 1, EYE_COLOR)
            utils.draw_part(surface, cx, cy, 1, -7, 1, 1, EYE_COLOR)
