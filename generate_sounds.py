"""Regenerate the placeholder sound effects in assets/.

Run once; the wavs are committed. Only needed if you want to retune them.
"""
import array
import math
import os
import random
import wave

SAMPLE_RATE = 44100
VOLUME = 0.2

def _sample(wave_type, freq, i):
    if wave_type == 'sine':
        return math.sin(2.0 * math.pi * freq * i / SAMPLE_RATE)
    if wave_type == 'square':
        return 1.0 if math.sin(2.0 * math.pi * freq * i / SAMPLE_RATE) > 0 else -1.0
    if wave_type == 'noise':
        return random.uniform(-1.0, 1.0)
    raise ValueError(f"unknown wave_type {wave_type!r}")

def make_wav(filename, freq, duration, wave_type='sine'):
    directory = os.path.dirname(filename)
    if directory:
        os.makedirs(directory, exist_ok=True)

    total = int(SAMPLE_RATE * duration)
    # Build the whole buffer first: struct.pack + writeframesraw per sample made
    # this hundreds of times slower than it needs to be.
    samples = array.array('h')
    for i in range(total):
        # Linear decay envelope, so these read as hits rather than held beeps.
        envelope = 1.0 - i / total
        samples.append(int(_sample(wave_type, freq, i) * envelope * VOLUME * 32767.0))

    with wave.open(filename, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(samples.tobytes())

if __name__ == "__main__":
    make_wav('assets/shoot.wav', 880, 0.1, 'square')
    make_wav('assets/hit.wav', 440, 0.1, 'noise')
    make_wav('assets/death.wav', 220, 0.3, 'noise')
    make_wav('assets/wave_start.wav', 660, 0.5, 'sine')
    print("Generated sounds.")
