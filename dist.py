"""
This package provides city block and euclidian distance functions. Use
 is_close() for speed and distance() for precision.
"""

def distance(x1, y1, x2, y2):
    """
    returns euclidian distance between 2 given points
    """

    return ((x1-x2)**2 + (y1-y2)**2)**.5

def is_close(x1, y1, x2, y2, d):
    """
    Function computes lightweight city block proximity given 2 coordinates and a
     distance. Returns true if the two points are closer or equal to distance.
    """

    if abs(y1-y2) <= d and abs(x1-x2) <= d:
        return True
    return False