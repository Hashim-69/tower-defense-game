import pygame
from settings import HIT_FLASH_TIME, PROJECTILE_HIT_RADIUS
import audio

PROJECTILE_COLOR = (255, 255, 200)  # Simple light yellow color for bullets

class Projectile(pygame.sprite.Sprite):
    def __init__(self, start_pos, target, stats):
        super().__init__()
        self.pos = pygame.Vector2(start_pos)
        self.target = target
        self.stats = stats
        self.speed = stats['proj_speed']
        self.damage = stats['damage']
        self.splash_radius_sq = stats['splash_radius'] ** 2 if 'splash_radius' in stats else 0
        self.color = PROJECTILE_COLOR

    def update(self, dt, state, enemy_group):
        target = self.target
        # If the target was killed by another projectile, die
        if not target.alive():
            self.kill()
            return

        to_target = target.pos - self.pos
        distance = to_target.length()
        step = self.speed * dt

        # Hit if this step reaches the target at all, not only if the projectile
        # happens to land inside the hit radius. A gunner bullet only covers
        # 3.7px per frame at 60fps against a 4px radius, so any frame-time dip
        # used to overshoot the target and leave the bullet circling it.
        if distance > step and distance > PROJECTILE_HIT_RADIUS:
            self.pos += to_target * (step / distance)
            return

        self._detonate(state, enemy_group)
        self.kill()

    def _detonate(self, state, enemy_group):
        audio.play('hit')

        if self.splash_radius_sq:
            # Copy: the damage pass can kill the target, and target.pos is a live
            # reference that must not be read back after that.
            impact_point = pygame.Vector2(self.target.pos)
            for enemy in list(enemy_group):
                if enemy.pos.distance_squared_to(impact_point) <= self.splash_radius_sq:
                    self._apply_damage(enemy, state)
            return

        # Direct damage for Gunner / Frost
        if 'slow_duration' in self.stats:
            self.target.slow_timer = self.stats['slow_duration']
            self.target.current_slow_mult = self.stats['slow_mult']
        self._apply_damage(self.target, state)

    def _apply_damage(self, enemy, state):
        enemy.hp -= self.damage
        enemy.hit_flash_timer = HIT_FLASH_TIME
        if enemy.hp <= 0:
            state.gold += enemy.reward
            audio.play('death')
            enemy.kill()

    def draw(self, surface):
        # Simple small circle for the projectile
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), 3)
