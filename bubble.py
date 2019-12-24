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
        screen.draw.filled_circle((self.x, self.y), 
                                   Bubble.BUBBLE_DIAMETER//2, 
                                   self.color)

class Bullet(Bubble):
    def __init__(self, x, y, color, ang):
        self.angle = ang
        super().__init__(x, y, color)
        
class Dropper(Bubble):
    #falling_bubbles = [] #[[x_pos, y_pos, color, vely, column], ...more droppers]
    def __init__(self, x, y, color, vely, column):
        self.vely = vely
        self.column = column
        super().__init__(x, y, color)

class Bubble_List(object):
    def __init__(self):
        self.contents = []
    
    def __str__(self):
        s = 'Bullets Object:\n'
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