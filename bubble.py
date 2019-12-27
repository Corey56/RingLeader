"""
Ring Leader
"""

from random import choice
from math import sin, cos

from dist import *

class Bubble(object):
    BUBBLE_DIAMETER = 32
    
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
    
    def __str__(self):
        atts = ['\t' + a + ': ' + str(v) for a,v in self.__dict__.items()]
        return type(self).__name__ + ' object:\n' + '\n'.join(atts)

    def draw(self, screen):
        if self.color:
            screen.draw.filled_circle((self.x, self.y), 
                                       Bubble.BUBBLE_DIAMETER//2, 
                                       self.color)

class Bullet(Bubble):
    BULLET_VELOCITY = .02 * Bubble.BUBBLE_DIAMETER # speed of a fired bullet
    LOST_BULLET_PENALTY = 4 # Points lost for an errant bullet
    
    def __init__(self, x, y, color, ang):
        self.angle = ang
        super().__init__(x, y, color)
        
    def move(self, time_delta):
        self.x += Bullet.BULLET_VELOCITY * cos(self.angle) * time_delta # x vect
        self.y -= Bullet.BULLET_VELOCITY * sin(self.angle) * time_delta # y vect
    
    def is_off_screen(self, HEIGHT, WIDTH):
        return self.x > WIDTH or self.x < 0 or self.y > HEIGHT or self.y < 0

class Dropper(Bubble):
    BUBBLE_GRAVITY = .00028 # bubble drops off the grid accellerate downward
    FALLING_BUBBLE_POINTS = 4 # Points received for a falling bubble

    def __init__(self, x, y, color, vely, column):
        self.vely = vely
        self.column = column
        super().__init__(x, y, color)
        
class Grid_Bubble(Bubble):
    def __init__(self, x, y, color, bulletFlag):
        self.bulletFlag = bulletFlag
        super().__init__(x, y, color)

class Bubble_List(object):
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
        if isinstance(rhs, Bubble_List):
            self.contents.extend(rhs.contents)
        else:
            self.contents.append(rhs)
        return self

    def draw(self, screen):
        for b in self.contents: 
            b.draw(screen)

class Bubble_Row(Bubble_List):
    def __str__(self):
        if self.contents:
            s = 'Bubble_Row:\n'
            s += '     x pos     y pos  P Flag   color'
            for b in self.contents:
                s += f'\n{b.x:10.2f}{b.y:10.2f}{b.bulletFlag:8}   {b.color}'
        else:
            s = 'Empty Bubble_Row'
        return s

class Bullet_List(Bubble_List):
    def __str__(self):
        if self.contents:
            s = 'Bullet_List:\n'
            s += '     x pos     y pos     ang   color'
            for b in self.contents:
                s += f'\n{b.x:10.2f}{b.y:10.2f}{b.angle:8.2f}   {b.color}'
        else:
            s = 'Empty Bullet_List:'
        return s
        
class Dropper_List(Bubble_List):
    def __str__(self):
        #x, y, color, vely, column
        if self.contents:
            s = 'Dropper_List:\n'
            s += '     x pos     y pos      vely   col   color'
            for b in self.contents:
                s += f'\n{b.x:10.2f}{b.y:10.2f}{b.vely:10.2f}{b.column:6}   {b.color}'
        else:
            s = 'Empty Dropper_List:'
        return s

