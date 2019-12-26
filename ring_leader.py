"""
Ring Leader
"""

import pgzrun
from math import sin, cos, atan2
from pygame.time import Clock

from ship import Ship
from bubble import Bubble_Grid, Bubble_List, Bubble, Bullet, Dropper, distance

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
BULLET_VELOCITY = .02 * Bubble.BUBBLE_DIAMETER # constant speed of a fired bullet
HIT_GROW = Bubble.BUBBLE_DIAMETER//4 #Ship growth when struck by a falling bubble
SCORE_VELOCITY = -.02 # Constant upward movement of score alerts
SCORE_DURATION = 40 # Update cycles to display score alerts
SHIP_ACCEL = .0003 # When W,A,S,D depressed, speedup this much, decel on release
BUBBLE_GRAVITY = .00028 # When a bubble drops off the grid accellerate downward
FALLING_BUBBLE_POINTS = 4 # Points received for a falling bubble
LOST_BULLET_PENALTY = -4 # Points lost for an errant bullet

# Global Data Structures--------------------------------------------------------
bubble_grid = Bubble_Grid(COLOR_LEVELS[0])
# list of all bubbles broken free from grid and falling 
droppers = Bubble_List()
# List of bullets fired from the player's ship
bullets = Bubble_List()

level_colors = COLOR_LEVELS[0] #start with 3 colors and increase

ship = Ship((WIDTH // 2 + Bubble.BUBBLE_DIAMETER // 2, 
             HEIGHT - 2*Bubble.BUBBLE_DIAMETER),
             COLOR_LEVELS[0],
             Bubble.BUBBLE_DIAMETER,
             SHIP_ACCEL*Bubble.BUBBLE_DIAMETER)
# Displayed briefly on screen when points are earned/lost
score_alerts = [] #[[x_pos, y_pos, msg, duration, velocity], ...more alerts]
cross_hair = (0,0) #starts here and follows mouse
score = 0
combo_bullets = 0 #global for counting user bullets in combos
combo_bubbles = 0 #global to track if matched bubbles score points
game_state = 1 #1: Normal Play, 0: Game Over, 3: Paused, 5: Instruction Screen
level = 1 # Levels progresses with player score
next_level_points = 500 # To get to level 2
new_level_msg = None # Displayed briefly at level changes
c = Clock()
delta = [0]
speed_rows = Bubble_Grid.MATCH_LENGTH

