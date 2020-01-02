"""
Module contains the following Classes:
- Bubble (Generic properties for 3 sub classes)
 - Bullet (A bullet fired from player's ship)
 - Dropper (A falling bubble broken free from the grid)
 - Grid_Bubble (A Bubble in grid formation)
- Bubble List (Generic properties for 3 sub classes)
 - Bubble_Row (A row of bubbles in a Bubble_Grid)
 - Bullet_List (A list of Bullet objects)
 - Dropper_List (A list of Dropper objects)
- Bubble_Grid (List of Bubble_Row objects)
"""

from random import choice
from math import sin, cos

from dist import *
from config import INITIAL_BUBBLE_VELOCITY, HEIGHT, WIDTH, BUBBLE_DIAMETER, \
                   MATCH_LENGTH, BUBBLE_PADDING, BUBBLE_GRAVITY, MARGINS, \
                   BOARD_WIDTH, BULLET_VELOCITY, FALLING_BUBBLE_POINTS, \
                   LOST_BULLET_PENALTY

class Bubble(object):
    """
    Represents a generic bubble for sub classing
    x: x position in pix
    y: y position in pix
    color: RGB tuple
    """

    def __init__(self, x, y, color):
        """
        Initialize postion and color
        """
        
        self.x = x
        self.y = y
        self.color = color

    def __str__(self):
        """
        Return a formatted string for printing
        """
        
        atts = ['\t' + a + ': ' + str(v) for a,v in self.__dict__.items()]
        return type(self).__name__ + ' object:\n' + '\n'.join(atts)

    def draw(self, screen):
        """
        Given a PGZero screen object, draw this bubble on the screen.
        """
        if self.color:
            screen.draw.filled_circle((self.x, self.y),
                                       BUBBLE_DIAMETER//2,
                                       self.color)
                                       
    def is_off_screen(self):
        """
        Given the height and width of the game board in pix, return boolean for
         bubble off screen
        """
        return self.x > WIDTH or self.x < 0 or self.y > HEIGHT or self.y < 0

class Bullet(Bubble):
    """
    Represents a bullet fired from the player's ship.
    angle: Angle of travel in radians
    """

    def __init__(self, x, y, color, ang):
        """
        Store generic bubble attributes and angle of travel in radians
        """
        self.angle = ang
        super().__init__(x, y, color)

    def move(self, time_delta):
        """
        Given ms since the last update, move bullet at set speed on angle
        """
        self.x += BULLET_VELOCITY * cos(self.angle) * time_delta # x vect
        self.y -= BULLET_VELOCITY * sin(self.angle) * time_delta # y vect

class Dropper(Bubble):
    """
    Represents a bubble falling downward after breaking free from bubble grid
    vely: falling speed in pix/ms
    column: integer index of falling column 0 - BOARD_WIDTH-1
    """

    def __init__(self, x, y, color, vely, column):
        """
        Initialize velocity, column and generic attributes
        """
        self.vely = vely
        self.column = column
        super().__init__(x, y, color)

    def move(self, time_delta):
        """
        Given time since last update in ms, accellerate dropper downward
        """
        self.y += self.vely * time_delta
        self.vely += BUBBLE_GRAVITY * time_delta

class Grid_Bubble(Bubble):
    """
    Represents a bubble in the grid
    bulletFlag: indicates if this grid bubble came from a Bullet for scoring
                purposes
    """
    def __init__(self, x, y, color, bulletFlag):
        """
        Initialize flag for grid bubble added by bullet and generic attributes
        """
        self.bulletFlag = bulletFlag
        super().__init__(x, y, color)

class Bubble_List(object):
    """
    Represents a generic list of Bubble sub classes
    contents: a list of Bubble object subclasses
    """
    def __init__(self):
        self.contents = []

    def __len__(self):
        return len(self.contents)

    def __iter__(self):
        return iter(self.contents)

    def __getitem__(self, key):
        return self.contents[key]

    def __setitem__(self, key, item):
        self.contents[key] = item

    def __delitem__(self, key):
        del self.contents[key]

    def __iadd__(self, rhs):
        """
        '+=' operator can handle single Bubble objects or Bubble_List objects
        """
        if isinstance(rhs, Bubble_List):
            self.contents.extend(rhs.contents)
        else:
            self.contents.append(rhs)
        return self

    def draw(self, screen):
        """
        Given a PGZero screen object, draw each Bubble in the list
        """
        for b in self.contents:
            b.draw(screen)
            
    def move(self, time_delta):
        """
        Given the ms since last move, move each Bubble in the list
        """
        for b in self.contents:
            b.move(time_delta)

