import pygame
import numpy as np

NUM_BOIDS = 100
SCREEN_HEIGHT = 700
SCREEN_WIDTH = 1200

ALIGN_RADIUS = 100
ALIGN_MAX_FORCE = 0.2
ALIGN_MAX_SPEED = 4.0

COHESION_RADIUS = 100
COHESION_MAX_FORCE = 0.2
COHESION_MAX_SPEED = 4.0

SEPARATION_RADIUS = 40
SEPARATION_MAX_FORCE = 0.5
SEPARATION_MAX_SPEED = 4.0

def setMagnitude(array:np.ndarray, val:float):
    magnitude = np.linalg.norm(array, axis=1)[:,np.newaxis]
    array = np.divide(array, magnitude, where=(magnitude!=0))
    return array * val

def update(boids_pos, boids_vel, boids_acc):

    boids_vel += boids_acc# velocity update
    boids_pos += boids_vel# position update

    # Trick : division by negative numbers
    # http://python-history.blogspot.com/2010/08/why-pythons-integer-division-floors.html
    boids_pos[:,0] %= SCREEN_WIDTH
    boids_pos[:,1] %= SCREEN_HEIGHT
    
    boids_acc = 0 # zero the acceleration
    boids_vel = setMagnitude(boids_vel, ALIGN_MAX_SPEED) # allow boids to move with max velocity in the desired direction


def _norm(array:np.ndarray) : return np.sqrt(np.sum(array**2))

def _setMagnitude(array, val:float) :
    for i in range(array.shape[0]) :
        if np.any(array[i,:]) :
            array[i,:] /= _norm(array[i,:])
            array[i,:] *= val
    return array

def _update(boids:np.ndarray) :
    boids[1,:,:] += boids[2,:,:] # velocity update
    boids[0,:,:] += boids[1,:,:] # position update
    for i in range(boids.shape[1]):
        if boids[0,i,0] < 0 : boids[0,i,0] += SCREEN_WIDTH
        elif boids[0,i,0] > SCREEN_WIDTH : boids[0,i,0] -= SCREEN_WIDTH
        if boids[0,i,1] < 0 : boids[0,i,1] += SCREEN_HEIGHT
        elif boids[0,i,1] > SCREEN_HEIGHT : boids[0,i,1] -= SCREEN_HEIGHT
    
    boids[2,:,:].fill(0) # zero the acceleration
    boids[1,:,:] = _setMagnitude(boids[1,:,:] , ALIGN_MAX_SPEED) # limit the velocity
    return boids

Boids = np.stack([np.random.uniform(0,SCREEN_WIDTH,size=(NUM_BOIDS,2)), # Boids position
                  np.random.uniform(-0.5,0.5,size=(NUM_BOIDS,2)), # Boids velocity
                  np.zeros(shape=(NUM_BOIDS,2),dtype=np.float32)]) # Boids acceleration
Boids[1,:,:] = setMagnitude(Boids[1,:,:], 1) # making velocity a unity vector

Boids_pos = Boids[0,:,:].copy()
Boids_vel = Boids[1,:,:].copy()
Boids_acc = Boids[2,:,:].copy()

