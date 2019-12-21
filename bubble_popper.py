"""
Bubble Popper
MAJ Crosser

Based on a conversation with CDT Robert Sewell about a game he once played on 
his phone.

Planned Improvements
- Structure
    - Looping through same data structures repetitously?
    - Move to OOP
    - Move to PYGame

- Game Play
    - Pausing Game pauses level message
    - Choice of 3 random powerups for catching falling bubbles

- Animations
    - Falling wiggle
    - Landing Squash
    - Exploding match bubble
    - Dying ship
"""

import pgzrun
import random
import math
from pygame.time import Clock

# Configuration Constants-------------------------------------------------------
BUBBLE_DIAMETER = 32 #Diameter of a Grid Bubble in pixels
BUBBLE_PADDING = 4 #Vertical and Horizontal space between grid bubbles in pixels
BOARD_HEIGHT = 20 #Height of screen in Bubbles
BOARD_WIDTH = 28 #Width of screen in bubbles
MARGINS = 10 #distance between horizontal edges and 1st, last bubble in a row
#Inital Fall fall/spawn speed of grid bubbles
INITIAL_BUBBLE_VELOCITY = .0001 *BUBBLE_DIAMETER 
MATCH_LENGTH = 4 # number of consecutive bubbles in a row/col to match
# Total Width of the screen based on bubbles
WIDTH = (BUBBLE_DIAMETER * BOARD_WIDTH 
         + BUBBLE_PADDING * (BOARD_WIDTH-1) 
         + MARGINS * 2)
# Total Height of the screen based on bubbles
HEIGHT = BUBBLE_DIAMETER*BOARD_HEIGHT + BUBBLE_PADDING * BOARD_HEIGHT

PURP = (62, 7, 120)   # Ship perimeter color
BLACK = (0,0,0)       # Background Color
FLAME = (237, 150, 9) # Ship Thruster Color

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
- p to pause

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
BULLET_VELOCITY = .02 * BUBBLE_DIAMETER # constant speed of a fired bullet
HIT_GROW = BUBBLE_DIAMETER//4 #Ship growth when struck by a falling bubble
SCORE_VELOCITY = -.02 # Constant upward movement of score alerts
SCORE_DURATION = 40 # Update cycles to display score alerts
SHIP_OUTER_COLOR = PURP # color of kill zone peremeter for player ship
SHIP_ACCEL = .0003 # When W,A,S,D depressed, speedup this much, decel on release
BUBBLE_GRAVITY = .00028 # When a bubble drops off the grid accellerate downward
FALLING_BUBBLE_POINTS = 4 # Points received for a falling bubble
LOST_BULLET_PENALTY = -4 # Points lost for an errant bullet