class Bubble_Row(Bubble_List):
    """
    Represents a row of Grid_Bubble objects in a Bubble_Grid object
    """
    
    def __str__(self):
        """
        Returns a formatted string for printing
        """
        if self.contents:
            s = 'Bubble_Row:\n'
            s += '     x pos     y pos  P Flag   color'
            for b in self.contents:
                s += f'\n{b.x:10.2f}{b.y:10.2f}{b.bulletFlag:8}   {b.color}'
        else:
            s = 'Empty Bubble_Row'
        return s

class Bullet_List(Bubble_List):
    """
    Represents a list of Bullets flying across the screen
    """
    def __str__(self):
        """
        Returns a formatted string for printing
        """
        if self.contents:
            s = 'Bullet_List:\n'
            s += '     x pos     y pos     ang   color'
            for b in self.contents:
                s += f'\n{b.x:10.2f}{b.y:10.2f}{b.angle:8.2f}   {b.color}'
        else:
            s = 'Empty Bullet_List:'
        return s

    def check_bounds(self):
        """
        Given the height and width of the game board in pix, return a list of 
         tuples representing bullets that flew off the screen. Also erase such 
         bullets from the list
        """
        oob = [] # [((x,y),score deduction), ...]
        cnt = 0
        while cnt < len(self.contents):
            b = self.contents[cnt]
            if b.is_off_screen():
                oob.append(((b.x, b.y), -LOST_BULLET_PENALTY))

                del self.contents[cnt]
            else:
                cnt += 1
        return oob

    def delete_strikers(self, grid):
        """
        Given a Bubble_Grid object, delete any Bullet objects which contact the 
         grid.
        """
        cnt = 0
        while cnt < len(self.contents):
            b = self.contents[cnt]
            if grid.bullet_collide(b):
                del self.contents[cnt]
            else:
                cnt += 1