def flock(boids_pos:np.ndarray, boids_vel:np.ndarray, boids_acc:np.ndarray):

    orig_boids_pos = boids_pos
    transpose_boid_pos = boids_pos
    transpose_boid_pos = np.transpose(transpose_boid_pos)
    reshape_boids_pos = boids_pos.reshape((NUM_BOIDS,2,1))
    np.broadcast(transpose_boid_pos,reshape_boids_pos)
    masked_boids_dist = transpose_boid_pos-reshape_boids_pos
    distance_boids = np.square(transpose_boid_pos-reshape_boids_pos)
    distance_boids = np.transpose(np.sqrt(np.sum(distance_boids,axis=1)))

    mask_array = np.full((NUM_BOIDS, NUM_BOIDS), True, dtype=bool)
    np.fill_diagonal(mask_array, False)

    align_check = distance_boids<ALIGN_RADIUS
    cohesion_check = distance_boids<COHESION_RADIUS
    separation_check = distance_boids<SEPARATION_RADIUS

    align_check = np.logical_and(align_check, mask_array)
    cohesion_check = np.logical_and(cohesion_check, mask_array)
    separation_check = np.logical_and(separation_check, mask_array)
    separation_check = np.transpose(separation_check)

    align_count = np.count_nonzero(align_check, axis=0)
    cohesion_count = np.count_nonzero(cohesion_check, axis=0)
    separation_count = np.count_nonzero(separation_check, axis=0)

    reshape_boids_vel = boids_vel.reshape((NUM_BOIDS, 2, 1))

    align_check = align_check.reshape((NUM_BOIDS,NUM_BOIDS,1))
    cohesion_check = cohesion_check.reshape((NUM_BOIDS,NUM_BOIDS,1))
    separation_check = separation_check.reshape((NUM_BOIDS,1,NUM_BOIDS))

    np.broadcast(align_check,boids_vel)
    masked_boids_vel = boids_vel*align_check
    align_steering = np.sum(masked_boids_vel, axis=1)

    np.broadcast(cohesion_check,orig_boids_pos)
    masked_boids_pos = orig_boids_pos*cohesion_check
    cohesion_steering = np.sum(masked_boids_pos, axis=1)
    
    np.broadcast(separation_check,masked_boids_dist)
    separation_steering = np.sum(masked_boids_dist*separation_check, axis=2)

    align_count[align_count==0] = 1
    cohesion_count[cohesion_count==0] = 1
    separation_count[separation_count==0] = 1
    
    align_steering = (np.transpose(align_steering)/align_count).T
    cohesion_steering = (np.transpose(cohesion_steering)/cohesion_count).T
    separation_steering = (np.transpose(separation_steering)/separation_count).T
    
    align_steering -= boids_vel
    align_steering = setMagnitude(align_steering, ALIGN_MAX_SPEED)
    if(np.linalg.norm(align_steering) > ALIGN_MAX_FORCE) :
        align_steering = setMagnitude(align_steering, ALIGN_MAX_FORCE)

    cohesion_steering -= boids_pos
    cohesion_steering = setMagnitude(cohesion_steering, COHESION_MAX_SPEED)
    cohesion_steering -= boids_vel
    if(np.linalg.norm(cohesion_steering) > COHESION_MAX_FORCE) :
        cohesion_steering = setMagnitude(cohesion_steering, COHESION_MAX_FORCE)
    
    separation_steering = setMagnitude(separation_steering, SEPARATION_MAX_SPEED)
    separation_steering -= boids_vel
    if(np.linalg.norm(separation_steering) > SEPARATION_MAX_FORCE) :
        separation_steering = setMagnitude(separation_steering, SEPARATION_MAX_FORCE)

    boids_acc = align_steering #+ cohesion_steering + separation_steering
    update(boids_pos, boids_vel, boids_acc)


def _flock(boids) :
    for i in range(boids.shape[1]):

        align_count = 0
        align_steering = np.array([[0.0, 0.0]])

        for j in range(boids.shape[1]):
            if not i==j :
                if _norm(boids[0,i,:]-boids[0,j,:]) < ALIGN_RADIUS :
                    align_count += 1
                    align_steering += boids[1,j,:]
        
        if align_count : align_steering /= align_count
        align_steering = align_steering - boids[1,i,:]
        align_steering = _setMagnitude(align_steering, ALIGN_MAX_SPEED)
        if(_norm(align_steering) > ALIGN_MAX_FORCE) :
            align_steering = _setMagnitude(align_steering, ALIGN_MAX_FORCE)

        boids[2,i,:] = align_steering

    boids = _update(boids)
    return boids

flock(Boids_pos, Boids_vel, Boids_acc)
_flock(Boids)

print(Boids[0,:,:] == Boids_pos)