import os
import pygame
import numpy as np

NUM_BOIDS = 300
SCREEN_HEIGHT = 700
SCREEN_WIDTH = 1200

ALIGN_RADIUS = 100
ALIGN_MAX_FORCE = 0.3
ALIGN_MAX_SPEED = 4.0

COHESION_RADIUS = 100
COHESION_MAX_FORCE = 0.3
COHESION_MAX_SPEED = 4.0

SEPARATION_RADIUS = 50
SEPARATION_MAX_FORCE = 10.0
SEPARATION_MAX_SPEED = 4.0

def setMagnitude(array: np.ndarray, val: float):
    magnitude = np.linalg.norm(array, axis=1)[:, np.newaxis]
    array = np.divide(array, magnitude, where=(magnitude != 0))
    return array * val

def update(boids_pos, boids_vel, boids_acc):

    boids_vel += boids_acc  # velocity update
    boids_pos += boids_vel  # position update

    # Trick : division by negative numbers
    # http://python-history.blogspot.com/2010/08/why-pythons-integer-division-floors.html
    boids_pos[:, 0] %= SCREEN_WIDTH
    boids_pos[:, 1] %= SCREEN_HEIGHT

    boids_acc = 0  # zero the acceleration
    # allow boids to move with max velocity in the desired direction
    boids_vel = setMagnitude(boids_vel, ALIGN_MAX_SPEED)

    return boids_pos, boids_vel, boids_acc

Boids_pos = np.random.uniform(
    0, SCREEN_WIDTH, size=(NUM_BOIDS, 2))  # Boids position
Boids_vel = np.random.uniform(-0.5, 0.5, size=(NUM_BOIDS, 2))  # Boids velocity
Boids_acc = np.zeros(shape=(NUM_BOIDS, 2),
                     dtype=np.float32)  # Boids acceleration
Boids_vel = setMagnitude(Boids_vel, 1)


def flock(boids_pos: np.ndarray, boids_vel: np.ndarray, boids_acc: np.ndarray):

    orig_boids_pos = boids_pos
    transpose_boid_pos = boids_pos
    transpose_boid_pos = np.transpose(transpose_boid_pos)
    reshape_boids_pos = boids_pos.reshape((NUM_BOIDS, 2, 1))
    np.broadcast(transpose_boid_pos, reshape_boids_pos)
    masked_boids_dist = transpose_boid_pos-reshape_boids_pos
    distance_boids = np.square(transpose_boid_pos-reshape_boids_pos)
    distance_boids = np.transpose(np.sqrt(np.sum(distance_boids, axis=1)))

    mask_array = np.full((NUM_BOIDS, NUM_BOIDS), True, dtype=bool)
    np.fill_diagonal(mask_array, False)

    align_check = distance_boids < ALIGN_RADIUS
    cohesion_check = distance_boids < COHESION_RADIUS
    separation_check = distance_boids < SEPARATION_RADIUS

    align_check = np.logical_and(align_check, mask_array)
    cohesion_check = np.logical_and(cohesion_check, mask_array)
    separation_check = np.logical_and(separation_check, mask_array)
    separation_check = np.transpose(separation_check)

    align_count = np.count_nonzero(align_check, axis=0)
    cohesion_count = np.count_nonzero(cohesion_check, axis=0)
    separation_count = np.count_nonzero(separation_check, axis=0)

    reshape_boids_vel = boids_vel.reshape((NUM_BOIDS, 2, 1))

    align_check = align_check.reshape((NUM_BOIDS, NUM_BOIDS, 1))
    cohesion_check = cohesion_check.reshape((NUM_BOIDS, NUM_BOIDS, 1))
    separation_check = separation_check.reshape((NUM_BOIDS, 1, NUM_BOIDS))

    np.broadcast(align_check, boids_vel)
    masked_boids_vel = boids_vel*align_check
    align_steering = np.sum(masked_boids_vel, axis=1)

    np.broadcast(cohesion_check, orig_boids_pos)
    masked_boids_pos = orig_boids_pos*cohesion_check
    cohesion_steering = np.sum(masked_boids_pos, axis=1)

    np.broadcast(separation_check, masked_boids_dist)
    separation_steering = np.sum(masked_boids_dist*separation_check, axis=2)

    align_count[align_count == 0] = 1
    cohesion_count[cohesion_count == 0] = 1
    separation_count[separation_count == 0] = 1

    align_steering = (np.transpose(align_steering)/align_count).T
    cohesion_steering = (np.transpose(cohesion_steering)/cohesion_count).T
    separation_steering = (np.transpose(
        separation_steering)/separation_count).T

    align_steering -= boids_vel
    align_steering = setMagnitude(align_steering, ALIGN_MAX_SPEED)
    if(np.linalg.norm(align_steering) > ALIGN_MAX_FORCE):
        align_steering = setMagnitude(align_steering, ALIGN_MAX_FORCE)

    cohesion_steering -= boids_pos
    cohesion_steering = setMagnitude(cohesion_steering, COHESION_MAX_SPEED)
    cohesion_steering -= boids_vel
    if(np.linalg.norm(cohesion_steering) > COHESION_MAX_FORCE):
        cohesion_steering = setMagnitude(cohesion_steering, COHESION_MAX_FORCE)

    separation_steering = setMagnitude(
        separation_steering, SEPARATION_MAX_SPEED)
    separation_steering -= boids_vel
    if(np.linalg.norm(separation_steering) > SEPARATION_MAX_FORCE):
        separation_steering = setMagnitude(
            separation_steering, SEPARATION_MAX_FORCE)

    boids_acc = align_steering + cohesion_steering - separation_steering
    boids_pos, boids_vel, boids_acc = update(boids_pos, boids_vel, boids_acc)

    return boids_pos, boids_vel, boids_acc

# adding boids
#-----------------------------------------------


# supressing the pygame hello message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

pygame.init()
FPS = 60
FONT = pygame.font.SysFont('ComicNeue-Regular.ttf', 20)
pygame.display.set_caption("flock simulation")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
color_red = (241, 38, 11)
color_green = (124, 252, 0)
exit = False

while not exit:
    # keyboard events
    for event in pygame.event.get():
        #closing pygame window
        if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_q):
            exit = True

    # screen movement
    pressed = pygame.key.get_pressed()

    # rendering
    screen.fill((0, 0, 0))

    for i in range(Boids_pos.shape[0]):
        pygame.draw.circle(screen, (255, 255, 255), Boids_pos[i, :], 3+1)
        pygame.draw.circle(screen, (0, 255, 0), Boids_pos[i, :], 3)

    text_y = 10
    text_surface = FONT.render(
        f"FPS : {int(clock.get_fps())}", True, color_red)
    screen.blit(text_surface, (SCREEN_WIDTH-150, text_y))
    text_y += 15

    Boids_pos, Boids_vel, Boids_acc = flock(Boids_pos, Boids_vel, Boids_acc)

    pygame.display.update()
    if FPS:
        clock.tick(FPS)
    else:
        clock.tick()

pygame.quit()
