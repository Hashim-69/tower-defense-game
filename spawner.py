import pygame
from waves import WAVES
import enemy
import audio

class Spawner:
    def __init__(self):
        self.current_wave_index = 0
        self.spawn_timer = 0
        self.spawn_queue = WAVES[0]["enemies"].copy()
        self.interval = WAVES[0]["interval"]
        self.delay_timer = 0
        self.game_won = False
        
    def update(self, dt, enemy_group):
        if self.spawn_queue:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                enemy_type = self.spawn_queue.pop(0)
                new_enemy = enemy.Enemy(enemy_type)
                enemy_group.add(new_enemy)
                self.spawn_timer = self.interval
        elif len(enemy_group) == 0:
            # Wave is cleared
            self.delay_timer += dt
            if self.delay_timer >= 4.0:
                self.current_wave_index += 1
                if self.current_wave_index > 3:
                    self.game_won = True
                else:
                    self.spawn_queue = WAVES[self.current_wave_index]["enemies"].copy()
                    self.interval = WAVES[self.current_wave_index]["interval"]
                    self.delay_timer = 0
                    audio.play('wave_start')
