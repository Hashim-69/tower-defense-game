import pygame
import audio

class Projectile(pygame.sprite.Sprite):
    def __init__(self, start_pos, target, stats):
        super().__init__()
        self.pos = pygame.Vector2(start_pos)
        self.target = target
        self.stats = stats
        self.color = (255, 255, 200) # Simple light yellow color for bullets
        
    def update(self, dt, state, enemy_group):
        # If the target was killed by another projectile, die
        if not self.target.alive():
            self.kill()
            return
            
        direction = (self.target.pos - self.pos).normalize()
        self.pos += direction * self.stats['proj_speed'] * dt
        
        # Check collision
        if self.pos.distance_to(self.target.pos) < 4:
            impact_point = self.target.pos
            audio.play('hit')
            
            # Apply splash damage if Cannon
            if 'splash_radius' in self.stats:
                # We iterate over a copy or simply the group to find all enemies in range
                for enemy in list(enemy_group):
                    if enemy.pos.distance_to(impact_point) <= self.stats['splash_radius']:
                        enemy.hp -= self.stats['damage']
                        enemy.hit_flash_timer = 0.1
                        if enemy.hp <= 0:
                            state.gold += enemy.reward
                            audio.play('death')
                            enemy.kill()
            else:
                # Apply direct damage for Gunner / Frost
                self.target.hp -= self.stats['damage']
                self.target.hit_flash_timer = 0.1
                
                # Apply Frost effects if applicable
                if 'slow_duration' in self.stats:
                    self.target.slow_timer = self.stats['slow_duration']
                    self.target.current_slow_mult = self.stats['slow_mult']
                    
                if self.target.hp <= 0:
                    state.gold += self.target.reward
                    audio.play('death')
                    self.target.kill()
                    
            self.kill()
            
    def draw(self, surface):
        # Simple small circle for the projectile
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), 3)
