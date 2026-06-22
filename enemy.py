import pygame
from settings import *
import grid
import utils

class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type):
        super().__init__()
        self.type = enemy_type
        stats = ENEMY_STATS[enemy_type]
        self.hp = stats['hp']
        self.base_speed = stats['speed']
        self.reward = stats['reward']
        self.color = stats['color']
        self.radius = stats['radius']
        self.slow_timer = 0
        self.current_slow_mult = 1.0
        self.hit_flash_timer = 0
        
        self.path = [grid.grid_to_pixel(c, r) for c, r in WAYPOINTS_GRID]
        self.pos = pygame.Vector2(self.path[0])
        self.waypoint_index = 1
        self.reached_end = False
        self.leaked = False

    def update(self, dt):
        if self.reached_end:
            return
            
        target = pygame.Vector2(self.path[self.waypoint_index])
        
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
        
        if self.slow_timer > 0:
            self.slow_timer -= dt
            effective_speed = self.base_speed * self.current_slow_mult
        else:
            effective_speed = self.base_speed
        
        if self.pos.distance_to(target) <= effective_speed * dt:
            self.pos = target
            self.waypoint_index += 1
            if self.waypoint_index >= len(self.path):
                self.reached_end = True
                self.leaked = True
        else:
            direction = (target - self.pos).normalize()
            self.pos += direction * effective_speed * dt

    def draw(self, surface):
        if not self.reached_end:
            cx, cy = int(self.pos.x), int(self.pos.y)
            stats = ENEMY_STATS[self.type]
            
            fill_color = (255, 255, 255) if self.hit_flash_timer > 0 else self.color
            out_color = (255, 255, 255) if self.hit_flash_timer > 0 else stats['outline_color']
            high_color = (255, 255, 255) if self.hit_flash_timer > 0 else stats['highlight_color']
            
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
