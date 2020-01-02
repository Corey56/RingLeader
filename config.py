"""
This module contains configuration constants for the ring leader game and 
 composite classes.
"""
BUBBLE_PADDING = 4 # Distance between grid bubbles (pix)
BOARD_WIDTH = 28  # Bubbles wide game board
MARGINS = 10 # dist between grid and horizontal screen edge
MATCH_LENGTH = 4 # Bubbles in a row to match
INITIAL_BUBBLE_VELOCITY = .0032 # fall of new bubbles from top (pix/ms)
#Alert
SCORE_VELOCITY = -.02 # Constant upward movement of score alerts (pix/ms)
SCORE_DURATION = 1 # Seconds to display score alerts
#Bubble
BUBBLE_DIAMETER = 32 # Diameter of all buubles in pix
#Bullet
BULLET_VELOCITY = .64   # speed of a fired bullet (pix/ms)
LOST_BULLET_PENALTY = 4 # Points lost for an errant bullet
#Dropper
BUBBLE_GRAVITY = .0003    # accellerate downward (pix/ms**2)
FALLING_BUBBLE_POINTS = 4 # Points received for a falling bubble
#Ship
PURP = (62, 7, 120)   # Ship perimeter color
FLAME = (237, 150, 9) # Ship Thruster Color
SHIP_ACCEL = .00048        # Acceleration on key hold
HULL_RADIUS = 32      # in pix
HIT_GROW = 8          # ship growth when struck by a falling bubble (pix)

BOARD_HEIGHT = 20 #Height of screen in Bubbles
# Total Width of the screen based on bubbles
WIDTH = (BUBBLE_DIAMETER * BOARD_WIDTH
         + BUBBLE_PADDING * (BOARD_WIDTH-1)
         + MARGINS * 2)
# Total Height of the screen based on bubbles
HEIGHT = (BUBBLE_DIAMETER*BOARD_HEIGHT
          + BUBBLE_PADDING * BOARD_HEIGHT)

BLACK = (0,0,0)       # Background Color

#Multiline String Games message constants
PAUSE_MESSAGE = """PAUSED
(unpause with 'p' key)
(restart with 'r' key)
(view instructions with i)"""
INSTRUCTIONS = """Controls
- Maneuver Ship with W,A,S,D
- Aim with mouse and crosshairs
- Left Mouse Button Fires Bubbles
- Space Bar cycles available colors
- Right click to speed out the next row
- p to pause game
- r to restart game

Gameplay
- Fire bubbles to make rows and columns of
  4 consecutive bubbles of the same color.
- Maneuver your ship to avoid all Bubbles.
- Bubbles creeping downward will destroy your ship on contact.
- Falling bubbles which strike your ship will cause it to grow.

Scoring
- Awarded points scale exponentially with the number
  of bubbles popped in a single combo. Bubbles created
  by player bullets do not score points.
- You cannot score more points than required to reach
  the next level with a combo.
- Points are awarded for any falling bubbles
  which do not strike the player's vessel.
- Points are deducted for any bullets which fly out of bounds.

Press 'I' to return to pause screen"""
GAME_OVER_MSG = """GAME OVER
press 'r' to play again"""

# 3, 4, 5 color lists for difficulty level
COLOR_LEVELS = [[(173, 207, 25),(25, 207, 195),(186, 25, 207)], # 3 color
           [(207, 195, 25),(25, 207, 55),(25, 70, 207),(198, 25, 207)], #4 color
  [(199, 196, 28),(37, 199, 28),(28, 199, 193),(65, 28, 199),(199, 28, 188)]] #5