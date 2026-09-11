from collections import deque

import enemy
import audio
from settings import WAVE_DELAY

class Spawner:
    def __init__(self, waves_list, enemy_mult=None):
        if not waves_list:
            raise ValueError("Spawner needs at least one wave")
        self.waves = waves_list
        self.enemy_mult = enemy_mult or {"hp": 1.0, "speed": 1.0}
        self.current_wave_index = 0
        self.spawn_timer = 0
        self.delay_timer = 0
        self.level_complete = False
        self._load_wave(0)

    def _load_wave(self, index):
        self.current_wave_index = index
        self.spawn_queue = deque(self.waves[index]["enemies"])
        self.interval = self.waves[index]["interval"]

    def update(self, dt, enemy_group, current_level_path):
        if self.spawn_queue:
            self.spawn_timer -= dt
            # Accumulate the interval rather than resetting to it: resetting
            # threw away the overshoot every spawn, so waves ran slower than
            # their configured interval and drifted further the longer they ran.
            while self.spawn_queue and self.spawn_timer <= 0:
                enemy_type = self.spawn_queue.popleft()
                enemy_group.add(enemy.Enemy(
                    enemy_type,
                    waypoints=current_level_path,
                    hp_mult=self.enemy_mult['hp'],
                    speed_mult=self.enemy_mult['speed'],
                ))
                self.spawn_timer += self.interval
        elif len(enemy_group) == 0:
            # Wave is cleared
            self.delay_timer += dt
            if self.delay_timer >= WAVE_DELAY:
                if self.current_wave_index >= len(self.waves) - 1:
                    self.level_complete = True
                else:
                    self._load_wave(self.current_wave_index + 1)
                    self.spawn_timer = 0
                    self.delay_timer = 0
                    audio.play('wave_start')
