import pygame
import random
import numba
from numba import njit

NUM_BOIDS = 100
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1200

# Quad-Tree Implementation

class Point:
    def __init__(self, surface:pygame.Surface , x:int = 0, y:int = 0) -> None:
        self.x = x
        self.y = y
        pygame.draw.circle(surface, (255, 255, 255), (self.x, SCREEN_HEIGHT-self.y), 3)

class Circle:
    def __init__(self, x:int = 0, y:int = 0, r:int = 0) -> None:
        self.x = x
        self.y = y
        self.r = r
    
    def isContain(self, point:Point) -> bool:
        diff_x = abs(point.x - self.x)
        diff_y = abs(point.y - self.y)
        return (diff_x**2 + diff_y**2) <= self.r

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

class QuadTree:
    def __init__(self, surface:pygame.Surface, rect:Rectangle, capacity:int = 0) -> None:
        self.rect = rect
        self.capacity =  capacity
        self.points = []
        self.isDivided = False
        self.surface = surface

        pygame_rect = pygame.Rect(rect.x-rect.w,SCREEN_HEIGHT-(rect.y+rect.h), rect.w*2, rect.h*2)
        pygame.draw.rect(surface, (255,255,255), pygame_rect, 1)
    
    def subdivide(self) -> None:
        x, y, w, h = self.rect.x, self.rect.y, self.rect.w, self.rect.h
        ne = Rectangle(x+w/2, y+h/2, w/2, h/2)
        nw = Rectangle(x-w/2, y+h/2, w/2, h/2)
        se = Rectangle(x+w/2, y-h/2, w/2, h/2)
        sw = Rectangle(x-w/2, y-h/2, w/2 , h/2)
        self.northeast = QuadTree(self.surface, ne,self.capacity)
        self.northwest = QuadTree(self.surface, nw,self.capacity)
        self.southeast = QuadTree(self.surface, se,self.capacity)
        self.southwest = QuadTree(self.surface, sw,self.capacity)
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

# supressing the pygame hello message
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

pygame.init()
FPS = 60
FONT = pygame.font.SysFont('ComicNeue-Regular.ttf',20)
pygame.display.set_caption("Quad Tree")
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
clock = pygame.time.Clock()
color_red = (241, 38, 11)
color_green = (124, 252, 0)
exit = False

screen.fill((0, 0, 0))
rootQuadTree = QuadTree(screen, Rectangle(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SCREEN_WIDTH/2, SCREEN_HEIGHT/2), 4)

for _ in range(15):
        rootQuadTree.insertPoint(Point(screen, random.randint(0,1200), random.randint(0,600)))
i=0
while not exit:
    # keyboard events
    for event in pygame.event.get():
        #closing pygame window
        if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_q):
            exit = True

    
    text_y = 10
    text_surface = FONT.render(f"FPS : {int(clock.get_fps())}",True,color_red)
    screen.blit(text_surface,(SCREEN_WIDTH-150, text_y))

    i += 1
    if i%30 : rootQuadTree.insertPoint(Point(screen, random.randint(0,SCREEN_WIDTH), random.randint(0,600)))

    pygame.display.update()
    if FPS: clock.tick(FPS)
    else : clock.tick()

pygame.quit()