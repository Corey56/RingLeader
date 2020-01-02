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
                   PAUSE_MESSAGE, INSTRUCTIONS, GAME_OVER_MSG

# Procedure starts / restarts the game when the 'r' key is pressed
def initalize_game():
    global bubble_grid, droppers, ship, bullets, score, new_level_msg,\
           game_state, level, level_colors, c

    bubble_grid = Bubble_Grid(COLOR_LEVELS[0])
    # list of all bubbles broken free from grid and falling
    droppers = Dropper_List()
    # List of bullets fired from the player's ship
    bullets = Bullet_List()
    level_colors = COLOR_LEVELS[0] #start with 3 colors and increase
    ship = Ship((WIDTH // 2, HEIGHT - 2*HULL_RADIUS), COLOR_LEVELS[0])
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
    score.draw(screen)
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
            game_state = 0
        score.update(delta)
        if score.is_new_level(): # Triger level change
            next_level()

def on_mouse_move(pos):
    ship.cross.pos = pos

def on_mouse_down(pos, button):
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
    global level, bubble_grid, bullets, droppers, new_level_msg, level_colors, \
           score

    droppers = Dropper_List()
    bullets = Bullet_List()
    ship.reset_hull_size()
    level += 1
    score.next_level_points += 250 * level

    new_level_msg = f"Level {level}"
    
    if level == 5:
        level_colors = COLOR_LEVELS[1]
        new_level_msg += "\nBubble Creation Rate -20%\nNew Color Added!"
        ship.set_colors(level_colors)
        bubble_grid = Bubble_Grid(level_colors, bubble_grid.velocity * .8)
    elif level == 10:
        level_colors = COLOR_LEVELS[2]
        new_level_msg += "\nBubble Creation Rate -20%\nNew Color Added!"
        ship.set_colors(level_colors)
        bubble_grid = Bubble_Grid(level_colors, bubble_grid.velocity * .8)
    else:
        new_level_msg += "\nBubble Creation Rate +10%"
        bubble_grid = Bubble_Grid(level_colors, bubble_grid.velocity * 1.1)

    
    clock.schedule(clear_new_level_msg, 10.0)

def clear_new_level_msg():
    global new_level_msg
    new_level_msg = None

pgzrun.go()