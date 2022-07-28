import math
import pygame
import random

Width = 1300.0
Height = 750.0
MAX_SPEED = 6
NUM_BOIDS = 100

PARAMETERS = {'align_radius' : 100, 'cohesion_radius' :  100, 'separation_radius' : 40,
              'align_max_force' : 0.2, 'align_max_speed' : 4.0,'cohesion_max_force' : 0.2, 
              'cohesion_max_speed' : 4.0,'separation_max_force' : 0.5, 'separation_max_speed' : 4.0}

def getMagnitude(vector):
    x = vector[0]
    y = vector[1]
    return math.sqrt(x*x+y*y)

def normalize(vector):
    mag = getMagnitude(vector)
    if mag>0:
        vector[0] /= mag
        vector[1] /= mag

def setMagnitude(vector, mag):
    normalize(vector)
    vector[0] *= mag
    vector[1] *= mag

def update(boid):
    position, velocity, accelaration = boid

    position[0] += velocity[0]
    position[1] += velocity[1]

    if position[0]  < 0.0:
        position[0] += Width
    elif position[0] > Width:
        position[0] -= Width
    if position[1] < 0.0:
        position[1] += Height
    elif position[1] > Height:
        position[1] -= Height
    
    velocity[0] += accelaration[0]
    velocity[1] += accelaration[1]

    if getMagnitude(velocity) > MAX_SPEED :
        setMagnitude(velocity,MAX_SPEED)
    
    accelaration[0], accelaration[1] = 0.0, 0.0
        
def dist(vector1, vector2, radius):
    x = vector1[0]-vector2[0]
    y = vector1[1]-vector2[1]
    distance = math.sqrt(x*x+y*y)
    if distance < radius:
        return True
    return False

def subVector(vector1, vector2):
    x = vector1[0]-vector2[0]
    y = vector1[1]-vector2[1]
    return [x,y]

def flock(boids, index, align_radius, cohesion_radius, separation_radius,
          align_max_force, align_max_speed,
          cohesion_max_force, cohesion_max_speed,
          separation_max_force, separation_max_speed):
    
    align_steering = [0.0, 0.0]
    align_count = 0

    cohesion_steering = [0.0, 0.0]
    cohesion_count = 0

    separation_steering = [0.0, 0.0]
    separation_count = 0
    
    for i in range(NUM_BOIDS):
        if not i==index:
            # Alignment
            if dist(boids[index][0], boids[i][0], align_radius)==True:
                align_count += 1
                align_steering[0] += boids[i][1][0]
                align_steering[1] += boids[i][1][1]
            # Cohesion
            if dist(boids[index][0], boids[i][0], cohesion_radius)==True:
                cohesion_count += 1
                cohesion_steering[0] += boids[i][0][0]
                cohesion_steering[1] += boids[i][0][1]
            # Seperartion
            if dist(boids[index][0], boids[i][0], separation_radius)==True:
                diff = [0.0, 0.0]
                separation_count += 1
                diff[0] = boids[index][0][0] - boids[i][0][0]
                diff[1] = boids[index][0][1] - boids[i][0][1]
                if getMagnitude(diff) > 0 :
                    diff[0] /= getMagnitude(diff)
                    diff[1] /= getMagnitude(diff)
                separation_steering[0] += diff[0]
                separation_steering[1] += diff[1]
    
    if align_count > 0: 
        align_steering[0] /= align_count
        align_steering[1] /= align_count
    if cohesion_count > 0: 
        cohesion_steering[0] /= cohesion_count
        cohesion_steering[1] /= cohesion_count
    if separation_count > 0: 
        separation_steering[0] /= separation_count
        separation_steering[1] /= separation_count
    
    setMagnitude(align_steering, align_max_speed)
    align_steering = subVector(align_steering, boids[index][1])
    if(getMagnitude(align_steering) > align_max_force):
        setMagnitude(align_steering, align_max_force)
    
    cohesion_steering = subVector(cohesion_steering, boids[index][0])
    setMagnitude(cohesion_steering, cohesion_max_speed)
    cohesion_steering = subVector(cohesion_steering, boids[index][1])
    if(getMagnitude(cohesion_steering) > cohesion_max_force):
        setMagnitude(cohesion_steering, cohesion_max_force)
    
    setMagnitude(separation_steering, separation_max_speed)
    separation_steering = subVector(separation_steering, boids[index][1])
    if(getMagnitude(separation_steering) > separation_max_force):
        setMagnitude(separation_steering, separation_max_force)

    # return [align_steering[0] + cohesion_steering[0] + separation_steering[0],
    #         align_steering[1] + cohesion_steering[1] + separation_steering[1] ]
    return align_steering, cohesion_steering, separation_steering

