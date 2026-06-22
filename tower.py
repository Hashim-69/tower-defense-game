import pygame
import math
from settings import *
from projectile import Projectile
import audio
import utils

selected_tower_type = 'gunner'
occupied = set()

class Tower(pygame.sprite.Sprite):
    def __init__(self, tower_type, pos):
        super().__init__()
        self.type = tower_type
        self.pos = pygame.Vector2(pos)
        self.stats = TOWER_STATS[tower_type]
        self.cooldown_timer = 0
        self.current_target = None
        self.last_heading = 0
        self.head_surface = self._build_head_surface()
        
    def _build_head_surface(self):
        surf = pygame.Surface((30, 30), pygame.SRCALPHA)
        if self.type == 'gunner':
            pygame.draw.rect(surf, self.stats['outline_color'], (12, 1, 6, 10))
            pygame.draw.rect(surf, self.stats['color'], (13, 2, 4, 8))
        elif self.type == 'cannon':
            pygame.draw.rect(surf, self.stats['outline_color'], (10, 5, 10, 6))
            pygame.draw.rect(surf, self.stats['color'], (11, 6, 8, 4))
        elif self.type == 'frost':
            spikes = [[(10,10),(13,10),(12,5)], [(13,10),(17,10),(15,3)], [(17,10),(20,10),(19,5)]]
            for p in spikes:
                pygame.draw.polygon(surf, self.stats['color'], p)
                pygame.draw.polygon(surf, self.stats['outline_color'], p, 1)
        return surf
        
    def find_target(self, enemy_group):
        closest, closest_dist = None, self.stats['range']
        for enemy in enemy_group:
            d = self.pos.distance_to(enemy.pos)
            if d <= closest_dist:
                closest, closest_dist = enemy, d
        return closest
        
    def update(self, dt, enemy_group, projectile_group):
        self.current_target = self.find_target(enemy_group)
        if self.current_target:
            direction = self.current_target.pos - self.pos
            if direction.length_squared() > 0:
                heading = math.degrees(math.atan2(direction.x, -direction.y))
                self.last_heading = -heading
                
        self.cooldown_timer -= dt
        if self.current_target and self.cooldown_timer <= 0:
            proj = Projectile(self.pos, self.current_target, self.stats)
            projectile_group.add(proj)
            self.cooldown_timer = self.stats['cooldown']
            audio.play('shoot')
        
    def draw(self, surface):
        cx, cy = int(self.pos.x), int(self.pos.y)
        stats = self.stats
        fill_color = stats['color']
        out_color = stats['outline_color']
        high_color = stats['highlight_color']
        
        if self.type == 'gunner':
            utils.draw_part(surface, cx, cy, -7, -7, 14, 14, out_color)
            utils.draw_part(surface, cx, cy, -5, -5, 10, 10, fill_color)
            utils.draw_part(surface, cx, cy, -4, -4, 4, 4, high_color)
        elif self.type == 'cannon':
            utils.draw_part(surface, cx, cy, -8, -7, 16, 14, out_color)
            utils.draw_part(surface, cx, cy, -6, -5, 12, 10, fill_color)
            utils.draw_part(surface, cx, cy, -5, -4, 4, 4, high_color)
        elif self.type == 'frost':
            utils.draw_part(surface, cx, cy, -7, -7, 14, 14, out_color)
            utils.draw_part(surface, cx, cy, -5, -5, 10, 10, fill_color)
            utils.draw_part(surface, cx, cy, -4, -4, 4, 4, high_color)
            
        rotated = pygame.transform.rotate(self.head_surface, self.last_heading)
        rect = rotated.get_rect(center=(cx, cy))
        surface.blit(rotated, rect)