class Dropper_List(Bubble_List):
    """
    Represents a list of bubbles falling off the screen
    """
    
    def __str__(self):
        """
        Returns a formatted string for printing purposes
        """
        if self.contents:
            s = 'Dropper_List:\n'
            s += '     x pos     y pos      vely   col   color'
            for b in self.contents:
                s += f'\n{b.x:10.2f}{b.y:10.2f}{b.vely:10.2f}{b.column:6}   {b.color}'
        else:
            s = 'Empty Dropper_List:'
        return s

    def check_bounds(self):
        """
        Given the height of the game board, return a list of tuples with the 
         locations of droppers that fell off the bottom ot the screen. Also 
         remove said droppers from the list.
        """
        oob = [] # [((x,y),points awarded), ...]
        cnt = 0
        while cnt < len(self.contents):
            fb = self.contents[cnt]
            if fb.y > HEIGHT: # fell off screen. Award points and remove
                oob.append(((fb.x, fb.y), FALLING_BUBBLE_POINTS))
                del self.contents[cnt]
            else:
                cnt += 1
        return oob

    def strike(self, ship):
        """
        Given a Ship object, identify and remove any droppers from the list 
        which struck the Ship.
        """
        cnt = 0
        while cnt < len(self.contents):
            fb = self.contents[cnt]

            if ship.hit_ship(fb.x,fb.y, BUBBLE_DIAMETER//2):
                del self.contents[cnt]
            else:
                cnt += 1

    def land(self, grid):
        """
        Given a Bubble_Grid, identify and delete any droppers which landed on 
         the grid.
        """
        cnt = 0
        while cnt < len(self.contents):
            if grid.falling_bubble_lands(self.contents[cnt]):
                del self.contents[cnt]
            else:
                cnt += 1

class Bubble_Grid(object):
    """
    Represents the grid of bubbles falling slowly from the top of the screen
    colors: list of RGB colors to make new grid bubbles
    velocity: speed of bubble generation from screen top
    rows: a list of Bubble_Row objects
    speed_rows: number of rows to speed out at level begining
    """

    def __init__(self, colors, velocity=None):
        if velocity:
            self.velocity = velocity
        else:
            self.velocity = INITIAL_BUBBLE_VELOCITY

        self.colors = colors
        self.rows = []
        self.speed_rows = MATCH_LENGTH

    def __str__(self):
        """
        Returns a formatted string for printing
        """
        if self.rows:
            s = 'Bubble Grid:'
            for i, b in enumerate(self.rows):
                s += f'\n\tRow {i}\n{b}'
        else:
            s = 'Empty Bubble Grid:'
        return s

    def __len__(self):
        return len(self.rows)

    def __iter__(self):
        return iter(self.rows)

    def __getitem__(self, key):
        return self.rows[key]

    def __setitem__(self, key, item):
        self.rows[key] = item

    def __delitem__(self, key):
        del self.rows[key]

    def draw(self, screen):
        for r in self.rows:
            r.draw(screen)

    def addBottomRow(self):
        """
        Adds a new bottom row at bottom of screen in position 0 of self.rows
        """
        nbr = Bubble_Row()

        # base coordinates on current first row bullet
        x = self.rows[0][0].x
        y = (self.rows[0][0].y + BUBBLE_DIAMETER + BUBBLE_PADDING)

        for j in range(BOARD_WIDTH):
            # color of None adds blank place holders
            nbr += Grid_Bubble(x,y,None,False)
            x += BUBBLE_DIAMETER + BUBBLE_PADDING

        self.rows.insert(0, nbr)

    def addTopRow(self):
        """
        Appends a new Bubble_Row to self.rows with no horizontal matches.
        Decrements self.speed_rows if > 0.
        """
        # Check if there's space at top of screen for new row.
        if self.rows and self.rows[-1][0].y < BUBBLE_DIAMETER//2 \
                                               + BUBBLE_PADDING:
            return
        
        # Distance between bubble centers
        offset = BUBBLE_PADDING + BUBBLE_DIAMETER
        
        # Distance the new row from the one below it. 
        if not self.rows:
            y = -BUBBLE_DIAMETER // 2 # Barely off the screen if no row exists
        else:
            y = self.rows[-1][0].y - offset
            
        x = MARGINS + BUBBLE_DIAMETER // 2 # First column
        nbr = Bubble_Row()
        nbr += Grid_Bubble(x, y, choice(self.colors), False) # Add 1st bubble
        x += offset # Move right to next spot
        last_color = nbr[0].color # Track this to ensure no horizontal matches
        consec = 1
        cs = set(self.colors)
        for j in range(BOARD_WIDTH-1):
            if consec == MATCH_LENGTH-1: # Avoid horizontal match
                c = choice(tuple(cs - set([last_color])))
            else: 
                c = choice(self.colors)            
            nbr += Grid_Bubble(x, y, c, False)
            x += offset
            if c == last_color:
                consec += 1
            else:
                last_color = c
                consec = 1

        self.rows.append(nbr)

        if self.speed_rows:
            self.speed_rows -= 1

    def bullet_collide(self, bullet):
        """
        Function takes a Bullet object and returns true if the bullet colides 
         with any Bubble in the grid.
        Returns true for collision and False otherwise. Uses is_close() and 
         distance() to verify collision.
        Calls findNearestSpot upon collision to find the nearest spot to place 
         the Bullet in the Bubble_Grid.
        Calls addGridBubble to add the Bullet to the grid.
        """
        x, y, c = bullet.x, bullet.y, bullet.color
        close_bubble = None #(i,j,dist)
        for i, row in enumerate(self.rows):
            for j, b in enumerate(row):
                # Use is_close() to find potential matches (city block distance)
                if b.color and is_close(x, y, b.x, b.y, BUBBLE_DIAMETER):
                    # Use euclidian distance for precision
                    d = distance(x, y, b.x, b.y)
                    if d < BUBBLE_DIAMETER:
                        # find the closest bubble if multiple in range
                        if close_bubble:
                            if d < close_bubble[2]:
                                close_bubble = (i,j,d)
                        else:
                            close_bubble = (i,j,d)

        if close_bubble: # collided with this grid bubble
            n = self.findNearestSpot(x, y, close_bubble[0], close_bubble[1])
            self.addGridBubble(*n, c)
            return True

        return False

    def findNearestSpot(self, x, y, i, j):
        """
        Given x, y position and Grid_Bubble location i, j, return the available
         spot nearest the position and a bool to indicate if this position 
         requires a new row be added to the grid: (i, j, newRowFlag)
        """
        n_list = [] #[(dist, (i,j), newRowFlag)...up, down, left, right]

        row_range = range(len(self.rows))
        col_range = range(BOARD_WIDTH)

        if i+1 in row_range and not self.rows[i+1][j].color: #up
            x1 = self.rows[i][j].x
            y1 = self.rows[i+1][j].y
            n_list.append((distance(x, y, x1, y1), (i+1,j), False))

        if j+1 in col_range and not self.rows[i][j+1].color: #right
            x1 = self.rows[i][j+1].x
            y1 = self.rows[i][j].y
            n_list.append((distance(x, y, x1, y1), (i,j+1), False))

        if j-1 in col_range and not self.rows[i][j-1].color: #left
            x1 = self.rows[i][j-1].x
            y1 = self.rows[i][j].y
            n_list.append((distance(x, y, x1, y1), (i,j-1), False))

        if i == 0: #new bottom row
            x1 = self.rows[0][j].x
            y1 = (self.rows[0][j].y + BUBBLE_DIAMETER + BUBBLE_PADDING)
            n_list.append((distance(x, y, x1, y1), (0, j), True))

        elif i-1 in row_range and not self.rows[i-1][j].color: # down
            x1 = self.rows[i][j].x
            y1 = self.rows[i-1][j].y
            n_list.append((distance(x, y, x1, y1), (i-1,j), False))

        nearest = min(n_list) # min distance is closest

        return nearest[1][0], nearest[1][1], nearest[2] # i, j, newRowFlag


    def addGridBubble(self, i, j, new_row_flag, c):
        """
        Given an i, j location and a color, add a Bubble to the grid creating a
         new Bubble_Row if required by flag. Set the bulletFlag on this bubble
         for scoring purposes.
        """
        if new_row_flag: # Add new row if neccessary
            self.addBottomRow()

        self.rows[i][j].color = c
        # Player added this bubble so can score points
        self.rows[i][j].bulletFlag = True

    def drop_loose_bubbles(self):
        """
        From every Bubble in the top row, attempt to reach every grid bubble, 
         storing all reachable bubbles in the keep list. Any grid bubbles not
         on the keep list are removed from the grid and returned in a list of 
         Droppers.
        """
        num_rows = len(self)
        col_range = range(BOARD_WIDTH)
        keep = [] #Bubbles connected to top row [(i,j), ...]
        for j in col_range:
            i = num_rows-1 # loop through top row of bubbles
            if not self.rows[i][j].color: # No color == No bubble
                continue

            path = [(i,j)] #stack to track path to every bubble reachable
            while path:
                check = path.pop()
                if check in keep: #No need to visit a bubble twice
                    continue
                keep.append(check) # Bubble is reachable
                i,j = check # Try all four neighbors
                if i-1 >= 0 and self.rows[i-1][j].color: #South
                    path.append((i-1,j))
                if i+1 < num_rows and self.rows[i+1][j].color: #North
                    path.append((i+1,j))
                if j-1 in col_range and self.rows[i][j-1].color: #West
                    path.append((i,j-1))
                if j+1 in col_range and self.rows[i][j+1].color: #East
                    path.append((i,j+1))

        newDroppers = Dropper_List()
        for i in range(num_rows-1): # loop through all Bubble_Row except top row
            for j in col_range:   
                gb = self.rows[i][j]
                if gb.color and (i,j) not in keep:  #drop bubbles not in keep 
                    newDroppers += Dropper(gb.x, gb.y, gb.color, self.velocity
                                           , j)
                    self.rows[i][j].color = None

        return newDroppers

    def get_matches(self):
        """
        Check for consecutive colors horizontally and vertically of the length
         perscribed in the MATCH_LENGTH constant. Return a list of tuples
         containing grid positions of matches: [(i,j), ...]
        """
        if not self.rows:
            return

        row_range = range(len(self.rows))

        matches = [] # [(i,j), ...]
        
        for i in row_range: # Horizontal Check
            curr_color = None
            count = 0
            for j in range(BOARD_WIDTH):
                tbc = self.rows[i][j].color
                if not tbc:
                    curr_color = None
                    count = 0
                    continue

                if tbc == curr_color:
                    count += 1
                else:
                    curr_color = tbc
                    count = 1

                if count == MATCH_LENGTH:
                    matches.append((i,j))

        for j in range(BOARD_WIDTH): # Vertical Check
            curr_color = None
            count = 0
            for i in row_range:
                tbc = self.rows[i][j].color
                if not tbc:
                    curr_color = None
                    count = 0
                    continue

                if tbc == curr_color:
                    count += 1
                else:
                    curr_color = tbc
                    count = 1

                if count == MATCH_LENGTH:
                    matches.append((i,j))

        return matches

    def prune_bottom_row(self):
        """
        Removes the bottom (1st) Bubble_Row if it's off the bottom of screen
        """
        if self.rows and self.rows[0][0].y > HEIGHT + BUBBLE_DIAMETER//2:
            del self.rows[0] # fell off screen

    def collide(self, x, y, radius):
        """
        Given an x, y location and radius of a circular object, return True if
         any Bubble in the grid collides with the object and False otherwise.
        """
        strike_zone = BUBBLE_DIAMETER//2 + radius
        for row in self.rows:
            for b in row:
                if b.color and is_close(b.x, b.y, x, y, strike_zone):
                    d = distance(b.x, b.y, x, y)
                    if d <= strike_zone:
                        return True
        return False

    def move(self, time_delta):
        """
        Given the time in ms since last update, move each bubble down at self
         .velocity pix/ms. If self.speed_rows > 0, bubbles fall 16 times faster.
        """
        delta_y = self.velocity * time_delta
        if self.speed_rows:
            delta_y *= 16
        for row in self.rows:
            for b in row:
                b.y += delta_y

    def erase_matches(self):
        """
        Get a list of i,j position matches from get_matches(). Erase all 
         consecutive bubbles of the same color begining at each match position.
        Store a tuple in combos list for each combo scored. A combo must contain 
         at least one player bullet to score points. The combos list is returned
         to update player's score.
        """
        combos = [] #[((x,y),pts), ...]
        for match in self.get_matches():
            bulletFound = None
            combo_bubbles = 0
            path = [match] #Stack to walk matches
            while path:
                r, c = path.pop()
                b = self.rows[r][c]
                color = b.color
                if not color:
                    continue
                if b.bulletFlag: # Found a bullet, place alert location here
                    bulletFound = (b.x,b.y)
                else:
                    combo_bubbles += 1
                b.color = None
                n = ((r+1,c), (r-1,c), (r, c+1), (r, c-1))
                for nei in n: # Try 4 cardinal neighbors
                    i, j = nei
                    if (i in range(len(self.rows))               # valid row
                            and j in range(BOARD_WIDTH)          # valid column
                            and self.rows[i][j].color == color): # color match
                        path.append((i, j))

            if bulletFound: # Only award points if player created this combo
                combos.append((bulletFound, 2**combo_bubbles))

        return combos

    def falling_bubble_lands(self, fb):
        """
        Given a Dropper, check falling column for landing back on the grid.
        Return True if Dropper lands and False otherwise.
        """
        y, c, j = fb.y, fb.color, fb.column
        d = BUBBLE_DIAMETER + BUBBLE_PADDING
        for i, row in enumerate(self.rows):
            b = row[j] # only check in the faller's column
            if b.color and abs(b.y - y) <= d:
                self.rows[i+1][j].color = c
                return True
        return False