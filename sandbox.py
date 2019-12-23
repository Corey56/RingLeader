"""
Ring Leader
"""

import pgzrun

from ship import Ship
from pygame.time import Clock

# Configuration Constants-------------------------------------------------------
BUBBLE_DIAMETER = 32 #Diameter of a Grid Bubble in pixels
BUBBLE_PADDING = 4 #Vertical and Horizontal space between grid bubbles in pixels

COLOR_LEVELS = [[(173, 207, 25),(25, 207, 195),(186, 25, 207)], # 3 color
           [(207, 195, 25),(25, 207, 55),(25, 70, 207),(198, 25, 207)], #4 color
  [(199, 196, 28),(37, 199, 28),(28, 199, 193),(65, 28, 199),(199, 28, 188)]] #5


WIDTH = 1280
HEIGHT = 720

PURP = (62, 7, 120)   # Ship perimeter color
BLACK = (0,0,0)       # Background Color
FLAME = (237, 150, 9) # Ship Thruster Color

BULLET_VELOCITY = .02 * BUBBLE_DIAMETER # constant speed of a fired bullet
HIT_GROW = BUBBLE_DIAMETER//4 #Ship growth when struck by a falling bubble

SHIP_ACCEL = .0003 # When W,A,S,D depressed, speedup this much, decel on release

# Global Data Structures--------------------------------------------------------
# pos, color_list, bubble_diameter, accel
ship = Ship((WIDTH // 2 + BUBBLE_DIAMETER // 2, HEIGHT - 2*BUBBLE_DIAMETER),
             COLOR_LEVELS[0],
             BUBBLE_DIAMETER,
             SHIP_ACCEL*BUBBLE_DIAMETER)


#print(ship)
c = Clock()

# PGZero's global draw() function
def draw():
    screen.fill(BLACK) # Background
    ship.draw(screen)
    
# PGZero's global update game loop
def update():
    ship.update(c.tick(), keyboard, keys, WIDTH, HEIGHT)

pgzrun.go()