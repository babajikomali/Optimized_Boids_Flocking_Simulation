import numpy as np
from QuadTree import QuadTree
from Point import Point
from Circle import Circle
from Rectangle import Rectangle
from SpatialHash import SpatialHash

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
