import os
import pygame
import numpy as np
import numba
from numba import njit

NUM_BOIDS = 100
SCREEN_HEIGHT = 700
SCREEN_WIDTH = 1200

ALIGN_RADIUS = 100
ALIGN_MAX_FORCE = 0.2
ALIGN_MAX_SPEED = 4.0

COHESION_RADIUS = 100
COHESION_MAX_FORCE = 0.2
COHESION_MAX_SPEED = 4.0

SEPERATION_RADIUS = 50
SEPERATION_MAX_FORCE = 0.5
SEPERATION_MAX_SPEED = 4.0

@njit
def norm(array: np.ndarray):
    return np.sqrt(np.sum(array**2))

@njit
def setMagnitude(array, val: float):
    for i in range(array.shape[0]):
        if np.any(array[i, :]):
            array[i, :] /= norm(array[i, :])
            array[i, :] *= val
    return array

@njit
def update(boids: np.ndarray):
    boids[1, :, :] += boids[2, :, :]  # velocity update
    boids[0, :, :] += boids[1, :, :]  # position update
    for i in range(boids.shape[1]):
        if boids[0, i, 0] < 0:
            boids[0, i, 0] += SCREEN_WIDTH
        elif boids[0, i, 0] > SCREEN_WIDTH:
            boids[0, i, 0] -= SCREEN_WIDTH
        if boids[0, i, 1] < 0:
            boids[0, i, 1] += SCREEN_HEIGHT
        elif boids[0, i, 1] > SCREEN_HEIGHT:
            boids[0, i, 1] -= SCREEN_HEIGHT

    boids[2, :, :].fill(0)  # zero the acceleration
    boids[1, :, :] = setMagnitude(
        boids[1, :, :], ALIGN_MAX_SPEED)  # limit the velocity
    return boids

@njit
def flock(boids):
    for i in range(boids.shape[1]):

        align_count = 0
        align_steering = np.array([[0.0, 0.0]])

        cohesion_steering = np.array([[0.0, 0.0]])
        cohesion_count = 0

        seperation_steering = np.array([[0.0, 0.0]])
        seperation_count = 0

        for j in range(boids.shape[1]):
            if not i == j:
                if norm(boids[0, i, :]-boids[0, j, :]) < ALIGN_RADIUS:
                    align_count += 1
                    align_steering += boids[1, j, :]
                if norm(boids[0, i, :]-boids[0, j, :]) < COHESION_RADIUS:
                    cohesion_count += 1
                    cohesion_steering += boids[0, j, :]
                if norm(boids[0, i, :]-boids[0, j, :]) < SEPERATION_RADIUS:
                    seperation_count += 1
                    seperation_steering+=boids[0, i, :]-boids[0, j, :]
                    pass

        if align_count:
            align_steering /= align_count
        align_steering = align_steering - boids[1, i, :]
        align_steering = setMagnitude(align_steering, ALIGN_MAX_SPEED)
        if(norm(align_steering) > ALIGN_MAX_FORCE):
            align_steering = setMagnitude(align_steering, ALIGN_MAX_FORCE)

        if cohesion_count : cohesion_steering /= cohesion_count
        cohesion_steering = cohesion_steering - boids[0,i,:]
        cohesion_steering = setMagnitude(cohesion_steering, COHESION_MAX_SPEED)
        cohesion_steering = cohesion_steering - boids[1,i,:]
        if(norm(cohesion_steering) > COHESION_MAX_FORCE) :
            cohesion_steering = setMagnitude(cohesion_steering, COHESION_MAX_FORCE)

        if seperation_count : seperation_steering /= seperation_count
        seperation_steering = setMagnitude(seperation_steering, SEPERATION_MAX_SPEED)
        seperation_steering = seperation_steering - boids[1, i, :]
        if(norm(seperation_steering) > SEPERATION_MAX_FORCE):
            seperation_steering = setMagnitude(seperation_steering, SEPERATION_MAX_FORCE)

        boids[2, i, :] = align_steering+cohesion_steering+seperation_steering

    boids = update(boids)
    return boids


Boids = np.stack([np.random.uniform(0, SCREEN_WIDTH, size=(NUM_BOIDS, 2)),  # Boids position
                  # Boids velocity
                  np.random.uniform(-0.5, 0.5, size=(NUM_BOIDS, 2)),
                  np.zeros(shape=(NUM_BOIDS, 2), dtype=np.float32)])  # Boids acceleration
# making velocity a unity vector
Boids[1, :, :] = setMagnitude(Boids[1, :, :], 1)

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

    for i in range(Boids.shape[1]):
        pygame.draw.circle(screen, (255, 255, 255), Boids[0, i, :], 3+1)
        pygame.draw.circle(screen, (0, 255, 0), Boids[0, i, :], 3)

    text_y = 10
    text_surface = FONT.render(
        f"FPS : {int(clock.get_fps())}", True, color_red)
    screen.blit(text_surface, (SCREEN_WIDTH-150, text_y))
    text_y += 15

    Boids = flock(Boids)

    pygame.display.update()
    if FPS:
        clock.tick(FPS)
    else:
        clock.tick()

pygame.quit()