def addBoid(boids):
    position = []
    velocity = []
    accelaration = []
    position = [random.uniform(0.0, Width), random.uniform(0.0, Height)]
    velocity = [random.random(), random.random()]
    setMagnitude(velocity, random.uniform(2.0, 4.0))
    accelaration = [0.0,0.0]
    setMagnitude(accelaration, random.uniform(2.0, 4.0))
    boid = [position, velocity, accelaration]
    boids.append(boid)

boids = []
for x in range(NUM_BOIDS):
    addBoid(boids)

def reset_boids():
    global boids
    boids = []
    for x in range(NUM_BOIDS):
        addBoid(boids)

#-----------------------------------------------

# supressing the pygame hello message
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

pygame.init()
FPS = None
FONT = pygame.font.SysFont('ComicNeue-Regular.ttf',20)
pygame.display.set_caption("flock simulation")
screen_width,screen_height = 1300,750
screen = pygame.display.set_mode((screen_width,screen_height))
clock = pygame.time.Clock()
color_red = (241, 38, 11)
color_green = (124, 252, 0)
circle_radius = 5
exit = False

align_select = False
separation_select = False
cohesion_select = False

while not exit:
    # keyboard events
    for event in pygame.event.get():
        #closing pygame window
        if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_q):
            exit = True

    # screen movement
    pressed = pygame.key.get_pressed()

    if event.type == pygame.KEYUP :
        if event.key == pygame.K_a :
            align_select = not align_select
            print('1')
        elif event.key == pygame.K_c :
            cohesion_select = not cohesion_select
            print('2')
        elif event.key == pygame.K_s :
            separation_select = not separation_select
            print('3')
        elif event.key == pygame.K_r :
            reset_boids()


    if pressed[pygame.K_UP] : 
        if align_select : 
            if pressed[pygame.K_r] : PARAMETERS['align_radius'] = min(PARAMETERS['align_radius'] + 1, 200)
            elif pressed[pygame.K_s] : PARAMETERS['align_max_speed'] = min(PARAMETERS['align_max_speed'] + 0.1, 5)
            elif pressed[pygame.K_f] : PARAMETERS['align_max_force'] = min(PARAMETERS['align_max_force'] + 0.1, 5)
        elif cohesion_select : 
            if pressed[pygame.K_r] : PARAMETERS['cohesion_radius'] = min(PARAMETERS['cohesion_radius'] + 1, 200)
            elif pressed[pygame.K_s] : PARAMETERS['cohesion_max_speed'] = min(PARAMETERS['cohesion_max_speed'] + 0.1, 5)
            elif pressed[pygame.K_f] : PARAMETERS['cohesion_max_force'] = min(PARAMETERS['cohesion_max_force'] + 0.1, 5)
        elif separation_select :
            if pressed[pygame.K_r] : PARAMETERS['separation_radius'] = min(PARAMETERS['separation_radius'] + 1, 200)
            elif pressed[pygame.K_s] : PARAMETERS['separation_max_speed'] = min(PARAMETERS['separation_max_speed'] + 0.1, 5)
            elif pressed[pygame.K_f] : PARAMETERS['separation_max_force'] = min(PARAMETERS['separation_max_force'] + 0.1, 5)
    
    if pressed[pygame.K_DOWN] : 
        if align_select : 
            if pressed[pygame.K_r] : PARAMETERS['align_radius'] = max(PARAMETERS['align_radius'] - 1, 0)
            elif pressed[pygame.K_s] : PARAMETERS['align_max_speed'] = max(PARAMETERS['align_max_speed'] - 0.1, 0)
            elif pressed[pygame.K_f] : PARAMETERS['align_max_force'] = max(PARAMETERS['align_max_force'] - 0.1, 0)
        elif cohesion_select :
            if pressed[pygame.K_r] : PARAMETERS['cohesion_radius'] = max(PARAMETERS['cohesion_radius'] - 1, 0)
            elif pressed[pygame.K_s] : PARAMETERS['cohesion_max_speed'] = max(PARAMETERS['cohesion_max_speed'] - 0.1, 0)
            elif pressed[pygame.K_f] : PARAMETERS['cohesion_max_force'] = max(PARAMETERS['cohesion_max_force'] - 0.1, 0)
        elif separation_select :
            if pressed[pygame.K_r] : PARAMETERS['separation_radius'] = max(PARAMETERS['separation_radius'] - 1, 0)
            elif pressed[pygame.K_s] : PARAMETERS['separation_max_speed'] = max(PARAMETERS['separation_max_speed'] - 0.1, 0)
            elif pressed[pygame.K_f] : PARAMETERS['separation_max_force'] = max(PARAMETERS['separation_max_force'] - 0.1, 0)

    # rendering
    screen.fill((0, 0, 0))

    for i,boid in enumerate(boids):
        
        align_steering, cohesion_steering, separation_steering = flock(boids,i,**PARAMETERS)
        # boids[i][2][0]=align_steering[0]
        # boids[i][2][1]=align_steering[1]
        # update(boid)
        # boids[i][2][0]=cohesion_steering[0]
        # boids[i][2][1]=cohesion_steering[1]
        # update(boid)
        # boids[i][2][0]=separation_steering[0]
        # boids[i][2][1]=separation_steering[1]
        # update(boid)
        boids[i][2][0]=separation_steering[0]+align_steering[0]+cohesion_steering[0]
        boids[i][2][1]=separation_steering[1]+align_steering[1]+cohesion_steering[1]
        update(boid)
        position = boid[0]
        pygame.draw.circle(screen, (255, 255, 255), position, circle_radius+1)
        pygame.draw.circle(screen, (0,255,0), position, circle_radius)
        
    text_y = 10
    text_surface = FONT.render(f"FPS : {int(clock.get_fps())}",True,color_red)
    screen.blit(text_surface,(screen_width-150, text_y))
    text_y += 15
    text_surface = FONT.render(f"boids : {len(boids)}",True,color_red)
    screen.blit(text_surface,(screen_width-150, text_y))
    text_y += 15

    text_color = color_green if align_select else color_red
    text_surface = FONT.render(f"Align Radius : {PARAMETERS['align_radius']}",True,text_color)
    screen.blit(text_surface,(screen_width-150,text_y)); text_y += 15
    text_surface = FONT.render(f"Align Speed : {PARAMETERS['align_max_speed']}",True,text_color)
    screen.blit(text_surface,(screen_width-150,text_y)); text_y += 15
    text_surface = FONT.render(f"Align Force : {PARAMETERS['align_max_force']}",True,text_color)
    screen.blit(text_surface,(screen_width-150,text_y)); text_y += 15
    
    text_color = color_green if cohesion_select else color_red
    text_surface = FONT.render(f"Cohesion Radius : {PARAMETERS['cohesion_radius']}",True,text_color)
    screen.blit(text_surface,(screen_width-150,text_y)); text_y += 15
    text_surface = FONT.render(f"Cohesion Speed : {PARAMETERS['cohesion_max_speed']}",True,text_color)
    screen.blit(text_surface,(screen_width-150,text_y)); text_y += 15
    text_surface = FONT.render(f"Cohesion Force : {PARAMETERS['cohesion_max_force']}",True,text_color)
    screen.blit(text_surface,(screen_width-150,text_y)); text_y += 15

    text_color = color_green if separation_select else color_red
    text_surface = FONT.render(f"Separation Radius : {PARAMETERS['separation_radius']}",True,text_color)
    screen.blit(text_surface,(screen_width-150,text_y)); text_y += 15
    text_surface = FONT.render(f"Separation Speed : {PARAMETERS['separation_max_speed']}",True,text_color)
    screen.blit(text_surface,(screen_width-150,text_y)); text_y += 15
    text_surface = FONT.render(f"Separation Force : {PARAMETERS['separation_max_force']}",True,text_color)
    screen.blit(text_surface,(screen_width-150,text_y)); text_y += 15

    pygame.display.flip()
    if FPS: clock.tick(FPS)
    else : clock.tick()

pygame.quit()