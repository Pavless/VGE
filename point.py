from collections import namedtuple

EPS = 1e-7

Point = namedtuple("Point", ["x", "y"])

def min_y_point(p1: Point, p2: Point):
    """Returns lower of the two given points"""
    return p1 if p1.y < p2.y else p2

def max_y_point(p1: Point, p2: Point):
    """Returns higher of the two given points"""
    return p1 if p1.y > p2.y else p2