# PGZero's global draw() function
def draw():
    screen.fill(BLACK) # Background
    bubble_grid.draw(screen)
    ship.draw(screen)
    bullets.draw(screen)
    droppers.draw(screen)
    draw_cross_hair()
    draw_score_alerts()
    # Draws the score and next level threshold in bottom left 
    screen.draw.text(str(int(score))+'/'+str(next_level_points)
                     , bottomleft=(10, HEIGHT-10))
    if new_level_msg: # Briefly introduce changes for a level
        screen.draw.text(new_level_msg , centery=(HEIGHT//4), centerx=WIDTH//2)
    if not game_state:
        screen.draw.text(GAME_OVER_MSG , centery=HEIGHT//2, centerx=WIDTH//2)
    elif game_state == 3:
        screen.draw.text(PAUSE_MESSAGE, centery=HEIGHT//2, centerx=WIDTH//2)
    elif game_state == 5:
        screen.fill(BLACK) # Declutter for redaing instructions
        screen.draw.text(INSTRUCTIONS, topleft=(350,150))

# Procedure draws score message pop-ups 
def draw_score_alerts():
    for s in score_alerts:
        #[[x_pos, y_pos, msg, duration, velocity], ...more alerts]
        x,y,m = s[0],s[1],s[2]
        if x > WIDTH: #Off screen to right, adjust
            screen.draw.text(f'{m:+d}', midright=(WIDTH, y))
        elif x < 0: #Off screen to left, adjust
            screen.draw.text(f'{m:+d}', midleft=(0, y))
        else:
            screen.draw.text(f'{m:+d}', midtop=(x, y))

# Procedure draws cross hairs to match player selected bullet color
def draw_cross_hair():
    x, y = cross_hair
    c = ship.get_color()
    b = Bubble.BUBBLE_DIAMETER
    screen.draw.line((x-b//2, y), (x-b//4, y), c)
    screen.draw.line((x+b//2, y), (x+b//4, y), c)
    screen.draw.line((x, y-b//2), (x, y-b//4), c)
    screen.draw.line((x, y+b//2), (x, y+b//4), c)

# PGZero's global update game loop
def update():
    delta[0] = c.tick()
    if game_state == 1: # Normal Game Play
        update_bullets()
        update_droppers()
        update_kill_bubbles()
        ship.update(delta[0], keyboard, keys, WIDTH, HEIGHT)
        update_score_alerts()
        if score >= next_level_points: # Triger level change
            next_level()

# Updates the movement and lifecycle of score alerts
#  Modifies the global score_alerts list
def update_score_alerts():
    #[[x_pos, y_pos, msg, duration, velocity], ...more alerts]
    cnt = 0
    while cnt < len(score_alerts):
        score_alerts[cnt][3] -= 1 # Decrement time to live
        if score_alerts[cnt][1] > HEIGHT: # Move low alerts up on to screen
            score_alerts[cnt][1] = HEIGHT-5
        elif score_alerts[cnt][1] < 5: # Move high alerts down 
            score_alerts[cnt][1] = 5
            score_alerts[cnt][4] *= -1 # And make them float down instead of up
        score_alerts[cnt][1] += score_alerts[cnt][4]*delta[0] # Float up slowly
        if score_alerts[cnt][3] < 0: # Time expired
            del score_alerts[cnt]
        else:
            cnt += 1

# Procedure updates player fired bullets
# Modifies global bullets list when bullets fly off screen or strike bubble grid
# Modifies global score to penalize player for errant bullets
# Calls the bullet_collide function do determine if a bullet strikes the KB grid
def update_bullets():
    global score
    cnt = 0
    #[[x_pos, y_pos, angle, color], ...more bullets]
    while cnt < len(bullets):
        b = bullets[cnt]
        new_x = b.x + BULLET_VELOCITY * cos(b.angle) * delta[0] # x vector change
        new_y = b.y - BULLET_VELOCITY * sin(b.angle) * delta[0] # y vector change
        
        # Check for bullet off screen
        if new_x > WIDTH or new_x < 0 or new_y > HEIGHT or new_y < 0:
            score_alerts.append([new_x, new_y, LOST_BULLET_PENALTY, 
                                 SCORE_DURATION, SCORE_VELOCITY])
            score += LOST_BULLET_PENALTY
            if score < 0: # Don't drop score below 0
                score = 0
            del bullets[cnt]
        elif bullet_collide(new_x, new_y, b.color): # Check for collision with grid
            del bullets[cnt]
        else: # Otherwise, move this bullet in it's direction of travel
            bullets[cnt].x = new_x
            bullets[cnt].y = new_y
            cnt += 1

# Function takes the coordinates of bullet and returns true if the bullet
#  colides with the kill bubble grid.
# Returns true for collision and False otherwise. Uses is_close() and distance()
#  to verify collision and find the nearest kill bubble.
# If the bullet collides with a kill bubble assimilate_bullet() is called to add
#  the bullet to the kill bubble grid.
def bullet_collide(x, y, c):
    close_bubble = None #(i,j,dist)
    for i, row in enumerate(bubble_grid):
        for j, b in enumerate(row):
            # Use is_close() to find potential matches (city block distance)
            if b.color and is_close(x, y, b.x, b.y, Bubble.BUBBLE_DIAMETER):
                # Use euclidian distance for precision
                d = distance(x, y, b.x, b.y)
                if d < Bubble.BUBBLE_DIAMETER:
                    # find the closest bubble if multiple in range
                    if close_bubble:
                        if d < close_bubble[2]:
                            close_bubble = (i,j,d)
                    else:
                        close_bubble = (i,j,d)

    if close_bubble: # collided with this kill bubble
        n = bubble_grid.findNearestSpot(x, y, close_bubble[0], close_bubble[1])
        bubble_grid.addGridBubble(*n, c)
        #assimilate_bullet(x, y, c, close_bubble) #add bubble to kill grid
        return True
    return False

# Function computes lightweight city block proximity given 2 coordinates and a 
#  distance. Returns true if the two points are closer or equal to distance.
def is_close(x1, y1, x2, y2, d):
    if abs(y1-y2) <= d and abs(x1-x2) <= d:
        return True
    return False

# Function returns boolean indicating if the player's ship collides with the 
#  kill bubble grid or a falling bubble given a coordinate and a flag which
#  indicates if the ship should grow or die. Falling bubbles cause groth and
#  grid bubbles cause death.
# Modifies the global ship_radius on collision with falling bubble
# Modifies the global game_state on collision with bubble grid
def hit_ship(x, y, g):
    global game_state
    kill_zone = ship.current_radius+Bubble.BUBBLE_DIAMETER//2
    sx, sy = ship.x, ship.y
    if is_close(sx, sy, x, y, kill_zone):
        d = distance(sx, sy, x, y)
        if d < kill_zone:
            if g:
                ship.final_radius += HIT_GROW
            else:
                game_state = 0
            return True
    return False

# Procedure updates kill bubble grid.
# 1. Remove the bottom row of bubbles if off screen
# 2. Call add_bubble_row() to add a new row of kill bubbles at top if needed
# 3. Call hit_ship() to end the game if any kill bubbles strike player ship
# 4. Move all bubbles downward by global bubble_velocity.
# 5. Call delete_bubble_matches() to match any bubbles of same color chains
# 6. Call drop_loose_bubbles() to drop bubbles not connected to top row of grid
# Modifies global kill_bubbles
def update_kill_bubbles():
    global speed_rows, droppers
    
    if bubble_grid and bubble_grid[0][0].y > HEIGHT + Bubble.BUBBLE_DIAMETER//2:
        del bubble_grid[0] # fell off screen
        
    # add a new row at top of screen
    if not bubble_grid or \
           bubble_grid[-1][0].y >= Bubble.BUBBLE_DIAMETER//2 \
                                   + Bubble_Grid.BUBBLE_PADDING:
        
        if speed_rows: # speed out a few rows at level begining
            speed_rows -=1

        bubble_grid.addTopRow()

    delta_y = bubble_grid.velocity * delta[0]
    if speed_rows:
        delta_y *= 16
    for row in bubble_grid:
        for b in row:
            if b.color: # Only bubbles with a color 'exist'
                hit_ship(b.x, b.y, False)
            
            b.y += delta_y
            
    delete_bubble_matches()
    
    droppers += bubble_grid.drop_loose_bubbles()

# Procedure updates falling bubbles which may fall off the screen, hit the 
#  player's ship, or land back on the kill bubble grid. Points are awarded for
#  falling bubbles leaving the screen.  All falling bubbles accelerate downward
#  away from the grid location from which they fell.
# Calls hit_ship() and falling_bubble_lands() to determine colisions.
# Modifies globals score and falling_bubbles
def update_droppers():
    #[[x_pos, y_pos, color, vely, column], ...more droppers]
    global score
    cnt = 0
    while cnt < len(droppers):
        fb = droppers[cnt]
        if fb.y > HEIGHT: # fell off screen. Award points and remove
            score += FALLING_BUBBLE_POINTS
            score_alerts.append([fb.x, fb.y, FALLING_BUBBLE_POINTS, 
                                 SCORE_DURATION, SCORE_VELOCITY])
            del droppers[cnt]
        
        # struck the ship or landed back on the kill bubble grid
        elif hit_ship(fb.x,fb.y, True) or falling_bubble_lands(fb):
            del droppers[cnt]
        
        else: # accelerate normally downward
            droppers[cnt].y += fb.vely * delta[0]
            droppers[cnt].vely += BUBBLE_GRAVITY * delta[0]
            cnt += 1

# Function returns True if a falling bubble lands on the kill bubble grid and 
#  false otherwise.
def falling_bubble_lands(fb):
    y, c, j = fb.y, fb.color, fb.column
    d = Bubble.BUBBLE_DIAMETER + Bubble_Grid.BUBBLE_PADDING
    for i, row in enumerate(bubble_grid):
        b = row[j] # only check in the faller's column
        if b.color and abs(b.y - y) <= d:
            bubble_grid[i+1][j].color = c
            return True
    return False

def delete_bubble_matches():
    global score, combo_bullets, combo_bubbles
    
    if not bubble_grid:
        return
    
    matches = bubble_grid.get_matches()

    for i, j in matches:
        combo_bullets = 0
        combo_bubbles = 0
        rec_erase(i,j)
        if combo_bullets and combo_bubbles:
            bonus = 2**combo_bubbles
            score_diff = next_level_points - score
            if bonus > score_diff:
                bonus = score_diff
            score += bonus
            x, y = bubble_grid[i][j].x, bubble_grid[i][j].y
            score_alerts.append([x, y, bonus, 
                                 SCORE_DURATION, SCORE_VELOCITY])

def rec_erase(i,j):
    global combo_bubbles, combo_bullets
    
    c = bubble_grid[i][j].color
    
    if not c:
        return    

    if bubble_grid[i][j].bulletFlag:
        combo_bullets += 1
    else:
        combo_bubbles += 1
    
    bubble_grid[i][j].color = None
    
    n = ((i+1,j), (i-1,j), (i, j+1), (i, j-1))
    for nei in n:
        i, j = nei
        if (i in range(len(bubble_grid)) 
                and j in range(Bubble_Grid.BOARD_WIDTH)
                and bubble_grid[i][j].color == c):
            rec_erase(i, j)

def on_mouse_move (pos):
    global cross_hair
    cross_hair = pos

def on_mouse_down (pos, button):
    global bubble_velocity, speed_rows, bullets
    if mouse.LEFT == button:
        bullets += Bullet(ship.x, ship.y, ship.get_color(), get_angle(pos))
    if mouse.RIGHT == button:
        speed_rows += 1

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

def get_angle(pos):
    return atan2(ship.y - pos[1], - (ship.x - pos[0]))

def next_level():
    global level, bubble_velocity, bubble_grid, bullets, next_level_points, \
        droppers, new_level_msg, speed_rows, level_colors
    
    droppers = Bubble_List()
    bullets = Bubble_List()
    ship.reset_hull_size()
    level += 1
    speed_rows = Bubble_Grid.MATCH_LENGTH
    next_level_points += 250 * level
    
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
    
# Procedure Restarts the game when the 'r' key is pressed
def initalize_game():
    global bubble_grid, droppers, ship, bullets, score, speed_rows, \
           game_state, level, next_level_points, level_colors\
    
    level_colors = COLOR_LEVELS[0]    
    droppers = Bubble_List()
    bullets = Bubble_List()
    bubble_grid = Bubble_Grid(level_colors)
    ship = Ship((WIDTH // 2 + Bubble.BUBBLE_DIAMETER // 2, 
                 HEIGHT - 2*Bubble.BUBBLE_DIAMETER),
                 level_colors,
                 Bubble.BUBBLE_DIAMETER,
                 SHIP_ACCEL*Bubble.BUBBLE_DIAMETER)
    score = 0
    game_state = 1
    level = 1 
    next_level_points = 500    
    new_level_msg = None 
    speed_rows = Bubble_Grid.MATCH_LENGTH

pgzrun.go()