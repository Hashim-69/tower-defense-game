import pygame
import sys
import os

def resource_path(rel_path):
    base = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base, rel_path)

SOUNDS = {}

def init():
    pygame.mixer.init()
    try:
        SOUNDS['shoot'] = pygame.mixer.Sound(resource_path('assets/shoot.wav'))
        SOUNDS['hit'] = pygame.mixer.Sound(resource_path('assets/hit.wav'))
        SOUNDS['death'] = pygame.mixer.Sound(resource_path('assets/death.wav'))
        SOUNDS['wave_start'] = pygame.mixer.Sound(resource_path('assets/wave_start.wav'))
    except Exception as e:
        print("Warning: Could not load sound files:", e)

def play(name):
    if name in SOUNDS:
        SOUNDS[name].play()
