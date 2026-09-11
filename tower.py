import pygame
import math
from settings import *
from projectile import Projectile
import audio
import utils
import grid

selected_tower_type = 'gunner'
occupied = set()

MIN_TOWER_DISTANCE_SQ = MIN_TOWER_DISTANCE * MIN_TOWER_DISTANCE

def is_valid_placement(col, row, tower_type, tile_map, occupied, gold, towers_group, purchase_counts, frost_available=True):
    if tile_map[col][row] != 'buildable':
        return False
    if (col, row) in occupied:
        return False
    if gold < TOWER_STATS[tower_type]['cost']:
        return False
    if purchase_counts[tower_type] >= TOWER_PURCHASE_LIMITS[tower_type]:
        return False
    if tower_type == 'frost' and not frost_available:
        return False
    candidate_pos = pygame.Vector2(grid.grid_to_pixel(col, row))
    for t in towers_group:
        if candidate_pos.distance_squared_to(t.pos) < MIN_TOWER_DISTANCE_SQ:
            return False
    return True

# Every tower of a type shares one barrel sprite, and rotating it is expensive
# enough to show up in a profile, so rotations are quantised and memoised.
# 6 degrees is well under one pixel of movement at this sprite size and scale.
_ROTATION_STEP = 6
_ROTATION_BUCKETS = 360 // _ROTATION_STEP
_head_cache = {}

def _head_surface(tower_type):
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    stats = TOWER_STATS[tower_type]
    if tower_type == 'gunner':
        pygame.draw.rect(surf, stats['outline_color'], (12, 1, 6, 10))
        pygame.draw.rect(surf, stats['color'], (13, 2, 4, 8))
    elif tower_type == 'cannon':
        pygame.draw.rect(surf, stats['outline_color'], (10, 5, 10, 6))
        pygame.draw.rect(surf, stats['color'], (11, 6, 8, 4))
    elif tower_type == 'frost':
        spikes = [[(10, 10), (13, 10), (12, 5)], [(13, 10), (17, 10), (15, 3)], [(17, 10), (20, 10), (19, 5)]]
        for p in spikes:
            pygame.draw.polygon(surf, stats['color'], p)
            pygame.draw.polygon(surf, stats['outline_color'], p, 1)
    return surf

def _rotated_head(tower_type, bucket):
    key = (tower_type, bucket)
    rotated = _head_cache.get(key)
    if rotated is None:
        rotated = pygame.transform.rotate(_head_surface(tower_type), bucket * _ROTATION_STEP)
        _head_cache[key] = rotated
    return rotated

class Tower(pygame.sprite.Sprite):
    def __init__(self, tower_type, pos):
        super().__init__()
        self.type = tower_type
        self.pos = pygame.Vector2(pos)
        self.stats = TOWER_STATS[tower_type]
        self.range_sq = self.stats['range'] ** 2
        self.cooldown = self.stats['cooldown']
        self.cooldown_timer = 0
        self.current_target = None
        self.heading_bucket = 0

    def find_target(self, enemy_group):
        # Squared distances: same ordering, no square roots, and this runs for
        # every tower against every enemy on every frame.
        closest, closest_dist = None, self.range_sq
        for enemy in enemy_group:
            d = self.pos.distance_squared_to(enemy.pos)
            if d <= closest_dist:
                closest, closest_dist = enemy, d
        return closest

    def update(self, dt, enemy_group, projectile_group):
        self.current_target = self.find_target(enemy_group)
        if self.current_target:
            direction = self.current_target.pos - self.pos
            if direction.length_squared() > 0:
                # Barrel sprites point up; rotate() is counter-clockwise.
                heading = math.degrees(math.atan2(-direction.x, -direction.y))
                self.heading_bucket = int(round(heading / _ROTATION_STEP)) % _ROTATION_BUCKETS

        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt
        if self.current_target and self.cooldown_timer <= 0:
            projectile_group.add(Projectile(self.pos, self.current_target, self.stats))
            self.cooldown_timer = self.cooldown
            audio.play('shoot')

    def draw(self, surface):
        cx, cy = int(self.pos.x), int(self.pos.y)
        stats = self.stats
        fill_color = stats['color']
        out_color = stats['outline_color']
        high_color = stats['highlight_color']

        if self.type == 'cannon':
            utils.draw_part(surface, cx, cy, -8, -7, 16, 14, out_color)
            utils.draw_part(surface, cx, cy, -6, -5, 12, 10, fill_color)
            utils.draw_part(surface, cx, cy, -5, -4, 4, 4, high_color)
        else:
            # gunner and frost share a base silhouette; the head tells them apart
            utils.draw_part(surface, cx, cy, -7, -7, 14, 14, out_color)
            utils.draw_part(surface, cx, cy, -5, -5, 10, 10, fill_color)
            utils.draw_part(surface, cx, cy, -4, -4, 4, 4, high_color)

        rotated = _rotated_head(self.type, self.heading_bucket)
        surface.blit(rotated, rotated.get_rect(center=(cx, cy)))
