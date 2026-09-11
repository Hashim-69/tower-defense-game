import pygame
import sys
import os

_ASSET_DIR = os.path.join(
    getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))),
    'assets',
)

# The pygbag (WebAssembly) build ships ogg copies because the browser mixer does
# not reliably decode these wavs; native builds keep using the wavs.
_EXT = '-pygbag.ogg' if sys.platform == 'emscripten' else '.wav'

SOUND_NAMES = ('shoot', 'hit', 'death', 'wave_start')

SOUNDS = {}

def init():
    try:
        # mixer.init() raises on a machine with no audio device (CI, headless
        # servers); that used to take the whole game down before the first frame.
        pygame.mixer.init()
        # Default is 8 channels, which a few gunners at a 0.3s cooldown exhaust,
        # cutting off death and wave-start cues mid-playback.
        pygame.mixer.set_num_channels(16)
        for name in SOUND_NAMES:
            SOUNDS[name] = pygame.mixer.Sound(os.path.join(_ASSET_DIR, name + _EXT))
    except Exception as e:
        SOUNDS.clear()
        print("Warning: audio disabled:", e)

def play(name):
    sound = SOUNDS.get(name)
    if sound is not None:
        sound.play()
