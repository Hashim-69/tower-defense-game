import os
import wave
import struct
import math
import random

def make_wav(filename, freq, duration, wave_type='sine'):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        
        for i in range(int(44100 * duration)):
            if wave_type == 'sine':
                val = math.sin(2.0 * math.pi * freq * i / 44100.0)
            elif wave_type == 'square':
                val = 1.0 if math.sin(2.0 * math.pi * freq * i / 44100.0) > 0 else -1.0
            elif wave_type == 'noise':
                val = random.uniform(-1.0, 1.0)
            
            # Envelope (decay) to make it sound like a hit/shoot rather than a continuous beep
            env = 1.0 - (i / (44100 * duration))
            val *= env * 0.2 # 20% volume
            
            data = struct.pack('<h', int(val * 32767.0))
            w.writeframesraw(data)

make_wav('assets/shoot.wav', 880, 0.1, 'square')
make_wav('assets/hit.wav', 440, 0.1, 'noise')
make_wav('assets/death.wav', 220, 0.3, 'noise')
make_wav('assets/wave_start.wav', 660, 0.5, 'sine')
print("Generated sounds.")
