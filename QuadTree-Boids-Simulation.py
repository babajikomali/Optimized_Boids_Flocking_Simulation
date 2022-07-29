import os
import sys
import math
import pygame
import numpy as np

# supressing the pygame hello message

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

class Point:
    def __init__(self, x: float = 0, y: float = 0, idx: int =0) -> None:
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
        return math.sqrt(diff_x**2 + diff_y**2) <= self.r

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
    def __init__(self, rect: Rectangle, capacity: int = 0) -> None:
        self.rect = rect
        self.capacity = capacity
        self.points = []
        self.isDivided = False

    def subdivide(self) -> None:
        x, y, w, h = self.rect.x, self.rect.y, self.rect.w, self.rect.h
        ne = Rectangle(x+w/2, y+h/2, w/2, h/2)
        nw = Rectangle(x-w/2, y+h/2, w/2, h/2)
        se = Rectangle(x+w/2, y-h/2, w/2, h/2)
        sw = Rectangle(x-w/2, y-h/2, w/2, h/2)
        self.northeast = QuadTree(ne, self.capacity)
        self.northwest = QuadTree(nw, self.capacity)
        self.southeast = QuadTree(se, self.capacity)
        self.southwest = QuadTree(sw, self.capacity)
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
                if circle.isContain(x) and x.idx!=circle.idx:
                    found.append(x.idx+1)
            if self.isDivided:
                found.extend(self.northeast.query(circle))
                found.extend(self.northwest.query(circle))
                found.extend(self.southeast.query(circle))
                found.extend(self.southwest.query(circle))
            return found