class Bubble_Grid(object):
    BUBBLE_PADDING = 4
    BOARD_WIDTH = 28
    MARGINS = 10
    MATCH_LENGTH = 4
    INITIAL_BUBBLE_VELOCITY = .0001 * Bubble.BUBBLE_DIAMETER 

    def __init__(self, colors, velocity=None):
        if velocity:
            self.velocity = velocity
        else:
            self.velocity = Bubble_Grid.INITIAL_BUBBLE_VELOCITY
        
        self.colors = colors
        self.rows = []

    def __str__(self):
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
        nbr = Bubble_Row()
        
        # base coordinates on current first row bullet
        x = self.rows[0][0].x
        y = (self.rows[0][0].y 
             + Bubble.BUBBLE_DIAMETER 
             + Bubble_Grid.BUBBLE_PADDING)
             
        for j in range(Bubble_Grid.BOARD_WIDTH):
            # color of None adds blank place holders
            nbr += Grid_Bubble(x,y,None,False)
            x += Bubble.BUBBLE_DIAMETER + Bubble_Grid.BUBBLE_PADDING
            
        self.rows.insert(0, nbr)
        
    def addTopRow(self):
        if not self.rows:
            y = -Bubble.BUBBLE_DIAMETER // 2 #Barely off the screen
        else:
            y = self.rows[-1][0].y - (Bubble_Grid.BUBBLE_PADDING
                                      + Bubble.BUBBLE_DIAMETER)
        x = Bubble_Grid.MARGINS + Bubble.BUBBLE_DIAMETER // 2 # First column
        nbr = Bubble_Row()
        nbr += Grid_Bubble(x, y, choice(self.colors), False)
        x += Bubble_Grid.BUBBLE_PADDING + Bubble.BUBBLE_DIAMETER
        last_color = nbr[0].color # Track this to ensure no horizontal matches
        consec = 1
        for j in range(Bubble_Grid.BOARD_WIDTH-1):
            c = choice(self.colors)
            while consec == Bubble_Grid.MATCH_LENGTH-1 and c == last_color:
                c = choice(self.colors)
            if last_color == c:
                consec += 1
            else:
                consec = 1
                last_color = c
            nbr += Grid_Bubble(x, y, c, False)
            x += Bubble_Grid.BUBBLE_PADDING + Bubble.BUBBLE_DIAMETER
        self.rows.append(nbr)
        
    # Function takes the coordinates of bullet and returns true if the bullet
    #  colides with the kill bubble grid.
    # Returns true for collision and False otherwise. Uses is_close() and distance()
    #  to verify collision and find the nearest kill bubble.
    # If the bullet collides with a kill bubble assimilate_bullet() is called to add
    #  the bullet to the kill bubble grid.
    def bullet_collide(self, x, y, c):
        close_bubble = None #(i,j,dist)
        for i, row in enumerate(self.rows):
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
            n = self.findNearestSpot(x, y, close_bubble[0], close_bubble[1])
            self.addGridBubble(*n, c)
            return True
        
        return False
    
    def findNearestSpot(self, x, y, i, j):
        n_list = [] #[(dist, (i,j), newRowFlag)...up, down, left, right]
            
        row_range = range(len(self.rows))
        col_range = range(Bubble_Grid.BOARD_WIDTH)

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
            y1 = (self.rows[0][j].y 
                  + Bubble.BUBBLE_DIAMETER
                  + Bubble_Grid.BUBBLE_PADDING)
            n_list.append((distance(x, y, x1, y1), (0, j), True)) 
        
        elif i-1 in row_range and not self.rows[i-1][j].color: # down
            x1 = self.rows[i][j].x
            y1 = self.rows[i-1][j].y
            n_list.append((distance(x, y, x1, y1), (i-1,j), False))
            
        nearest = min(n_list) # min distance is closest

        return nearest[1][0], nearest[1][1], nearest[2] # i, j, newRowFlag


    def addGridBubble(self, i, j, new_row_flag, c):
        if new_row_flag: # Add new row if neccessary
            self.addBottomRow()

        self.rows[i][j].color = c
        # Player added this bubble so can score points
        self.rows[i][j].bulletFlag = True

    def drop_loose_bubbles(self):
        num_rows = len(self)
        col_range = range(Bubble_Grid.BOARD_WIDTH)
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
        for i in range(num_rows):
            for j in col_range:   # loop through all kill bubbles except top row
                gb = self.rows[i][j]
                if gb.color and (i,j) not in keep:  # drop any bubbles not in keep list
                    newDroppers += Dropper(gb.x, gb.y, gb.color, self.velocity, j)
                    self.rows[i][j].color = None

        return newDroppers
    
    def get_matches(self):
        if not self.rows:
            return

        row_range = range(len(self.rows))
        
        matches = [] #[(i,j), ...]
        for i in row_range:
            curr_color = None
            count = 0
            for j in range(Bubble_Grid.BOARD_WIDTH):
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
                
                if count >= Bubble_Grid.MATCH_LENGTH:
                    matches.append((i,j))

        for j in range(Bubble_Grid.BOARD_WIDTH):
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
                
                if count >= Bubble_Grid.MATCH_LENGTH:
                    matches.append((i,j))
        
        return matches