# Rendering
LOW_RES = (320, 180)
SCALE = 4
WINDOW_SIZE = (1280, 720)
FPS = 60
BG_COLOR = (30, 30, 40)
HUD_COLOR = (20, 20, 25)
HUD_HEIGHT = 20

# Grid
TILE_SIZE = 16
GRID_COLS = 20
GRID_ROWS = 10
MIN_TOWER_DISTANCE = 24  # low-res px; blocks placement within ~1.5 tiles of another tower

# Path
WAYPOINTS_GRID = [(0, 2), (15, 2), (15, 5), (3, 5), (3, 8), (19, 8)]
WAYPOINTS_GRID_2 = [(0,1), (16,1), (16,3), (4,3), (4,6), (16,6), (16,8), (19,8)]
WAYPOINTS_GRID_3 = [(0,0), (19,0), (19,2), (1,2), (1,4), (19,4), (19,6), (1,6), (1,9), (19,9)]

# Economy
START_GOLD = 150
START_LIVES = 10

# Tower stats
TOWER_STATS = {
    'gunner': {
        'cost': 50, 'damage': 10, 'range': 60, 'cooldown': 0.3,
        'proj_speed': 220, 'color': (80, 200, 120),
        'outline_color': (43, 111, 68), 'highlight_color': (163, 232, 192)
    },
    'cannon': {
        'cost': 100, 'damage': 20, 'range': 50, 'cooldown': 1.2,
        'proj_speed': 140, 'splash_radius': 24, 'color': (220, 140, 60),
        'outline_color': (138, 85, 31), 'highlight_color': (245, 200, 150)
    },
    'frost': {
        'cost': 75, 'damage': 4, 'range': 55, 'cooldown': 0.8,
        'proj_speed': 200, 'slow_mult': 0.5, 'slow_duration': 2.0, 'color': (100, 180, 230),
        'outline_color': (51, 110, 143), 'highlight_color': (185, 226, 250)
    }
}

# Enemy stats
ENEMY_STATS = {
    'walker': {
        'hp': 30, 'speed': 40, 'reward': 5, 'radius': 4, 'color': (220, 60, 60),
        'outline_color': (140, 36, 36), 'highlight_color': (242, 155, 155)
    },
    'armored': {
        'hp': 90, 'speed': 25, 'reward': 12, 'radius': 5, 'color': (150, 40, 40),
        'outline_color': (92, 23, 23), 'highlight_color': (197, 101, 101)
    }
}

EYE_COLOR = (26, 26, 26)

from waves import WAVES

WAVES_LEVEL2 = [
    {"enemies": ["walker"]*10,                          "interval": 0.9},
    {"enemies": ["walker"]*8  + ["armored"]*4,          "interval": 0.8},
    {"enemies": ["walker"]*10 + ["armored"]*6,          "interval": 0.7},
    {"enemies": ["walker"]*8  + ["armored"]*10,         "interval": 0.6},
    {"enemies": ["walker"]*12 + ["armored"]*12,         "interval": 0.5},
]

WAVES_LEVEL3 = [
    {"enemies": ["walker"]*12 + ["armored"]*6,          "interval": 0.8},
    {"enemies": ["walker"]*10 + ["armored"]*10,         "interval": 0.7},
    {"enemies": ["walker"]*14 + ["armored"]*10,         "interval": 0.6},
    {"enemies": ["walker"]*10 + ["armored"]*16,         "interval": 0.55},
    {"enemies": ["walker"]*16 + ["armored"]*16,         "interval": 0.5},
    {"enemies": ["walker"]*14 + ["armored"]*20,         "interval": 0.45},
]

LEVELS = [
    {"path": WAYPOINTS_GRID,   "waves": WAVES,        "enemy_mult": {"hp": 1.0, "speed": 1.0}},
    {"path": WAYPOINTS_GRID_2, "waves": WAVES_LEVEL2,  "enemy_mult": {"hp": 1.4, "speed": 1.15}},
    {"path": WAYPOINTS_GRID_3, "waves": WAVES_LEVEL3,  "enemy_mult": {"hp": 1.8, "speed": 1.3}},
]
