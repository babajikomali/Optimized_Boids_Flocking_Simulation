import random
import numba
from numba import njit
from numba.typed import List
from numba.experimental import jitclass

NUM_BOIDS = 100
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1200

# Quad-Tree Implementation

spec = [('x',numba.int32),('y',numba.int32)]
# @jitclass(spec)
class Point(object):
    def __init__(self, x:int = 0, y:int = 0) -> None:
        self.x = x
        self.y = y

spec = [('x',numba.int32),('y',numba.int32),('r',numba.int32)]
# @jitclass(spec)
class Circle(object):
    def __init__(self, x:int = 0, y:int = 0, r:int = 0) -> None:
        self.x = x
        self.y = y
        self.r = r
    
    def isContain(self, point:Point) -> bool:
        diff_x = abs(point.x - self.x)
        diff_y = abs(point.y - self.y)
        return (diff_x**2 + diff_y**2) <= self.r

spec = [('x',numba.int32),('y',numba.int32),('w',numba.int32),('h',numba.int32)]
# @jitclass(spec)
class Rectangle:
    def __init__(self, x:int = 0, y:int = 0, w:int = 0, h:int = 0) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    def isContain(self, point:Point):
        x, y = point.x, point.y
        return (self.x-self.w <= x <= self.x+self.w) and (self.y-self.h <= y <= self.y+self.h)
    
    def isIntersect(self, circle:Circle):
        diff_x = abs(circle.x - self.x)
        diff_y = abs(circle.y - self.y)

        if diff_x > (self.w+circle.r) : return False
        if diff_y > (self.h+circle.r) : return False
        if diff_x <= self.w : return True
        if diff_y <= self.h : return True

        corner_dist = (diff_x - self.w)**2 + (diff_y - self.h)**2
        return corner_dist <= circle.r**2

# @jitclass(spec)
class QuadTree:
    def __init__(self, rect:Rectangle, capacity:int = 0) -> None:
        self.rect = rect
        self.capacity =  capacity
        self.points = []
        self.isDivided :bool = False
    
    def subdivide(self) -> None:
        x, y, w, h = self.rect.x, self.rect.y, self.rect.w, self.rect.h
        ne = Rectangle(x+w/2, y+h/2, w/2, h/2)
        nw = Rectangle(x-w/2, y+h/2, w/2, h/2)
        se = Rectangle(x+w/2, y-h/2, w/2, h/2)
        sw = Rectangle(x-w/2, y-h/2, w/2 , h/2)
        self.northeast = QuadTree(ne,self.capacity)
        self.northwest = QuadTree(nw,self.capacity)
        self.southeast = QuadTree(se,self.capacity)
        self.southwest = QuadTree(sw,self.capacity)
        self.isDivided = True

    def insertPoint(self, point:Point) -> bool:
        if not self.rect.isContain(point) : return False
        elif len(self.points)<self.capacity :
            self.points.append(point)
            return True
        else :
            if not self.isDivided : self.subdivide()
            if self.northeast.insertPoint(point)   : return True
            if self.northwest.insertPoint(point) : return True
            if self.southeast.insertPoint(point) : return True
            if self.southwest.insertPoint(point) : return True
    
    def query(self, circle:Circle):
        found = []
        if not self.rect.isIntersect(circle) : return found
        else :
            for x in self.points:
                if circle.isContain(x) : found.append(x)
            if self.isDivided:
                found.extend(self.northeast.query(circle))
                found.extend(self.northwest.query(circle))
                found.extend(self.southeast.query(circle))
                found.extend(self.southwest.query(circle))
            return found

#-----------------------------------------------

rootQuadTree = QuadTree(Rectangle(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SCREEN_WIDTH/2, SCREEN_HEIGHT/2), 4)

import time
start_time = time.time()
for _ in range(100 * 60):
    rootQuadTree.insertPoint(Point(random.randint(0,1200), random.randint(0,600)))
for _ in range(100 * 60):
    result = rootQuadTree.query(Circle(random.randint(0,1200), random.randint(0,600),50))
print(time.time()-start_time)
