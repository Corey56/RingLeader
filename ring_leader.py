"""
Ring Leader
"""

import pgzrun
from pygame.time import Clock

from ship import *
from bubble import *
from score import *

# Configuration Constants-------------------------------------------------------
BOARD_HEIGHT = 20 #Height of screen in Bubbles
# Total Width of the screen based on bubbles
WIDTH = (Bubble.BUBBLE_DIAMETER * Bubble_Grid.BOARD_WIDTH 
         + Bubble_Grid.BUBBLE_PADDING * (Bubble_Grid.BOARD_WIDTH-1) 
         + Bubble_Grid.MARGINS * 2)
# Total Height of the screen based on bubbles
HEIGHT = (Bubble.BUBBLE_DIAMETER*BOARD_HEIGHT 
          + Bubble_Grid.BUBBLE_PADDING * BOARD_HEIGHT)

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

# Procedure starts / restarts the game when the 'r' key is pressed
def initalize_game():
    global bubble_grid, droppers, ship, bullets, score, \
           new_level_msg,\
           game_state, level, level_colors, c\
    
    bubble_grid = Bubble_Grid(COLOR_LEVELS[0])
    # list of all bubbles broken free from grid and falling 
    droppers = Dropper_List()
    # List of bullets fired from the player's ship
    bullets = Bullet_List()
    level_colors = COLOR_LEVELS[0] #start with 3 colors and increase
    ship = Ship((WIDTH // 2 + Bubble.BUBBLE_DIAMETER // 2, 
                 HEIGHT - 2*Bubble.BUBBLE_DIAMETER),
                 COLOR_LEVELS[0],
                 Bubble.BUBBLE_DIAMETER,
                 Ship.SHIP_ACCEL*Bubble.BUBBLE_DIAMETER)
    # Displayed briefly on screen when points are earned/lost
    score = Score(500)
    game_state = 1 #1: Normal Play, 0: Game Over, 3: Paused, 5: Instruction 
    level = 1 # Levels progresses with player score
    new_level_msg = None # Displayed briefly at level changes
    c = Clock()

initalize_game()

# PGZero's global draw() function
def draw():
    screen.fill(BLACK) # Background
    bubble_grid.draw(screen)
    ship.draw(screen)
    bullets.draw(screen)
    droppers.draw(screen)
    score.draw(screen, HEIGHT, WIDTH)
    if new_level_msg: # Briefly introduce changes for a level
        screen.draw.text(new_level_msg , centery=(HEIGHT//4), centerx=WIDTH//2)
    if not game_state:
        screen.draw.text(GAME_OVER_MSG , centery=HEIGHT//2, centerx=WIDTH//2)
    elif game_state == 3:
        screen.draw.text(PAUSE_MESSAGE, centery=HEIGHT//2, centerx=WIDTH//2)
    elif game_state == 5:
        screen.fill(BLACK) # Declutter for redaing instructions
        screen.draw.text(INSTRUCTIONS, topleft=(350,150))

# PGZero's global update game loop
def update():
    global game_state, droppers, score
    delta = c.tick()
    
    if game_state == 1: # Normal Game Play
        bullets.move(delta)
        score += bullets.check_bounds(HEIGHT, WIDTH)
        bullets.delete_strikers(bubble_grid)
        droppers.move(delta)
        score += droppers.check_bounds(HEIGHT)
        droppers.delete_landers(bubble_grid)
        ship.final_radius += Dropper.HIT_GROW * droppers.num_strikers(ship)
        bubble_grid.prune_bottom_row(HEIGHT)
        bubble_grid.addTopRow()
        bubble_grid.move(delta)
        score += bubble_grid.erase_matches()
        droppers += bubble_grid.drop_loose_bubbles()
        ship.update(delta, keyboard, keys, WIDTH, HEIGHT)
        if bubble_grid.collide(ship.x, ship.y, ship.current_radius):
            game_state = 0
        score.update(delta, HEIGHT)
        if score.is_new_level(): # Triger level change
            next_level()

def on_mouse_move (pos):
    ship.cross.pos = pos

def on_mouse_down (pos, button):
    global bullets
    if mouse.LEFT == button:
        bullets += Bullet(ship.x, ship.y, ship.get_color(), ship.get_angle(pos))
    if mouse.RIGHT == button:
        bubble_grid.speed_rows += 1

def on_key_down(key):
    global game_state
    if key == keys.SPACE:
        ship.cycle_color()
    if key == keys.P:
        if game_state == 3:
            game_state = 1
        elif game_state == 1:
            game_state = 3
    if key == keys.R:
        initalize_game()
    if key == keys.I:
        if game_state == 3:
            game_state = 5
        elif game_state == 5:
            game_state = 3

def next_level():
    global level, bubble_grid, bullets, \
        droppers, new_level_msg, level_colors, score
    
    droppers = Dropper_List()
    bullets = Bullet_List()
    ship.reset_hull_size()
    level += 1
    score.next_level_points += 250 * level
    
    new_level_msg = f"Level {level}\nBubble Creation Rate +10%"
    
    if level == 5:
        level_colors = COLOR_LEVELS[1]
        new_level_msg += "\nNew Color Added!"
        ship.set_colors(level_colors)
    elif level == 10:
        level_colors = COLOR_LEVELS[2]
        new_level_msg += "\nNew Color Added!"
        ship.set_colors(level_colors)

    bubble_grid = Bubble_Grid(level_colors, bubble_grid.velocity * 1.1)
    clock.schedule(clear_new_level_msg, 10.0)

def clear_new_level_msg():
    global new_level_msg
    new_level_msg = None

pgzrun.go()