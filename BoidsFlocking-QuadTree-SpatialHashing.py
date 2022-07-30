import os
import sys
import pygame
import numpy as np

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'


class Point:
    def __init__(self, x: float = 0, y: float = 0, idx: int = 0) -> None:
        self.x = x
        self.y = y
        self.idx = idx

class Circle:
    def __init__(self, x: float = 0, y: float = 0, r: float = 0, idx: int = 0) -> None:
        self.x = x
        self.y = y
        self.r = r
        self.idx = idx

    def isContain(self, point: Point) -> bool:
        diff_x = abs(point.x - self.x)
        diff_y = abs(point.y - self.y)

        if diff_x > self.r:
            return False
        if diff_y > self.r:
            return False
        if diff_x + diff_y <= self.r:
            return True
        if diff_x**2 + diff_y**2 <= self.r**2:
            return True

        return False


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

class SpatialHash:
    def __init__(self,screen_width: float = 1200.0, screen_height: float = 700.0 ,radius: float = 0) -> None:
        self.screen_height = screen_height
        self.screen_width =screen_width
        self.radius = radius
        self.hash = {}
    
    def hashPoint(self, point: Point):
        xidx = int(point.x/self.radius)
        yidx = int(point.y/self.radius)
        return xidx,yidx

    def insertPoint(self, point: Point) ->None:
        self.hash.setdefault( self.hashPoint(point), [] ).append(point.idx)

    def queryPoint(self, point: Point):
        found = []
        xidx = int(point.x/self.radius)
        yidx = int(point.y/self.radius)

        keys = [(xidx,yidx),(xidx+1,yidx+1),(xidx-1,yidx-1),(xidx-1,yidx+1),
                (xidx+1,yidx-1),(xidx,yidx+1),(xidx,yidx-1),(xidx+1,yidx),(xidx-1,yidx)]

        for key in keys:
            if key in self.hash:
                found.extend(self.hash[key])
        
        if point.idx in found:
            found.remove(point.idx)
        return found

