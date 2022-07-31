from Point import Point
from Circle import Circle

class Rectangle:
    def __init__(self, x: float = 0, y: float = 0, w: float = 0, h: float = 0) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def isContain(self, point: Point):
        x, y = point.x, point.y
        return (self.x-self.w <= x <= self.x+self.w) and (self.y-self.h <= y <= self.y+self.h)

    def isIntersect(self, circle: Circle):
        diff_x = abs(circle.x - self.x)
        diff_y = abs(circle.y - self.y)

        if diff_x > (self.w+circle.r):
            return False
        if diff_y > (self.h+circle.r):
            return False
        if diff_x <= self.w:
            return True
        if diff_y <= self.h:
            return True

        corner_dist = (diff_x - self.w)**2 + (diff_y - self.h)**2
        return corner_dist <= circle.r**2
