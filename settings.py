"""
Project settings for the minimal Minesweeper.
All game configuration and color constants live here.
"""

# Field
WIDTH = 10
HEIGHT = 10
MINES = 10

# UI layout
CELL = 36
MARGIN = 16
TOPBAR = 56
SCREEN_W = MARGIN * 2 + WIDTH * CELL
SCREEN_H = TOPBAR + MARGIN * 2 + HEIGHT * CELL
SCREEN_SIZE = (SCREEN_W, SCREEN_H)

# Colors
BG = (200, 200, 200)       # gray background
TOP_BG = (170, 170, 170)   # top bar gray
COVER = (160, 160, 160)    # covered cell (gray)
OPEN = (220, 220, 220)     # opened cell (lighter gray for contrast)
FLAG = (200, 40, 40)       # flag
MINE = (10, 10, 10)        # mine
GRID = (100, 100, 100)
NUM_COLOR = (30, 30, 30)

# colors for numbers (classic minesweeper mapping)
NUM_COLORS = {
    1: (0, 0, 255),
    2: (0, 128, 0),
    3: (255, 0, 0),
    4: (0, 0, 128),
    5: (128, 0, 0),
    6: (0, 128, 128),
    7: (0, 0, 0),
    8: (128, 128, 128),
}
