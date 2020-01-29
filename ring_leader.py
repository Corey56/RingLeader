"""
This file contains the Ring Leader game which has the following dependencies.
- PGZero package
- dist.py
- score.py
- bubble.py
- ship.py
- config.py

- Install Dependencies: `pip install pgzero`
- Play the game: `python ring_leader.py`
- Press 'p' to pause and then 'i' to view instructions.
"""

import pgzrun
from pygame.time import Clock

from ship import Ship
from bubble import Bubble_Grid, Bullet_List, Dropper_List, Bullet
from score import Score
from config import HEIGHT, WIDTH, COLOR_LEVELS, HULL_RADIUS, BLACK, \
                   PAUSE_MESSAGE, INSTRUCTIONS, GAME_OVER_MSG, INTRODUCTION

def initalize_game():
    """
    Procedure starts / restarts the game when the 'r' key is pressed
    """
    global bubble_grid, droppers, ship, bullets, score, new_level_msg, \
           game_state, level, level_colors, c

    # Bubbles creeping downward from top of screen
    bubble_grid = Bubble_Grid(COLOR_LEVELS[0])
    # list of all bubbles broken free from grid and falling
    droppers = Dropper_List()
    # List of bullets fired from the player's ship
    bullets = Bullet_List()
    # List of RGB tuples tracks the number of colors in the game currently
    level_colors = COLOR_LEVELS[0]
    # Player's ship 
    ship = Ship((WIDTH // 2, HEIGHT - 2*HULL_RADIUS), COLOR_LEVELS[0])
    # Tracks the player's score
    score = Score(500)
    #1: Normal Play, 0: Game Over, 3: Paused, 5: Instruction, 6: Introduction
    game_state = 6 
    # Levels progresses with player score
    level = 1
    # Briefly displayed at level up
    new_level_msg = None
    # PYGame object used to scale movements with time
    c = Clock()

initalize_game()

def draw():
    """
    PGZero's global draw() function
    """
    screen.fill(BLACK) # Background
    bubble_grid.draw(screen)
    ship.draw(screen)
    bullets.draw(screen)
    droppers.draw(screen)
    score.draw(screen)
    if new_level_msg:      # Briefly introduce changes for a level
        screen.draw.text(new_level_msg , centery=(HEIGHT//4), centerx=WIDTH//2)
    if not game_state:     # Game Over
        screen.draw.text(GAME_OVER_MSG , centery=HEIGHT//2, centerx=WIDTH//2)
    elif game_state == 3:  # Game Paused
        screen.draw.text(PAUSE_MESSAGE, centery=HEIGHT//2, centerx=WIDTH//2)
    elif game_state == 5:  # Instruction Screen
        screen.fill(BLACK) # Declutter for reading instructions
        screen.draw.text(INSTRUCTIONS, topleft=(350,150))
    elif game_state == 6:  # Introduction Screen
        screen.fill(BLACK) # Declutter for reading introduction
        screen.draw.text(INTRODUCTION, topleft=(350,150))


def update():
    """
    PGZero's global update game loop
    """
    global game_state, droppers, score
    delta = c.tick() # Time in ms since last update

    if game_state == 1: # Normal Game Play
        bullets.move(delta)
        score += bullets.check_bounds()
        bullets.delete_strikers(bubble_grid)
        droppers.move(delta)
        score += droppers.check_bounds()
        droppers.land(bubble_grid)
        droppers.strike(ship)
        bubble_grid.prune_bottom_row()
        bubble_grid.addTopRow()
        bubble_grid.move(delta)
        score += bubble_grid.erase_matches()
        droppers += bubble_grid.drop_loose_bubbles()
        ship.update(delta, keyboard, keys)
        if bubble_grid.collide(ship.x, ship.y, ship.current_radius):
            game_state = 0 # Game Over
        score.update(delta)
        if score.is_new_level(): # Triger level change
            next_level()

def on_mouse_move(pos):
    """
    PGZero hook procedure. Cross-hairs follow mouse movements
    """
    ship.cross.pos = pos

def on_mouse_down(pos, button):
    """
    PGZero hook procedure. 
    LMB: Fire Bullet
    RMB: Rush out a new Bubble_Row
    """
    global bullets
    if mouse.LEFT == button:
        bullets += Bullet(ship.x, ship.y, ship.get_color(), ship.get_angle(pos))
    if mouse.RIGHT == button:
        bubble_grid.speed_rows += 1

def on_key_down(key):
    """
    PGZero hook procedure. 
    SPACE: Cycle Ship's Bullet Color
    P:     Pause/Unpause the game
    R:     Restart the game
    I:     Move between Pause and Instruction screens
    """
    global game_state
    if key == keys.SPACE:
        if game_state == 6:
            game_state == 1
        elif game_state == 1:
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
        elif game_state == 6:
            game_state = 3

def next_level():
    """
    Procedure trigered when player score reaches next_level_points. Sets 
     conditions for next level.
    """
    global level, bubble_grid, bullets, droppers, new_level_msg, level_colors, \
           score

    droppers = Dropper_List()
    bullets = Bullet_List()
    ship.reset_hull_size()
    level += 1
    score.next_level_points += 250 * level

    new_level_msg = f"Level {level}"
    
    if level == 5:    # Add new color to increase difficulty
        level_colors = COLOR_LEVELS[1]
        new_level_msg += "\nBubble Creation Rate -20%\nNew Color Added!"
        ship.set_colors(level_colors)
        # Slow down bubble grid
        bubble_grid = Bubble_Grid(level_colors, bubble_grid.velocity * .8)
    elif level == 10: # Add new color to increase difficulty
        level_colors = COLOR_LEVELS[2]
        new_level_msg += "\nBubble Creation Rate -20%\nNew Color Added!"
        ship.set_colors(level_colors)
        # Slow down bubble grid
        bubble_grid = Bubble_Grid(level_colors, bubble_grid.velocity * .8)
    else: # Speed up bubble creation by 10%
        new_level_msg += "\nBubble Creation Rate +10%"
        bubble_grid = Bubble_Grid(level_colors, bubble_grid.velocity * 1.1)

    # Schedule New Level Message to disappear in 8 seconds
    clock.schedule(clear_new_level_msg, 8.0)

def clear_new_level_msg():
    """
    Procedure clears new level message when it expires
    """
    global new_level_msg
    new_level_msg = None

# PGZero method starts game
pgzrun.go()