# Global Data Structures--------------------------------------------------------
# list of rows of bullets in a grid that spawn slowly at top of screen
#[[[x_pos, y_pos, color, wasBullet Flag],...more bubbles] ...more rows]
kill_bubbles = []
debug_kb = False # i key toggles 
# list of all bubbles broken free from grid and falling 
falling_bubbles = [] #[[x_pos, y_pos, color, vely, column], ...more droppers]
# List of bullets fired from the player's ship
bullets = [] #[[x_pos, y_pos, angle, color], ...more bullets]
level_colors = COLOR_LEVELS[0] #start with 3 colors and increase
ship_radius = BUBBLE_DIAMETER # Ship is twice the size of bubbles
# [x, y, velx, vely, accel, color, [Thrust Indicators], outer radius]
ship = [(WIDTH // 2) + BUBBLE_DIAMETER // 2 , # x coordinate
        HEIGHT - 2 *BUBBLE_DIAMETER,          # y coordinate
        0,                                    # x velocity
        0,                                    # y velocity
        SHIP_ACCEL * BUBBLE_DIAMETER,         # acceration on key hold
        random.choice(level_colors),          # core/bullet color
        [False, False, False, False],         # Thrust indicators
        BUBBLE_DIAMETER//8]                   # outer radius kill circle
# Displayed briefly on screen when points are earned/lost
score_alerts = [] #[[x_pos, y_pos, msg, duration, velocity], ...more alerts]
cross_hair = (0,0) #starts here and follows mouse
score = 0
bubble_velocity = INITIAL_BUBBLE_VELOCITY #bubbles spawn faster as game progress
combo_bullets = 0 #global for counting user bullets in combos
combo_bubbles = 0 #global to track if matched bubbles score points
game_state = 1 #1: Normal Play, 0: Game Over, 3: Paused, 5: Instruction Screen
level = 1 # Levels progresses with player score
next_level_points = 500 # To get to level 2
level_colors = COLOR_LEVELS[0] # Start with 3 colors
new_level_msg = None # Displayed briefly at level changes
c = Clock()
delta = [0]
speed_rows = MATCH_LENGTH

# PGZero's global draw() function
def draw():
    screen.fill(BLACK) # Background
    draw_bubbles()
    draw_ship()
    draw_bullets()
    draw_droppers()
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

# Procedure draws falling bubbles
def draw_droppers():
    for d in falling_bubbles:
        #[[x_pos, y_pos, color, vely, column], ...more droppers]
        x, y, c = d[0], d[1], d[2]
        screen.draw.filled_circle((x,y),BUBBLE_DIAMETER//2, c)

# Procedure draws cross hairs to match player selected bullet color
def draw_cross_hair():
    x, y = cross_hair
    screen.draw.line((x-BUBBLE_DIAMETER//2, y), (x-BUBBLE_DIAMETER//4, y),
                     ship[5])
    screen.draw.line((x+BUBBLE_DIAMETER//2, y), (x+BUBBLE_DIAMETER//4, y), 
                     ship[5])
    screen.draw.line((x, y-BUBBLE_DIAMETER//2), (x, y-BUBBLE_DIAMETER//4), 
                     ship[5])
    screen.draw.line((x, y+BUBBLE_DIAMETER//2), (x, y+BUBBLE_DIAMETER//4), 
                     ship[5])

# Procedure draws player fired bullets
def draw_bullets():
    for b in bullets:
        #[[x_pos, y_pos, angle, color], ...more bullets]
        x, y, c = b[0], b[1], b[3], 
        screen.draw.filled_circle((x,y),BUBBLE_DIAMETER//2, c)

# Porcedure draws player's ship
def draw_ship():
    # [x, y, velx, vely, accel, color, [Thrust Indicators], outer radius]
    x, y, c, b, r = ship[0], ship[1], ship[5], ship[6], ship[7]
    screen.draw.circle((x, y), r, SHIP_OUTER_COLOR) #outer hull
    screen.draw.filled_circle((x, y), BUBBLE_DIAMETER//4, c) #bullet indicator
    if b[0]: # North, Boost Down
        screen.draw.filled_circle((x, y-r-BUBBLE_PADDING),
                                  BUBBLE_DIAMETER//4, FLAME)
    if b[1]: # South, Boost Up
        screen.draw.filled_circle((x, y+r+BUBBLE_PADDING),
                                  BUBBLE_DIAMETER//4, FLAME)
    if b[2]: # East, Boost left
        screen.draw.filled_circle((x+r+BUBBLE_PADDING, y),
                                  BUBBLE_DIAMETER//4, FLAME)
    if b[3]: # West, Boost right
        screen.draw.filled_circle((x-r-BUBBLE_PADDING, y),
                                  BUBBLE_DIAMETER//4, FLAME)
# Procedure draws grid of kill bubbles
def draw_bubbles():
    #[[[x_pos, y_pos, color, wasBullet Flag],...more bubbles] ...more rows]
    for i, row in enumerate(kill_bubbles):
        for j, b in enumerate(row):
            x, y, c = b[0], b[1], b[2]
            if c:
                screen.draw.filled_circle((x,y),BUBBLE_DIAMETER//2, c)
            elif debug_kb: #Bullet with no color is an empty grid space
                screen.draw.text(str(i)+'\n'+str(j), centery=y, centerx=x, 
                                  fontsize=11)

# PGZero's global update game loop
def update():
    delta[0] = c.tick()
    if game_state == 1: # Normal Game Play
        update_bullets()
        update_droppers()
        update_kill_bubbles()
        update_ship()
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
        x, y, ang, c = b
        new_x = x + BULLET_VELOCITY * math.cos(ang) * delta[0] # x vector change
        new_y = y - BULLET_VELOCITY * math.sin(ang) * delta[0] # y vector change
        
        # Check for bullet off screen
        if new_x > WIDTH or new_x < 0 or new_y > HEIGHT or new_y < 0:
            score_alerts.append([new_x, new_y, LOST_BULLET_PENALTY, 
                                 SCORE_DURATION, SCORE_VELOCITY])
            score += LOST_BULLET_PENALTY
            if score < 0: # Don't drop score below 0
                score = 0
            del bullets[cnt]
        elif bullet_collide(new_x, new_y, c): # Check for collision with grid
            del bullets[cnt]
        else: # Otherwise, move this bullet in it's direction of travel
            bullets[cnt][0] = new_x
            bullets[cnt][1] = new_y
            cnt += 1

# Function takes the coordinates of bullet and returns true if the bullet
#  colides with the kill bubble grid.
# Returns true for collision and False otherwise. Uses is_close() and distance()
#  to verify collision and find the nearest kill bubble.
# If the bullet collides with a kill bubble assimilate_bullet() is called to add
#  the bullet to the kill bubble grid.
def bullet_collide(x, y, c):
    close_bubble = None #(i,j,dist)
    for i, row in enumerate(kill_bubbles):
        for j, bub in enumerate(row):
            # Use is_close() to find potential matches (city block distance)
            if bub[2] and is_close(x, y, bub[0], bub[1], BUBBLE_DIAMETER):
                # Use euclidian distance for precision
                d = distance(x, y, bub[0], bub[1])
                if d < BUBBLE_DIAMETER:
                    # find the closest bubble if multiple in range
                    if close_bubble:
                        if d < close_bubble[2]:
                            close_bubble = (i,j,d)
                    else:
                        close_bubble = (i,j,d)

    if close_bubble: # collided with this kill bubble
        assimilate_bullet(x, y, c, close_bubble) #add bubble to kill grid
        return True
    return False

# Procedure adds a bullet to the closest available spot in the kill bubble grid.
# Modifies global kill_bubbles
# Calls distance() to find the closest available spot
# Calls add_bottom_kill_row() if neccessary to place the new bubble
def assimilate_bullet(x, y, c, c_b_index):
    i, j, d = c_b_index
    n_list = [] #[(dist, (i,j), newRowFlag)...up, down, left, right]
        
    row_range = range(len(kill_bubbles))
    col_range = range(BOARD_WIDTH)

    if i+1 in row_range and not kill_bubbles[i+1][j][2]: #up
        x1 = kill_bubbles[i][j][0]
        y1 = kill_bubbles[i+1][j][1]
        n_list.append((distance(x, y, x1, y1), (i+1,j), False))
    if j+1 in col_range and not kill_bubbles[i][j+1][2]: #right
        x1 = kill_bubbles[i][j+1][0]
        y1 = kill_bubbles[i][j][1]
        n_list.append((distance(x, y, x1, y1), (i,j+1), False))
    if j-1 in col_range and not kill_bubbles[i][j-1][2]: #left
        x1 = kill_bubbles[i][j-1][0]
        y1 = kill_bubbles[i][j][1]
        n_list.append((distance(x, y, x1, y1), (i,j-1), False))
    if i == 0: #new bottom row
        x1 = kill_bubbles[0][j][0]
        y1 = kill_bubbles[0][j][1] + BUBBLE_DIAMETER+BUBBLE_PADDING
        n_list.append((distance(x, y, x1, y1), (0, j), True)) 
    elif i-1 in row_range and not kill_bubbles[i-1][j][2]: # down
        x1 = kill_bubbles[i][j][0]
        y1 = kill_bubbles[i-1][j][1]
        n_list.append((distance(x, y, x1, y1), (i-1,j), False))
        
    new_spot = min(n_list) # min distance is closest
    
    if new_spot[2]: # Add new row if neccessary
        add_bottom_kill_row()
    
    i = new_spot[1][0]
    j = new_spot[1][1]
    kill_bubbles[i][j][2] = c
    kill_bubbles[i][j][3] = True # Player added this bubble so can score points

# Procedure adds a new bottom row to the kill bubble grid to assimilate a new
#  bubble.
# Modifies global kill_bubbles
def add_bottom_kill_row():
    nbr = []
    # base coordinates on current first row bullet
    x = kill_bubbles[0][0][0]
    y = kill_bubbles[0][0][1] + BUBBLE_DIAMETER+BUBBLE_PADDING
    for j in range(BOARD_WIDTH):
        nbr.append([x,y,None,False]) # color of None adds blank place holders
        x += BUBBLE_DIAMETER+BUBBLE_PADDING
        
    kill_bubbles.insert(0, nbr)
    
# Function computes lightweight city block proximity given 2 coordinates and a 
#  distance. Returns true if the two points are closer or equal to distance.
def is_close(x1, y1, x2, y2, d):
    if abs(y1-y2) <= d and abs(x1-x2) <= d:
        return True
    return False

# Function returns euclidian distance between 2 given points
def distance(x1, y1, x2, y2):
    return ((x1-x2)**2 + (y1-y2)**2)**.5

# Procedure updates the ships outer radius and calls the move_ship() procedure.
# Modifies global ship
def update_ship():
    global ship_radius
    # Animate ship growth
    if ship[7] < ship_radius:
        ship[7] += 1
    elif ship[7] > ship_radius:
        ship[7] -= 1
    move_ship()

# Procedure moves the ship position, updates ship velocity and places thrust
#  indicators based on user keys W,A,S,D. Constains the ships movement in the
#  vertical plane and wraps it in the horizontal.
# Modifies global ship
def move_ship():
    velx, vely, accel = ship[2], ship[3], ship[4]
    
    # Update horizontal velocity and thrust indicators
    if keyboard[keys.A] and keyboard[keys.D]:
        ship[6][2] = ship[6][3] = True
    elif keyboard[keys.A]:
        velx -= accel
        ship[6][2] = True
        ship[6][3] = False
    elif keyboard[keys.D]:
        velx += accel
        ship[6][3] = True
        ship[6][2] = False
    else: # Decelerate in the horizontal plane if A or D not depressed.
        ship[6][2] = ship[6][3] = False
        sign = 1
        if velx < 0:
            sign = -1
        velx = abs(velx) - accel
        if velx < 0:
            velx = 0
        else:
            velx *= sign

    # Update vertical velocity and thrust indicators
    if keyboard[keys.W] and keyboard[keys.S]:
        ship[6][0] = ship[6][1] = True
    elif keyboard[keys.W]:
        vely -= accel
        ship[6][1] = True
        ship[6][0] = False
    elif keyboard[keys.S]:
        vely += accel
        ship[6][0] = True
        ship[6][1] = False
    else: # Decelerate in the vertical plane if W or S not depressed.
        ship[6][0] = ship[6][1] = False
        sign = 1
        if vely < 0:
            sign = -1
        vely = abs(vely) - accel
        if vely < 0:
            vely = 0
        else:
            vely *= sign
    
    # Update velocity
    ship[2] = velx
    ship[3] = vely
    
    # Update position
    ship[0] += ship[2] * delta[0]
    ship[1] += ship[3] * delta[0]
    
    # Wrap ship movement in horizontal plane
    if ship[0] > WIDTH:
        ship[0] = 0
    elif ship[0] < 0:
        ship[0] = WIDTH
    
    # Constrain ship movement in vertical plane
    if ship[1] > HEIGHT:
        ship[1] = HEIGHT
        ship[3] = 0
    elif ship[1] < 0:
        ship[1] = 0
        ship[3] = 0

# Function returns boolean indicating if the player's ship collides with the 
#  kill bubble grid or a falling bubble given a coordinate and a flag which
#  indicates if the ship should grow or die. Falling bubbles cause groth and
#  grid bubbles cause death.
# Modifies the global ship_radius on collision with falling bubble
# Modifies the global game_state on collision with bubble grid
def hit_ship(x, y, g):
    global game_state, ship_radius
    kill_zone = ship[7]+BUBBLE_DIAMETER//2
    if is_close(ship[0], ship[1], x, y, kill_zone):
        d = distance(ship[0], ship[1], x, y)
        if d < kill_zone:
            if g:
                ship_radius += HIT_GROW
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
    global speed_rows
    if kill_bubbles and kill_bubbles[0][0][1] > HEIGHT + BUBBLE_DIAMETER//2:
        del kill_bubbles[0]
    if not kill_bubbles or \
           kill_bubbles[-1][0][1] >= BUBBLE_DIAMETER//2 + BUBBLE_PADDING:
        add_bubble_row()
    for row in kill_bubbles:
        for bubb in row:
            if bubb[2]: # Only bubbles with a color 'exist'
                hit_ship(bubb[0],bubb[1], False)
            if speed_rows:
                bubb[1] += bubble_velocity * delta[0] * 10
            else:
                bubb[1] += bubble_velocity * delta[0]
    delete_bubble_matches()
    drop_loose_bubbles()

# Procedure checks for kill bubbles not connected with top row and turns them 
#  into falling bubbles.
# Modifies globals kill_bubbles and falling_bubbles
def drop_loose_bubbles():
    num_rows = len(kill_bubbles)
    col_range = range(BOARD_WIDTH)
    keep = [] #Bubbles connected to top row [(i,j), ...]
    for j in col_range:
        i = num_rows-1 # loop through top row of bubbles
        if not kill_bubbles[i][j][2]: # No color == No bubble
            continue

        path = [(i,j)] #stack to track path to every bubble reachable
        while path:
            check = path.pop()
            if check in keep: #No need to visit a bubble twice
                continue
            keep.append(check) # Bubble is reachable
            i,j = check # Try all four neighbors
            if i-1 >= 0 and kill_bubbles[i-1][j][2]: #South
                path.append((i-1,j))
            if i+1 < num_rows and kill_bubbles[i+1][j][2]: #North
                path.append((i+1,j))
            if j-1 in col_range and kill_bubbles[i][j-1][2]: #West
                path.append((i,j-1))
            if j+1 in col_range and kill_bubbles[i][j+1][2]: #East
                path.append((i,j+1))

    for i in range(num_rows):
        for j in col_range:   # loop through all kill bubbles
            kb = kill_bubbles[i][j]
            if kb[2] and (i,j) not in keep:  # drop any bubbles not in keep list
                x, y, c = kb[0], kb[1], kb[2] #add new bubble to fallers
                falling_bubbles.append([x,y,c,bubble_velocity,j])
                kill_bubbles[i][j][2] = None    

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
    while cnt < len(falling_bubbles):
        fb = falling_bubbles[cnt]
        if fb[1] > HEIGHT: # fell off screen. Award points and remove
            score += FALLING_BUBBLE_POINTS
            score_alerts.append([fb[0], fb[1], FALLING_BUBBLE_POINTS, 
                                 SCORE_DURATION, SCORE_VELOCITY])
            del falling_bubbles[cnt]
        
        # struck the ship or landed back on the kill bubble grid
        elif hit_ship(fb[0],fb[1], True) or falling_bubble_lands(fb):
            del falling_bubbles[cnt]
        
        else: # accelerate normally downward
            falling_bubbles[cnt][1] += fb[3] * delta[0]
            falling_bubbles[cnt][3] += BUBBLE_GRAVITY * delta[0]
            cnt += 1

# Function returns True if a falling bubble lands on the kill bubble grid and 
#  false otherwise.
# Modifies global kill_bubbles to add the faller back to the grid
def falling_bubble_lands(fb):
    #[x_pos, y_pos, color, vely, column]
    y, c, j = fb[1], fb[2], fb[4]
    d = BUBBLE_DIAMETER + BUBBLE_PADDING
    for i, kb_row in enumerate(kill_bubbles):
        kb = kb_row[j] # only check in the faller's column
        if kb[2] and abs(kb[1] - y) <= d:
            kill_bubbles[i+1][j][2] = c
            return True
    return False

# Procedure adds a new top row of random colored bubbles just above the top of
#  the screen. The new row contains no horizontal color matches.
# Modifies global kill_bubbles
def add_bubble_row():
    global speed_rows
    if speed_rows:
        speed_rows -=1
    if not kill_bubbles:
        y = -BUBBLE_DIAMETER // 2 #Barely off the screen
    else:
        y = kill_bubbles[-1][0][1] - (BUBBLE_PADDING + BUBBLE_DIAMETER)
    x = MARGINS + BUBBLE_DIAMETER // 2 # First column
    nbr = []
    nb = [x, y, random.choice(level_colors), False]
    nbr.append(nb)
    x += BUBBLE_PADDING + BUBBLE_DIAMETER
    last_color = nb[2] # Track this to ensure no horizontal matches
    consec = 1
    for j in range(BOARD_WIDTH-1):
        c = random.choice(level_colors)
        while consec == MATCH_LENGTH-1 and c == last_color:
            c = random.choice(level_colors)
        if last_color == c:
            consec += 1
        else:
            consec = 1
            last_color = c
        nbr.append([x, y, c, False])
        x += BUBBLE_PADDING + BUBBLE_DIAMETER
    kill_bubbles.append(nbr)


def delete_bubble_matches():
    if not kill_bubbles:
        return

    row_range = range(len(kill_bubbles))
    
    matched_bubbles = []
    for i in row_range:
        curr_color = None
        count = 0
        for j in range(BOARD_WIDTH):
            if not kill_bubbles[i][j][2]:
                curr_color = None
                count = 0
                continue
            tbc = kill_bubbles[i][j][2]
            if tbc == curr_color:
                count += 1
            else:
                curr_color = tbc
                count = 1
            if count == MATCH_LENGTH:
                matched_bubbles.append((i,j))
            elif count > MATCH_LENGTH:
                matched_bubbles.remove((i,j-1))
                matched_bubbles.append((i,j))
                
    for j in range(BOARD_WIDTH):
        curr_color = None
        count = 0
        for i in row_range:
            if not kill_bubbles[i][j][2]:
                curr_color = None
                count = 0
                continue
            tbc = kill_bubbles[i][j][2]
            if tbc == curr_color:
                count += 1
            else:
                curr_color = tbc
                count = 1
            if count == MATCH_LENGTH:
                matched_bubbles.append((i,j))
            elif count > MATCH_LENGTH:
                matched_bubbles.remove((i-1,j))
                matched_bubbles.append((i,j))
                
    global score, combo_bullets, combo_bubbles, bubble_velocity
    for i, j in matched_bubbles:
        combo_bullets = 0
        combo_bubbles = 0
        rec_erase(i,j)
        if combo_bullets and combo_bubbles:
            over_match = combo_bubbles
            bonus = 2**combo_bubbles
            score_diff = next_level_points - score
            if bonus > score_diff:
                bonus = score_diff
            score += bonus
            x,y = kill_bubbles[i][j][0], kill_bubbles[i][j][1]
            score_alerts.append([x, y, bonus, 
                                 SCORE_DURATION, SCORE_VELOCITY])

def rec_erase(i,j):
    if not kill_bubbles[i][j][2]:
        return False
    global combo_bubbles, combo_bullets
    c = kill_bubbles[i][j][2]
    if kill_bubbles[i][j][3]:
        combo_bullets += 1
    else:
        combo_bubbles += 1
    kill_bubbles[i][j][2] = None
    n = ((i+1,j), (i-1,j), (i, j+1), (i, j-1))
    for nei in n:
        i, j = nei
        if (i in range(len(kill_bubbles)) 
                and j in range(BOARD_WIDTH)
                and kill_bubbles[i][j][2]
                and c == kill_bubbles[i][j][2]):
            rec_erase(i, j)

def on_mouse_move (pos):
    global cross_hair
    cross_hair = pos

def on_mouse_down (pos, button):
    global bubble_velocity, speed_rows
    if mouse.LEFT == button:
        bullets.append([ship[0],ship[1], get_angle(pos), ship[5]])
    if mouse.RIGHT == button:
        speed_rows += 1

def on_key_down(key):
    global game_state, debug_kb
    if key == keys.SPACE:
        cycle_bullet_color()
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
    if key == keys.K:
        debug_kb = not debug_kb
        
def cycle_bullet_color():
    ship[5] = level_colors[(level_colors.index(ship[5])+1) % len(level_colors)]

def get_angle(pos):
    return math.atan2(ship[1] - pos[1], -(ship[0] - pos[0]))

def next_level():
    global level, bubble_velocity, kill_bubbles, bullets, next_level_points, \
        falling_bubbles, ship_radius, level_colors, new_level_msg, speed_rows
    kill_bubbles, falling_bubbles, bullets = [], [], []
    ship_radius = BUBBLE_DIAMETER
    level += 1
    new_level_msg = f"Level {level}"
    obv = INITIAL_BUBBLE_VELOCITY+(INITIAL_BUBBLE_VELOCITY * ((level-1) * .1))
    bubble_velocity = INITIAL_BUBBLE_VELOCITY+(INITIAL_BUBBLE_VELOCITY * (level * .1))
    bv_change = (bubble_velocity-obv)/obv
    speed_rows = MATCH_LENGTH
    if bv_change:
        new_level_msg += f'\nBubble Creation Rate +{bv_change:.0%}'
    next_level_points += 250 * level
    if level == 5:
        level_colors = COLOR_LEVELS[1]
        new_level_msg += "\nNew Color Added!"
        ship[5] = random.choice(level_colors)
    elif level == 10:
        level_colors = COLOR_LEVELS[2]
        new_level_msg += "\nNew Color Added!"
        ship[5] = random.choice(level_colors)

    clock.schedule(clear_new_level_msg, 15.0)

def clear_new_level_msg():
    global new_level_msg
    new_level_msg = None
    
# Procedure Restarts the game when the 'r' key is pressed
def initalize_game():
    global kill_bubbles, falling_bubbles, ship_radius, ship, bullets, score, \
    game_state, level_colors, bubble_velocity, level, next_level_points, \
    speed_rows
    
    kill_bubbles = []
    falling_bubbles = []
    bullets = []
    level_colors = COLOR_LEVELS[0] 
    ship_radius = BUBBLE_DIAMETER
    ship = [(WIDTH // 2) + BUBBLE_DIAMETER // 2 ,
            HEIGHT - 2 *BUBBLE_DIAMETER,         
            0,                                   
            0,                                   
            SHIP_ACCEL * BUBBLE_DIAMETER,        
            random.choice(level_colors),         
            [False, False, False, False],        
            BUBBLE_DIAMETER//8]                  
    score = 0
    bubble_velocity = INITIAL_BUBBLE_VELOCITY 
    game_state = 1
    level = 1 
    next_level_points = 500    
    level_colors = COLOR_LEVELS[0] 
    new_level_msg = None 
    speed_rows = MATCH_LENGTH

pgzrun.go()