class BoidsFlock:

    ALIGN_RADIUS = 50
    ALIGN_MAX_FORCE = 0.2
    ALIGN_MAX_SPEED = 4.0

    COHESION_RADIUS = 50
    COHESION_MAX_FORCE = 0.2
    COHESION_MAX_SPEED = 4.0

    SEPARATION_RADIUS = 50
    SEPARATION_MAX_FORCE = 0.2
    SEPARATION_MAX_SPEED = 4.0

    def __init__(self, num_boids: int = 10, screen_width: int = 1200, screen_height: int = 700) -> None:

        self.boids = num_boids
        self.screen_height = screen_height
        self.screen_width = screen_width

        self.boids_pos = np.random.uniform(
            0, max(screen_width, screen_height), size=(num_boids, 2))  # Boids position

        self.boids_vel = np.random.uniform(-0.5, 0.5, size=(num_boids, 2))
        self.boids_acc = np.zeros(
            shape=(num_boids, 2), dtype=np.float32)  # Boids acceleration
        self.boids_vel = BoidsFlock.setMagnitude(self.boids_vel, 1)
        self.rootQuadTree = QuadTree(Rectangle(self.screen_width/2, self.screen_height/2,
                                               self.screen_width/2, self.screen_height/2), 4)

    @staticmethod
    def setMagnitude(array: np.ndarray, val: float):
        magnitude = np.linalg.norm(array, axis=1)[:, np.newaxis]
        array = np.divide(array, magnitude, where=(magnitude != 0))
        return array * val

    def __update(self):

        self.boids_vel += self.boids_acc  # velocity update
        self.boids_pos += self.boids_vel  # position update

        # Trick : division by negative numbers
        # http://python-history.blogspot.com/2010/08/why-pythons-integer-division-floors.html
        self.boids_pos[:, 0] %= self.screen_width
        self.boids_pos[:, 1] %= self.screen_height

        self.boids_acc.fill(0)  # zero the acceleration
        # allow boids to move with max velocity in the desired direction
        self.boids_vel = BoidsFlock.setMagnitude(
            self.boids_vel, BoidsFlock.ALIGN_MAX_SPEED)
    
    def __hash(self):
        align_hash = SpatialHash(self.screen_width, self.screen_height, BoidsFlock.ALIGN_RADIUS)
        cohesion_hash = SpatialHash(self.screen_width, self.screen_height, BoidsFlock.COHESION_RADIUS)
        separation_hash = SpatialHash(self.screen_width, self.screen_height, BoidsFlock.SEPARATION_RADIUS)

        for i, pos in enumerate(self.boids_pos):
            point = Point(pos[0],pos[1],i)
            align_hash.insertPoint(point)
            cohesion_hash.insertPoint(point)
            separation_hash.insertPoint(point)

        align_indices = []
        cohesion_indices = []
        separation_indices = []

        for i, pos in enumerate(self.boids_pos):
            point = Point(pos[0],pos[1],i)
            align_indices.append(align_hash.queryPoint(point))
            cohesion_indices.append(cohesion_hash.queryPoint(point))
            separation_indices.append(separation_hash.queryPoint(point))

        align_lens = [len(l) for l in align_indices]
        align_maxlen = max(align_lens)
        align_idx = np.zeros((len(align_indices), align_maxlen), int)
        mask = np.arange(align_maxlen) < np.array(align_lens)[:, None]
        align_idx[mask] = np.concatenate(align_indices)

        cohesion_lens = [len(l) for l in cohesion_indices]
        cohesion_maxlen = max(cohesion_lens)
        cohesion_idx = np.zeros((len(cohesion_indices), cohesion_maxlen), int)
        mask = np.arange(cohesion_maxlen) < np.array(cohesion_lens)[:, None]
        cohesion_idx[mask] = np.concatenate(cohesion_indices)

        separation_lens = [len(l) for l in separation_indices]
        separation_maxlen = max(separation_lens)
        separation_idx = np.zeros(
            (len(separation_indices), separation_maxlen), int)
        mask = np.arange(separation_maxlen) < np.array(
            separation_lens)[:, None]
        separation_idx[mask] = np.concatenate(separation_indices)

        return align_idx, cohesion_idx, separation_idx

    def hashflock(self):

        align_idx, cohesion_idx, separation_idx = self.__hash()

        boids_pos = np.insert(self.boids_pos, [0], [0.0], axis=0)
        boids_vel = np.insert(self.boids_vel, [0], [0.0], axis=0)

        align_vel = boids_vel[align_idx]
        cohesion_pos = boids_pos[cohesion_idx]
        separation_pos = boids_pos[separation_idx]

        align_steering = np.sum(align_vel, axis=1)
        cohesion_steering = np.sum(cohesion_pos, axis=1)
        separation_steering = np.sum(separation_pos, axis=1)

        align_count = np.count_nonzero(align_idx, axis=1)
        align_count = np.transpose(align_count)[:, np.newaxis]
        cohesion_count = np.count_nonzero(cohesion_idx, axis=1)
        cohesion_count = np.transpose(cohesion_count)[:, np.newaxis]
        separation_count = np.count_nonzero(separation_idx, axis=1)
        separation_count = np.transpose(separation_count)[:, np.newaxis]

        align_count[align_count == 0] = 1
        cohesion_count[cohesion_count == 0] = 1
        separation_count[separation_count == 0] = 1

        sep_boids_pos = self.boids_pos
        np.broadcast(separation_count, sep_boids_pos)
        separation_steering -= (separation_count*sep_boids_pos)

        np.broadcast(align_steering, align_count)
        align_steering = align_steering/align_count
        np.broadcast(cohesion_steering, cohesion_count)
        cohesion_steering = cohesion_steering/cohesion_count
        np.broadcast(separation_steering, separation_count)
        separation_steering = separation_steering/separation_count

        align_steering -= self.boids_vel
        align_steering = BoidsFlock.setMagnitude(
            align_steering, BoidsFlock.ALIGN_MAX_SPEED)
        if(np.linalg.norm(align_steering) > BoidsFlock.ALIGN_MAX_FORCE):
            align_steering = BoidsFlock.setMagnitude(
                align_steering, BoidsFlock.ALIGN_MAX_FORCE)

        cohesion_steering -= self.boids_pos
        cohesion_steering = BoidsFlock.setMagnitude(
            cohesion_steering, BoidsFlock.COHESION_MAX_SPEED)
        cohesion_steering -= self.boids_vel
        if(np.linalg.norm(cohesion_steering) > BoidsFlock.COHESION_MAX_FORCE):
            cohesion_steering = BoidsFlock.setMagnitude(
                cohesion_steering, BoidsFlock.COHESION_MAX_FORCE)

        separation_steering = BoidsFlock.setMagnitude(
            separation_steering, BoidsFlock.SEPARATION_MAX_SPEED)
        separation_steering -= self.boids_vel
        if(np.linalg.norm(separation_steering) > BoidsFlock.SEPARATION_MAX_FORCE):
            separation_steering = BoidsFlock.setMagnitude(
                separation_steering, BoidsFlock.SEPARATION_MAX_FORCE)

        self.boids_acc = align_steering + cohesion_steering - separation_steering

        self.__update()
    
    def __tree(self):

        align_indices = []
        cohesion_indices = []
        separation_indices = []

        for i, pos in enumerate(self.boids_pos):
            align_circle = Circle(pos[0], pos[1], BoidsFlock.ALIGN_RADIUS, i)
            cohesion_circle = Circle(pos[0], pos[1], BoidsFlock.COHESION_RADIUS, i)
            separation_circle = Circle(pos[0], pos[1], BoidsFlock.SEPARATION_RADIUS, i)

            align_nearby = self.rootQuadTree.query(align_circle)
            cohesion_nearby = self.rootQuadTree.query(cohesion_circle)
            separation_nearby = self.rootQuadTree.query(separation_circle)

            align_indices.append(align_nearby)
            cohesion_indices.append(cohesion_nearby)
            separation_indices.append(separation_nearby)

        align_lens = [len(l) for l in align_indices]
        align_maxlen = max(align_lens)
        align_idx = np.zeros((len(align_indices), align_maxlen), int)
        mask = np.arange(align_maxlen) < np.array(align_lens)[:, None]
        align_idx[mask] = np.concatenate(align_indices)

        cohesion_lens = [len(l) for l in cohesion_indices]
        cohesion_maxlen = max(cohesion_lens)
        cohesion_idx = np.zeros((len(cohesion_indices), cohesion_maxlen), int)
        mask = np.arange(cohesion_maxlen) < np.array(cohesion_lens)[:, None]
        cohesion_idx[mask] = np.concatenate(cohesion_indices)

        separation_lens = [len(l) for l in separation_indices]
        separation_maxlen = max(separation_lens)
        separation_idx = np.zeros(
            (len(separation_indices), separation_maxlen), int)
        mask = np.arange(separation_maxlen) < np.array(
            separation_lens)[:, None]
        separation_idx[mask] = np.concatenate(separation_indices)

        return align_idx, cohesion_idx, separation_idx

    def treeflock(self):

        align_idx, cohesion_idx, separation_idx = self.__tree()

        boids_pos = np.insert(self.boids_pos, [0], [0.0], axis=0)
        boids_vel = np.insert(self.boids_vel, [0], [0.0], axis=0)

        align_vel = boids_vel[align_idx]
        cohesion_pos = boids_pos[cohesion_idx]
        separation_pos = boids_pos[separation_idx]

        align_steering = np.sum(align_vel, axis=1)
        cohesion_steering = np.sum(cohesion_pos, axis=1)
        separation_steering = np.sum(separation_pos, axis=1)

        align_count = np.count_nonzero(align_idx, axis=1)
        align_count = np.transpose(align_count)[:, np.newaxis]
        cohesion_count = np.count_nonzero(cohesion_idx, axis=1)
        cohesion_count = np.transpose(cohesion_count)[:, np.newaxis]
        separation_count = np.count_nonzero(separation_idx, axis=1)
        separation_count = np.transpose(separation_count)[:, np.newaxis]

        align_count[align_count == 0] = 1
        cohesion_count[cohesion_count == 0] = 1
        separation_count[separation_count == 0] = 1

        sep_boids_pos = self.boids_pos
        np.broadcast(separation_count, sep_boids_pos)
        separation_steering -= (separation_count*sep_boids_pos)

        np.broadcast(align_steering, align_count)
        align_steering = align_steering/align_count
        np.broadcast(cohesion_steering, cohesion_count)
        cohesion_steering = cohesion_steering/cohesion_count
        np.broadcast(separation_steering, separation_count)
        separation_steering = separation_steering/separation_count

        align_steering -= self.boids_vel
        align_steering = BoidsFlock.setMagnitude(
            align_steering, BoidsFlock.ALIGN_MAX_SPEED)
        if(np.linalg.norm(align_steering) > BoidsFlock.ALIGN_MAX_FORCE):
            align_steering = BoidsFlock.setMagnitude(
                align_steering, BoidsFlock.ALIGN_MAX_FORCE)

        cohesion_steering -= self.boids_pos
        cohesion_steering = BoidsFlock.setMagnitude(
            cohesion_steering, BoidsFlock.COHESION_MAX_SPEED)
        cohesion_steering -= self.boids_vel
        if(np.linalg.norm(cohesion_steering) > BoidsFlock.COHESION_MAX_FORCE):
            cohesion_steering = BoidsFlock.setMagnitude(
                cohesion_steering, BoidsFlock.COHESION_MAX_FORCE)

        separation_steering = BoidsFlock.setMagnitude(
            separation_steering, BoidsFlock.SEPARATION_MAX_SPEED)
        separation_steering -= self.boids_vel
        if(np.linalg.norm(separation_steering) > BoidsFlock.SEPARATION_MAX_FORCE):
            separation_steering = BoidsFlock.setMagnitude(
                separation_steering, BoidsFlock.SEPARATION_MAX_FORCE)

        self.boids_acc = align_steering + cohesion_steering - separation_steering

        self.__update()

    def flock(self):

        transpose_boid_pos = np.transpose(self.boids_pos)
        reshape_boids_pos = self.boids_pos.reshape((self.boids, 2, 1))
        np.broadcast(transpose_boid_pos, reshape_boids_pos)
        masked_boids_dist = transpose_boid_pos-reshape_boids_pos
        distance_boids = np.square(transpose_boid_pos-reshape_boids_pos)
        distance_boids = np.transpose(np.sqrt(np.sum(distance_boids, axis=1)))

        mask_array = np.full((self.boids, self.boids), True, dtype=bool)
        np.fill_diagonal(mask_array, False)

        align_check = distance_boids < BoidsFlock.ALIGN_RADIUS
        cohesion_check = distance_boids < BoidsFlock.COHESION_RADIUS
        separation_check = distance_boids < BoidsFlock.SEPARATION_RADIUS

        align_check = np.logical_and(align_check, mask_array)
        cohesion_check = np.logical_and(cohesion_check, mask_array)
        separation_check = np.logical_and(separation_check, mask_array)
        separation_check = np.transpose(separation_check)

        align_count = np.count_nonzero(align_check, axis=0)
        cohesion_count = np.count_nonzero(cohesion_check, axis=0)
        separation_count = np.count_nonzero(separation_check, axis=0)

        align_check = align_check.reshape((self.boids, self.boids, 1))
        cohesion_check = cohesion_check.reshape((self.boids, self.boids, 1))
        separation_check = separation_check.reshape(
            (self.boids, 1, self.boids))

        np.broadcast(align_check, self.boids_vel)
        masked_boids_vel = self.boids_vel*align_check
        align_steering = np.sum(masked_boids_vel, axis=1)

        np.broadcast(cohesion_check, self.boids_pos)
        masked_boids_pos = self.boids_pos*cohesion_check
        cohesion_steering = np.sum(masked_boids_pos, axis=1)

        np.broadcast(separation_check, masked_boids_dist)
        separation_steering = np.sum(
            masked_boids_dist*separation_check, axis=2)

        align_count[align_count == 0] = 1
        cohesion_count[cohesion_count == 0] = 1
        separation_count[separation_count == 0] = 1

        align_steering = (np.transpose(align_steering)/align_count).T
        cohesion_steering = (np.transpose(cohesion_steering)/cohesion_count).T
        separation_steering = (np.transpose(
            separation_steering)/separation_count).T

        align_steering -= self.boids_vel
        align_steering = BoidsFlock.setMagnitude(
            align_steering, BoidsFlock.ALIGN_MAX_SPEED)
        if(np.linalg.norm(align_steering) > BoidsFlock.ALIGN_MAX_FORCE):
            align_steering = BoidsFlock.setMagnitude(
                align_steering, BoidsFlock.ALIGN_MAX_FORCE)

        cohesion_steering -= self.boids_pos
        cohesion_steering = BoidsFlock.setMagnitude(
            cohesion_steering, BoidsFlock.COHESION_MAX_SPEED)
        cohesion_steering -= self.boids_vel
        if(np.linalg.norm(cohesion_steering) > BoidsFlock.COHESION_MAX_FORCE):
            cohesion_steering = BoidsFlock.setMagnitude(
                cohesion_steering, BoidsFlock.COHESION_MAX_FORCE)

        separation_steering = BoidsFlock.setMagnitude(
            separation_steering, BoidsFlock.SEPARATION_MAX_SPEED)
        separation_steering -= self.boids_vel
        if(np.linalg.norm(separation_steering) > BoidsFlock.SEPARATION_MAX_FORCE):
            separation_steering = BoidsFlock.setMagnitude(
                separation_steering, BoidsFlock.SEPARATION_MAX_FORCE)

        self.boids_acc = align_steering + cohesion_steering - separation_steering

        self.__update()

    def addBoid(self, num: int = 1):

        self.boids += num

        # generating boids
        boids_pos = np.random.uniform(
            0, max(self.screen_width, self.screen_height), size=(num, 2))  # Boids position
        # Boids velocity
        boids_vel = np.random.uniform(-0.5, 0.5, size=(num, 2))
        boids_vel = BoidsFlock.setMagnitude(boids_vel, 1)

        # adding boids
        self.boids_pos = np.vstack((self.boids_pos, boids_pos))
        self.boids_vel = np.vstack((self.boids_vel, boids_vel))

    def reset(self):

        self.boids_pos = np.random.uniform(0, max(
            self.screen_width, self.screen_height), size=(self.boids, 2))  # Boids position
        # Boids velocity
        self.boids_vel = np.random.uniform(-0.5, 0.5, size=(self.boids, 2))


