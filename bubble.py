"""
Ring Leader
"""

class Bubble(object):
    BUBBLE_DIAMETER = 32
    ##[[[x_pos, y_pos, color, wasBullet Flag],...more bubbles] ...more rows]
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
    def __init__(self, x, y, color, ang):
        self.angle = ang
        super().__init__(x, y, color)

class Dropper(Bubble):
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
    
    def __str__(self):
        s = 'Bubble_List:\n'
        s += '     x pos     y pos     ang   color\n'
        for b in self.contents:
            s += f'{b.x:10.2f}{b.y:10.2f}{b.angle:8.2f}   {b.color}\n'
        return s

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

    def addBullet(self, x, y, color, ang):
        self.contents.append(Bullet(x, y, color, ang))

    def addDropper(self, x, y, color, vely, column):
        self.contents.append(Dropper(x, y, color, vely, column))

    def draw(self, screen):
        for b in self.contents: 
            b.draw(screen)
            
class Bubble_Grid(object):
    BUBBLE_PADDING = 4
    BOARD_WIDTH = 28

    def __init__(self, width):
        self.width = width
        self.rows = []

    def __str__(self):
        s = 'Bubble Grid:\n'
        for i, b in enumerate(self.contents):
            s += f'\tRow {i}\n{b}'
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
        nbr = []
        
        # base coordinates on current first row bullet
        x = self.rows[0][0].x
        y = (self.rows[0][0].y 
             + Bubble.BUBBLE_DIAMETER 
             + Bubble_Grid.BUBBLE_PADDING)
             
        for j in range(Bubble_Grid.BOARD_WIDTH):
            # color of None adds blank place holders
            nbr.append(Grid_Bubble(x,y,None,False))
            x += Bubble.BUBBLE_DIAMETER + Bubble_Grid.BUBBLE_PADDING
            
        self.rows.insert(0, nbr)
        
    def addTopRow(self, speed_rows):
        if (self.rows and self.rows[-1][0].y 
                < Bubble.BUBBLE_DIAMETER//2 + Bubble_Grid.BUBBLE_PADDING):
            return
        
        if speed_rows:
            speed_rows -=1
            
        if not self.rows:
            y = -BUBBLE_DIAMETER // 2 #Barely off the screen
        else:
            y = self.rows[-1][0].y - (Bubble_Grid.BUBBLE_PADDING
                                      + Bubble.BUBBLE_DIAMETER)
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

    def pruneBottomRow(self, HEIGHT):
        if self.rows and self.rows[0][0].y > HEIGHT + Bubble.BUBBLE_DIAMETER//2:
            del self.rows[0]