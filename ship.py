"""
Ring Leader
"""

from math import atan2
from dist import *

class Cross(object):
    def __init__(self, size):
        self.pos = (0,0)
        self.size = size
    
    # Procedure draws cross hairs to match player selected bullet color
    def draw(self, screen, color):
        x, y = self.pos
        b = self.size
        screen.draw.line((x-b//2, y), (x-b//4, y), color)
        screen.draw.line((x+b//2, y), (x+b//4, y), color)
        screen.draw.line((x, y-b//2), (x, y-b//4), color)
        screen.draw.line((x, y+b//2), (x, y+b//4), color)

class Ship(object):
    PURP = (62, 7, 120)   # Ship perimeter color
    FLAME = (237, 150, 9) # Ship Thruster Color
    SHIP_ACCEL = .0003 #W,A,S,D depressed, speedup this much, decel on release
    
    def __init__(self, pos, color_list, bubble_diameter, accel):
        self.x, self.y = pos
        self.bullet_colors = color_list
        self.bullet_index = 0
        self.final_radius = bubble_diameter
        self.initial_radius = bubble_diameter
        self.current_radius = 0
        self.accel = accel
        self.velx, self.vely  = 0, 0
        self.ethrust = False
        self.wthrust = False
        self.nthrust = False
        self.sthrust = False
        self.cross = Cross(bubble_diameter)
    
    def __str__(self):
        atts = ['\t' + a + ': ' + str(v) for a,v in self.__dict__.items()]
        return type(self).__name__ + ' object:\n' + '\n'.join(atts)
    
    def draw(self, screen):
        self.cross.draw(screen, self.get_color())
        
        screen.draw.circle((self.x, self.y), self.current_radius,
            Ship.PURP) #outer hull
            
        screen.draw.filled_circle((self.x, self.y), self.initial_radius//4,
            self.bullet_colors[self.bullet_index]) #bullet indicator
            
        if self.nthrust: # North, Boost Down
            screen.draw.filled_circle((self.x, self.y-self.current_radius),
                                      self.initial_radius//4 , Ship.FLAME)
        if self.sthrust: # South, Boost Up
            screen.draw.filled_circle((self.x, self.y+self.current_radius),
                                      self.initial_radius//4 , Ship.FLAME)
        
        if self.ethrust: # East, Boost left
            screen.draw.filled_circle((self.x+self.current_radius, self.y),
                                      self.initial_radius//4 , Ship.FLAME)
                                      
        if self.wthrust: # West, Boost right
            screen.draw.filled_circle((self.x-self.current_radius, self.y),
                                      self.initial_radius//4 , Ship.FLAME)
                                      
    def update(self, time_delta, keyboard, keys, WIDTH, HEIGHT):
        self.update_hull()
        self.move(time_delta, keyboard, keys, WIDTH, HEIGHT)
            
    def update_hull(self):
        if self.current_radius < self.final_radius:
            self.current_radius += 1
        elif self.current_radius > self.final_radius:
            self.current_radius -= 1
            
    def move(self, time_delta, keyboard, keys, WIDTH, HEIGHT):
        # Update horizontal velocity and thrust indicators
        if keyboard[keys.A] and keyboard[keys.D]:
            self.ethrust = True
            self.wthrust = True
        elif keyboard[keys.A]:
            self.velx -= self.accel
            self.ethrust = True
            self.wthrust = False
        elif keyboard[keys.D]:
            self.velx += self.accel
            self.ethrust = False
            self.wthrust = True
        else: # Decelerate in the horizontal plane if A or D not depressed.
            self.ethrust = False
            self.wthrust = False
            sign = 1
            if self.velx < 0:
                sign = -1
            self.velx = abs(self.velx) - self.accel
            if self.velx < 0:
                self.velx = 0
            else:
                self.velx *= sign

        # Update vertical velocity and thrust indicators
        if keyboard[keys.W] and keyboard[keys.S]:
            self.nthrust = True
            self.sthrust = True
        elif keyboard[keys.W]:
            self.vely -= self.accel
            self.sthrust = True
            self.nthrust = False
        elif keyboard[keys.S]:
            self.vely += self.accel
            self.nthrust = True
            self.sthrust = False
        else: # Decelerate in the vertical plane if W or S not depressed.
            self.nthrust = False
            self.sthrust = False
            sign = 1
            if self.vely < 0:
                sign = -1
            self.vely = abs(self.vely) - self.accel
            if self.vely < 0:
                self.vely = 0
            else:
                self.vely *= sign

        # Update position
        self.x += self.velx * time_delta
        self.y += self.vely * time_delta
        
        # Wrap ship movement in horizontal plane
        if self.x > WIDTH:
            self.x = 0
        elif self.x < 0:
            self.x = WIDTH
        
        # Constrain ship movement in vertical plane
        if self.y > HEIGHT:
            self.y = HEIGHT
            self.vely = 0
        elif self.y < 0:
            self.y = 0
            self.vely = 0
            
    def get_color(self):
        return self.bullet_colors[self.bullet_index]
    
    def set_colors(self, color_list):
        self.bullet_colors = color_list
        self.bullet_index = 0
    
    def cycle_color(self):
        self.bullet_index = (self.bullet_index+1)%len(self.bullet_colors)
        
    def reset_hull_size(self):
        self.final_radius = self.initial_radius
        
    # Function returns boolean indicating if the player's ship collides with
    #  a bubble
    def hit_ship(self, x, y, radius):
        kill_zone = self.current_radius + radius
        sx, sy = self.x, self.y
        if is_close(sx, sy, x, y, kill_zone):
            d = distance(sx, sy, x, y)
            if d < kill_zone:                    
                return True
        
        return False
        
    def get_angle(self, pos):
        return atan2(self.y - pos[1], - (self.x - pos[0]))