class Stimulation(BoidsFlock):

    COLOR_RED = (241, 38, 11)
    COLOR_GREEN = (124, 252, 0)

    def __init__(self, num_boids: int = 10, screen_width: int = 1200, screen_height: int = 700) -> None:
        super().__init__(num_boids, screen_width, screen_height)

        pygame.init()
        pygame.display.set_caption("flock simulation")
        self.FONT = pygame.font.SysFont('ComicNeue-Regular.ttf', 18)

        self.FPS = None
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
        self.exit = False

    def stimulate(self):

        while not self.exit:
            # keyboard events
            for event in pygame.event.get():
                #closing pygame window
                if event.type == pygame.QUIT:
                    self.exit = True

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_q:
                        self.exit = True
                    elif event.key == pygame.K_r:
                        self.reset()

            # # screen movement
            # pressed = pygame.key.get_pressed()

            # rendering
            self.screen.fill((0, 0, 0))
            self.rootQuadTree = QuadTree(Rectangle(self.screen_width/2, self.screen_height/2,
                                                   self.screen_width/2, self.screen_height/2),
                                         self.screen, self.screen_width, self.screen_height, 4)
            for i in range(self.boids):
                point = Point(self.boids_pos[i][0], self.boids_pos[i][1], i)
                self.rootQuadTree.insertPoint(point)

            # self.rootQuadTree.show()
            for pos in self.boids_pos:
                pygame.draw.circle(self.screen, (0, 255, 0),
                                   (pos[0], self.screen_height-pos[1]), 4)

            text_y = 10
            text_surface = self.FONT.render(
                f"FPS : {int(self.clock.get_fps())}", True, Stimulation.COLOR_RED)
            self.screen.blit(text_surface, (self.screen_width-150, text_y))
            text_y += 15
            text_surface = self.FONT.render(
                f"Boids : {self.boids}", True, Stimulation.COLOR_RED)
            self.screen.blit(text_surface, (self.screen_width-150, text_y))
            text_y += 15

            self.flock()

            # if clock.get_fps() > 60 : flock_stimulation.addBoid()

            pygame.display.update()
            if self.FPS:
                self.clock.tick(self.FPS)
            else:
                self.clock.tick()

        pygame.quit()


def main():

    Stimulation(100).stimulate()

if __name__ == '__main__':
    import cProfile
    cProfile.run('main()', 'output.dat')

    import pstats
    from pstats import SortKey

    with open('output_time.txt', 'w') as f:
        p = pstats.Stats('output.dat', stream=f)
        p.sort_stats('time').print_stats()
    with open('output_calls.txt', 'w') as f:
        p = pstats.Stats('output.dat', stream=f)
        p.sort_stats('calls').print_stats()
