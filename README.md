# RingLeader
PyGame Zero Falling Matcher Game

## Dependencies
Python 3
pgzero

## Running
from console
'''python ring_leader.py'''

## INSTRUCTIONS
### Controls
- Maneuver Ship with W,A,S,D
- Aim with mouse and crosshairs
- Left Mouse Button Fires Bubbles
- Space Bar cycles available colors
- Right click to speed out the next row
- p to pause

### Gameplay
- Fire bubbles to make rows and columns of 
  4 consecutive bubbles of the same color.
- Maneuver your ship to avoid all Bubbles. 
- Bubbles creeping downward will destroy your ship on contact.
- Falling bubbles which strike your ship will cause it to grow.

### Scoring
- Awarded points scale exponentially with the number 
  of bubbles popped in a single combo. Bubbles created 
  by player bullets do not score points.
- You cannot score more points than required to reach 
  the next level with a combo.
- Points are awarded for any falling bubbles 
  which do not strike the player's vessel.
- Points are deducted for any bullets which fly out of bounds.

## Planned Improvements
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
