"""
Module contains the Ship and Cross classes
"""

from math import atan2
from dist import *

from config import HULL_RADIUS, HIT_GROW, SHIP_ACCEL, WIDTH, HEIGHT, PURP, FLAME

class Ship(object):
    """
    Represents the player piloted ship.
    
    x, y: float x, y position in pixel
    color_list: list of RGB tuples for available bullet colors
    bullet_index: int index to the color_list for current bullet color
    final_radius: int outer radius of the ship
    current_radius: int animates 1 pix per update towards final_radius
    velx, vely: float x, y velocity in pix/ms
    ethrust, wthrust, nthrust, sthrust: bool thrust indicators to draw flames
    cross: Cross object represents cross-hair for aiming bullets
    """

    def __init__(self, pos, color_list):
        """
        Initialize location, size, color, thrusters and cross-hair.
        """
        self.x, self.y = pos
        self.bullet_colors = color_list
        self.bullet_index = 0
        self.final_radius = HULL_RADIUS
        self.current_radius = 0
        self.velx, self.vely  = 0, 0
        self.ethrust = False
        self.wthrust = False
        self.nthrust = False
        self.sthrust = False
        self.cross = Cross()

    def __str__(self):
        """
        Returns formatted string for printing
        """
        atts = ['\t' + a + ': ' + str(v) for a,v in self.__dict__.items()]
        return type(self).__name__ + ' object:\n' + '\n'.join(atts)

    def draw(self, screen):
        """
        Given a PGZero screen object, draw the ship, thrusters and cross-hair.
        """
        self.cross.draw(screen, self.get_color())

        screen.draw.circle((self.x, self.y), self.current_radius,
            PURP) #outer hull

        screen.draw.filled_circle((self.x, self.y), HULL_RADIUS//4,
            self.bullet_colors[self.bullet_index]) #central bullet indicator

        if self.nthrust: # North, Boost Down
            screen.draw.filled_circle((self.x, self.y-self.current_radius),
                                      HULL_RADIUS//4 , FLAME)
        if self.sthrust: # South, Boost Up
            screen.draw.filled_circle((self.x, self.y+self.current_radius),
                                      HULL_RADIUS//4 , FLAME)

        if self.ethrust: # East, Boost left
            screen.draw.filled_circle((self.x+self.current_radius, self.y),
                                      HULL_RADIUS//4 , FLAME)

        if self.wthrust: # West, Boost right
            screen.draw.filled_circle((self.x-self.current_radius, self.y),
                                      HULL_RADIUS//4 , FLAME)

    def update(self, time_delta, keyboard, keys):
        """
        Wrapper function updates the ship's hull size and moves the ship.
        """
        self.update_hull()
        self.move(time_delta, keyboard, keys)

    def update_hull(self):
        """
        Animates the shrinking and growing of the ship's hull 1 pixel per update
        """
        if self.current_radius < self.final_radius:
            self.current_radius += 1
        elif self.current_radius > self.final_radius:
            self.current_radius -= 1

    def move(self, time_delta, keyboard, keys):
        """
        Given time elapsed since last update, keyboard and key pgzero objects,
         width and height of the game board: Update the ship's position,
         velocity and thrust indicators.
        """
        # Update horizontal velocity and thrust indicators
        if keyboard[keys.A] and keyboard[keys.D]:
            self.ethrust = True
            self.wthrust = True
        elif keyboard[keys.A]:
            self.velx -= SHIP_ACCEL * time_delta
            self.ethrust = True
            self.wthrust = False
        elif keyboard[keys.D]:
            self.velx += SHIP_ACCEL * time_delta
            self.ethrust = False
            self.wthrust = True
        else: # Decelerate in the horizontal plane if 'A' or 'D' not depressed.
            self.ethrust = False
            self.wthrust = False
            sign = 1
            if self.velx < 0:
                sign = -1
            self.velx = abs(self.velx) - SHIP_ACCEL * time_delta
            if self.velx < 0:
                self.velx = 0
            else:
                self.velx *= sign

        # Update vertical velocity and thrust indicators
        if keyboard[keys.W] and keyboard[keys.S]:
            self.nthrust = True
            self.sthrust = True
        elif keyboard[keys.W]:
            self.vely -= SHIP_ACCEL * time_delta
            self.sthrust = True
            self.nthrust = False
        elif keyboard[keys.S]:
            self.vely += SHIP_ACCEL * time_delta
            self.nthrust = True
            self.sthrust = False
        else: # Decelerate in the vertical plane if 'W' or 'S' not depressed.
            self.nthrust = False
            self.sthrust = False
            sign = 1
            if self.vely < 0:
                sign = -1
            self.vely = abs(self.vely) - SHIP_ACCEL * time_delta
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
        """
        Returns the color of bullet the ship is firing
        """
        return self.bullet_colors[self.bullet_index]

    def set_colors(self, color_list):
        """
        Updates the color of bullets the ship may fire
        """
        self.bullet_colors = color_list
        self.bullet_index = 0

    def cycle_color(self):
        """
        Move to the next possible bullet color
        """
        self.bullet_index = (self.bullet_index+1)%len(self.bullet_colors)

    def reset_hull_size(self):
        """
        Reset the ship's hull back to it's original size
        """
        self.final_radius = HULL_RADIUS

    def hit_ship(self, x, y, radius):
        """
        returns boolean indicating if the player's ship collides with a bubble
        """
        kill_zone = self.current_radius + radius
        sx, sy = self.x, self.y
        if is_close(sx, sy, x, y, kill_zone):
            d = distance(sx, sy, x, y)
            if d < kill_zone:
                self.final_radius += HIT_GROW
                return True

        return False

    def get_angle(self, pos):
        """
        Returns the angle between a given position and the player's ship in
         radians.
        """
        return atan2(self.y - pos[1], - (self.x - pos[0]))

class Cross(object):
    """
    Represents colored cross-hairs for aiming.
    pos: tuple of floats x, y position in pix
    """
    def __init__(self):
        """
        Initialize position to top left of screen
        """
        self.pos = (0,0)

    def draw(self, screen, color):
        """
        Given a PGZero screen object and a color, draws cross-hairs to match
         ship's selected bullet color
        """
        x, y = self.pos
        b = HULL_RADIUS
        screen.draw.line((x-b//2, y), (x-b//4, y), color)
        screen.draw.line((x+b//2, y), (x+b//4, y), color)
        screen.draw.line((x, y-b//2), (x, y-b//4), color)
        screen.draw.line((x, y+b//2), (x, y+b//4), color)