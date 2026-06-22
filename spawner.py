import pygame
import enemy
import audio

class Spawner:
    def __init__(self, waves_list, enemy_mult=None):
        self.waves = waves_list
        self.enemy_mult = enemy_mult or {"hp": 1.0, "speed": 1.0}
        self.current_wave_index = 0
        self.spawn_timer = 0
        self.spawn_queue = self.waves[0]["enemies"].copy()
        self.interval = self.waves[0]["interval"]
        self.delay_timer = 0
        self.level_complete = False
        
    def update(self, dt, enemy_group, current_level_path):
        if self.spawn_queue:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                enemy_type = self.spawn_queue.pop(0)
                new_enemy = enemy.Enemy(enemy_type, waypoints=current_level_path, hp_mult=self.enemy_mult['hp'], speed_mult=self.enemy_mult['speed'])
                enemy_group.add(new_enemy)
                self.spawn_timer = self.interval
        elif len(enemy_group) == 0:
            # Wave is cleared
            self.delay_timer += dt
            if self.delay_timer >= 4.0:
                if self.current_wave_index >= len(self.waves) - 1:
                    self.level_complete = True
                else:
                    self.current_wave_index += 1
                    self.spawn_queue = self.waves[self.current_wave_index]["enemies"].copy()
                    self.interval = self.waves[self.current_wave_index]["interval"]
                    self.delay_timer = 0
                    audio.play('wave_start')
