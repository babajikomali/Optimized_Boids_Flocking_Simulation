from Point import Point
from Circle import Circle 
from Rectangle import Rectangle
import pygame 

class QuadTree:
    def __init__(self, rect: Rectangle, screen: pygame.display, screen_width: float = 1200.0, screen_height: float = 700.0, capacity: int = 0) -> None:
        self.rect = rect
        self.capacity = capacity
        self.points = []
        self.isDivided = False
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height

    def show(self) -> None:
        pygame_rect = pygame.Rect(self.rect.x-self.rect.w, self.screen_height-(self.rect.y +
                                                                               self.rect.h), self.rect.w*2, self.rect.h*2)
        pygame.draw.rect(self.screen, (0, 255, 0), pygame_rect, 1)
        if self.isDivided == False:
            return
        self.northeast.show()
        self.northwest.show()
        self.southeast.show()
        self.southwest.show()

    def subdivide(self) -> None:
        x, y, w, h = self.rect.x, self.rect.y, self.rect.w, self.rect.h
        ne = Rectangle(x+w/2, y+h/2, w/2, h/2)
        nw = Rectangle(x-w/2, y+h/2, w/2, h/2)
        se = Rectangle(x+w/2, y-h/2, w/2, h/2)
        sw = Rectangle(x-w/2, y-h/2, w/2, h/2)
        self.northeast = QuadTree(
            ne, self.screen, self.screen_width, self.screen_height, self.capacity)
        self.northwest = QuadTree(
            nw, self.screen, self.screen_width, self.screen_height, self.capacity)
        self.southeast = QuadTree(
            se, self.screen, self.screen_width, self.screen_height, self.capacity)
        self.southwest = QuadTree(
            sw, self.screen, self.screen_width, self.screen_height, self.capacity)
        self.isDivided = True

    def insertPoint(self, point: Point) -> bool:
        if not self.rect.isContain(point):
            return False
        elif len(self.points) < self.capacity:
            self.points.append(point)
            return True
        else:
            if not self.isDivided:
                self.subdivide()
            if self.northeast.insertPoint(point):
                return True
            if self.northwest.insertPoint(point):
                return True
            if self.southeast.insertPoint(point):
                return True
            if self.southwest.insertPoint(point):
                return True

    def query(self, circle: Circle):
        found = []
        if not self.rect.isIntersect(circle):
            return found
        else:
            for x in self.points:
                if circle.isContain(x) and x.idx != circle.idx:
                    found.append(int(x.idx+1))
            if self.isDivided:
                found.extend(self.northeast.query(circle))
                found.extend(self.northwest.query(circle))
                found.extend(self.southeast.query(circle))
                found.extend(self.southwest.query(circle))
            return found