class BoidsFlock:

    ALIGN_RADIUS = 100
    ALIGN_MAX_FORCE = 0.4
    ALIGN_MAX_SPEED = 4.0

    COHESION_RADIUS = 50
    COHESION_MAX_FORCE = 0.2
    COHESION_MAX_SPEED = 4.0

    SEPARATION_RADIUS = 50
    SEPARATION_MAX_FORCE = 10.0
    SEPARATION_MAX_SPEED = 3.0

    def __init__(self, num_boids: int = 10, screen_width: int = 1200, screen_height: int = 700) -> None:

        self.boids = num_boids
        self.screen_height = screen_height
        self.screen_width = screen_width

        # adding boids
        self.boids_pos = np.random.uniform(
            0, max(screen_width, screen_height), size=(num_boids, 2))  # Boids position
        # Boids velocity
        self.boids_vel = np.random.uniform(-0.5, 0.5, size=(num_boids, 2))
        self.boids_acc = np.zeros(
            shape=(num_boids, 2), dtype=np.float32)  # Boids acceleration
        self.boids_vel = BoidsFlock.setMagnitude(self.boids_vel, 1)

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

    def __flock(self):
        rootQuadTree = QuadTree(Rectangle(self.screen_width/2, self.screen_height/2, 
                                          self.screen_width/2, self.screen_height/2), 4)
        
        for i in range(self.boids):
            point = Point(self.boids_pos[i][0], self.boids_pos[i][1], i)
            rootQuadTree.insertPoint(point)

        align_indices = []
        cohesion_indices = []
        separation_indices = []

        for i,pos in enumerate(self.boids_pos):
            align_circle = Circle(pos[0],pos[1],BoidsFlock.ALIGN_RADIUS,i)
            cohesion_circle = Circle(pos[0],pos[1],BoidsFlock.COHESION_RADIUS,i)
            separation_circle = Circle(pos[0],pos[1],BoidsFlock.SEPARATION_RADIUS,i)

            align_nearby = rootQuadTree.query(align_circle)
            cohesion_nearby = rootQuadTree.query(cohesion_circle)
            separation_nearby = rootQuadTree.query(separation_circle)

            align_indices.append(align_nearby)
            cohesion_indices.append(cohesion_nearby)
            separation_indices.append(separation_nearby)

        # align_idx = np.take(self.boids_pos, separation_nearby, axis = 0)
        # print(align_indices)
        # sys.exit()
        align_idx = np.zeros([len(align_indices),len(max(align_indices,key = lambda x: len(x)))])
        for i,j in enumerate(align_indices):align_idx[i][0:len(j)] = j
        cohesion_idx = np.zeros([len(cohesion_indices),len(max(cohesion_indices,key = lambda x: len(x)))])
        for i,j in enumerate(cohesion_indices):cohesion_idx[i][0:len(j)] = j
        separation_idx = np.zeros([len(separation_indices),len(max(separation_indices,key = lambda x: len(x)))])
        for i,j in enumerate(separation_indices):separation_idx[i][0:len(j)] = j

        return np.array(align_idx),np.array(cohesion_idx),np.array(separation_idx)

    def newflock(self):

        align_idx,cohesion_idx,separation_idx = self.__flock()

        intalign_idx = align_idx.astype(int)
        intcohesion_idx = cohesion_idx.astype(int)
        intseparation_idx = separation_idx.astype(int)

        boids_pos = np.insert(self.boids_pos, [0], [0.0], axis=0)
        boids_vel = np.insert(self.boids_vel, [0], [0.0], axis=0)

        align_vel = boids_vel[intalign_idx]
        cohesion_pos = boids_pos[intcohesion_idx]
        separation_pos = boids_pos[intseparation_idx]

        align_steering = np.sum(align_vel,axis=1)
        cohesion_steering = np.sum(cohesion_pos,axis=1)
        separation_steering = np.sum(separation_pos,axis=1)

        separation_count = np.count_nonzero(separation_idx, axis=1)
        separation_count = np.transpose(separation_count)[:, np.newaxis]

        sep_boids_pos = self.boids_pos
        np.broadcast(separation_count,sep_boids_pos)
        separation_steering -= (separation_count*sep_boids_pos)

        align_steering /= np.count_nonzero(align_idx)
        cohesion_steering /= np.count_nonzero(cohesion_idx)
        separation_steering /= np.count_nonzero(separation_idx)
        
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




        # for i,pos in enumerate(self.boids_pos):
        #     align_circle = Circle(pos[0],pos[1],BoidsFlock.ALIGN_RADIUS)
        #     cohesion_circle = Circle(pos[0],pos[1],BoidsFlock.COHESION_RADIUS)
        #     separation_circle = Circle(pos[0],pos[1],BoidsFlock.SEPARATION_RADIUS)

        #     align_nearby = np.setdiff1d(np.array(rootQuadTree.query(align_circle)),np.array([i]))
        #     cohesion_nearby = np.setdiff1d(np.array(rootQuadTree.query(cohesion_circle)),np.array([i]))
        #     separation_nearby = np.setdiff1d(np.array(rootQuadTree.query(separation_circle)),np.array([i]))

        #     align_vel = np.copy(self.boids_vel)
        #     if len(align_nearby): align_vel = np.delete(align_vel,align_nearby,0)

        #     cohesion_pos = np.copy(self.boids_pos)
        #     if len(cohesion_nearby): cohesion_pos = np.delete(cohesion_pos,cohesion_nearby,0)

        #     separation_pos = np.copy(self.boids_pos)
        #     if len(separation_nearby): separation_pos = np.delete(separation_pos,separation_nearby,0)
        #     boid_pos = self.boids_pos[i,:]
        #     np.broadcast(boid_pos,separation_pos)
        #     separation_pos = boid_pos-separation_pos
            
        #     align_steering = np.sum(align_vel,axis=0)[:,np.newaxis].T
        #     cohesion_steering = np.sum(cohesion_pos,axis=0)[:,np.newaxis].T
        #     separation_steering = np.sum(separation_pos,axis=0)[:,np.newaxis].T

        #     if len(align_nearby): align_steering/=len(align_nearby)
        #     if len(cohesion_nearby): cohesion_steering/=len(cohesion_nearby)
        #     if len(separation_nearby): separation_steering/=len(separation_nearby)

        #     align_steering -= self.boids_vel[i,:]
        #     align_steering = BoidsFlock.setMagnitude(
        #         align_steering, BoidsFlock.ALIGN_MAX_SPEED)
        #     if(np.linalg.norm(align_steering) > BoidsFlock.ALIGN_MAX_FORCE):
        #         align_steering = BoidsFlock.setMagnitude(
        #             align_steering, BoidsFlock.ALIGN_MAX_FORCE)

        #     cohesion_steering -= self.boids_pos[i,:]
        #     cohesion_steering = BoidsFlock.setMagnitude(
        #         cohesion_steering, BoidsFlock.COHESION_MAX_SPEED)
        #     cohesion_steering -= self.boids_vel[i,:]
        #     if(np.linalg.norm(cohesion_steering) > BoidsFlock.COHESION_MAX_FORCE):
        #         cohesion_steering = BoidsFlock.setMagnitude(
        #             cohesion_steering, BoidsFlock.COHESION_MAX_FORCE)
            
        #     separation_steering = BoidsFlock.setMagnitude(
        #         separation_steering, BoidsFlock.SEPARATION_MAX_SPEED)
        #     separation_steering -= self.boids_vel[i,:]
        #     if(np.linalg.norm(separation_steering) > BoidsFlock.SEPARATION_MAX_FORCE):
        #         separation_steering = BoidsFlock.setMagnitude(
        #             separation_steering, BoidsFlock.SEPARATION_MAX_FORCE)

        #     self.boids_acc[i] = align_steering + cohesion_steering - separation_steering

        # self.__update()

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

            for i in range(self.boids_pos.shape[0]):
                pygame.draw.circle(self.screen, (255, 255, 255),
                                   self.boids_pos[i, :], 3+1)
                pygame.draw.circle(self.screen, (0, 255, 0),
                                   self.boids_pos[i, :], 3)

            text_y = 10
            text_surface = self.FONT.render(
                f"FPS : {int(self.clock.get_fps())}", True, Stimulation.COLOR_RED)
            self.screen.blit(text_surface, (self.screen_width-150, text_y))
            text_y += 15
            text_surface = self.FONT.render(
                f"Boids : {self.boids}", True, Stimulation.COLOR_RED)
            self.screen.blit(text_surface, (self.screen_width-150, text_y))
            text_y += 15

            self.newflock()

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
    main()
