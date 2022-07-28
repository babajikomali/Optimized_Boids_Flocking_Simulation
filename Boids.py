import numpy as np
import pygame

# supressing the pygame hello message
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'


class BoidsFlock:

    ALIGN_RADIUS = 50
    ALIGN_MAX_FORCE = 0.2
    ALIGN_MAX_SPEED = 4.0

    COHESION_RADIUS = 50
    COHESION_MAX_FORCE = 0.2
    COHESION_MAX_SPEED = 4.0

    SEPARATION_RADIUS = 40
    SEPARATION_MAX_FORCE = 0.15
    SEPARATION_MAX_SPEED = 3.0

    def __init__(self,num_boids:int = 10, screen_width:int = 1200, screen_height:int = 700) -> None:

        self.boids = num_boids
        self.screen_height = screen_height
        self.screen_width = screen_width

        # adding boids
        self.boids_pos = np.random.uniform(0,max(screen_width,screen_height),size=(num_boids,2)) # Boids position
        self.boids_vel = np.random.uniform(-0.5,0.5,size=(num_boids,2)) # Boids velocity
        self.boids_acc = np.zeros(shape=(num_boids,2),dtype=np.float32) # Boids acceleration
        self.boids_vel = BoidsFlock.setMagnitude(self.boids_vel, 1)

    @staticmethod
    def setMagnitude(array:np.ndarray, val:float):
        magnitude = np.linalg.norm(array, axis=1)[:,np.newaxis]
        array = np.divide(array, magnitude, where=(magnitude!=0))
        return array * val

    def __update(self):

        self.boids_vel += self.boids_acc# velocity update
        self.boids_pos += self.boids_vel# position update

        # Trick : division by negative numbers
        # http://python-history.blogspot.com/2010/08/why-pythons-integer-division-floors.html
        self.boids_pos[:,0] %= self.screen_width
        self.boids_pos[:,1] %= self.screen_height
        
        self.boids_acc.fill(0) # zero the acceleration
        self.boids_vel = BoidsFlock.setMagnitude(self.boids_vel, BoidsFlock.ALIGN_MAX_SPEED) # allow boids to move with max velocity in the desired direction

    def flock(self):

        transpose_boid_pos = np.transpose(self.boids_pos)
        reshape_boids_pos = self.boids_pos.reshape((self.boids,2,1))
        np.broadcast(transpose_boid_pos,reshape_boids_pos)
        masked_boids_dist = transpose_boid_pos-reshape_boids_pos
        distance_boids = np.square(transpose_boid_pos-reshape_boids_pos)
        distance_boids = np.transpose(np.sqrt(np.sum(distance_boids,axis=1)))

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

        align_check = align_check.reshape((self.boids,self.boids,1))
        cohesion_check = cohesion_check.reshape((self.boids,self.boids,1))
        separation_check = separation_check.reshape((self.boids,1,self.boids))

        np.broadcast(align_check, self.boids_vel)
        masked_boids_vel = self.boids_vel*align_check
        align_steering = np.sum(masked_boids_vel, axis=1)

        np.broadcast(cohesion_check, self.boids_pos)
        masked_boids_pos = self.boids_pos*cohesion_check
        cohesion_steering = np.sum(masked_boids_pos, axis=1)
        
        np.broadcast(separation_check,masked_boids_dist)
        separation_steering = np.sum(masked_boids_dist*separation_check, axis=2)

        align_count[align_count==0] = 1
        cohesion_count[cohesion_count==0] = 1
        separation_count[separation_count==0] = 1
        
        align_steering = (np.transpose(align_steering)/align_count).T
        cohesion_steering = (np.transpose(cohesion_steering)/cohesion_count).T
        separation_steering = (np.transpose(separation_steering)/separation_count).T
        
        align_steering -= self.boids_vel
        align_steering = BoidsFlock.setMagnitude(align_steering, BoidsFlock.ALIGN_MAX_SPEED)
        if(np.linalg.norm(align_steering) > BoidsFlock.ALIGN_MAX_FORCE) :
            align_steering = BoidsFlock.setMagnitude(align_steering, BoidsFlock.ALIGN_MAX_FORCE)

        cohesion_steering -= self.boids_pos
        cohesion_steering = BoidsFlock.setMagnitude(cohesion_steering, BoidsFlock.COHESION_MAX_SPEED)
        cohesion_steering -= self.boids_vel
        if(np.linalg.norm(cohesion_steering) > BoidsFlock.COHESION_MAX_FORCE) :
            cohesion_steering = BoidsFlock.setMagnitude(cohesion_steering, BoidsFlock.COHESION_MAX_FORCE)
        
        separation_steering = BoidsFlock.setMagnitude(separation_steering, BoidsFlock.SEPARATION_MAX_SPEED)
        separation_steering -= self.boids_vel
        if(np.linalg.norm(separation_steering) > BoidsFlock.SEPARATION_MAX_FORCE) :
            separation_steering = BoidsFlock.setMagnitude(separation_steering, BoidsFlock.SEPARATION_MAX_FORCE)

        self.boids_acc = align_steering + cohesion_steering - separation_steering
        
        self.__update()
    
    def addBoid(self, num:int = 1):

        self.boids += num

        # generating boids
        boids_pos = np.random.uniform(0,max(self.screen_width,self.screen_height),size=(num,2)) # Boids position
        boids_vel = np.random.uniform(-0.5,0.5,size=(num,2)) # Boids velocity
        boids_vel = BoidsFlock.setMagnitude(boids_vel, 1)

        # adding boids
        self.boids_pos = np.vstack((self.boids_pos,boids_pos))
        self.boids_vel = np.vstack((self.boids_vel,boids_vel))

    def reset(self):

        self.boids_pos = np.random.uniform(0,max(self.screen_width,self.screen_height),size=(self.boids,2)) # Boids position
        self.boids_vel = np.random.uniform(-0.5,0.5,size=(self.boids,2)) # Boids velocity


class Stimulation(BoidsFlock):

    COLOR_RED = (241, 38, 11)
    COLOR_GREEN = (124, 252, 0)

    def __init__(self, num_boids: int = 10, screen_width: int = 1200, screen_height: int = 700) -> None:
        super().__init__(num_boids, screen_width, screen_height)

        pygame.init()
        pygame.display.set_caption("flock simulation")
        self.FONT = pygame.font.SysFont('ComicNeue-Regular.ttf',18)

        self.FPS = 60
        self.screen = pygame.display.set_mode((self.screen_width,self.screen_height))
        self.clock = pygame.time.Clock()
        self.exit = False

    def stimulate(self):

        while not self.exit:
            # keyboard events
            for event in pygame.event.get():
                #closing pygame window
                if event.type == pygame.QUIT :
                    self.exit = True
                
                elif event.type == pygame.KEYUP :
                    if event.key == pygame.K_q : self.exit = True
                    elif event.key == pygame.K_r : self.reset()


            # # screen movement
            # pressed = pygame.key.get_pressed()
                    
            # rendering
            self.screen.fill((0, 0, 0))

            for i in range(self.boids_pos.shape[0]):
                pygame.draw.circle(self.screen, (255, 255, 255), self.boids_pos[i,:], 3+1)
                pygame.draw.circle(self.screen, (0,255,0), self.boids_pos[i,:], 3)

            text_y = 10
            text_surface = self.FONT.render(f"FPS : {int(self.clock.get_fps())}",True,Stimulation.COLOR_RED)
            self.screen.blit(text_surface,(self.screen_width-150, text_y))
            text_y += 15
            text_surface = self.FONT.render(f"Boids : {self.boids}",True,Stimulation.COLOR_RED)
            self.screen.blit(text_surface,(self.screen_width-150, text_y))
            text_y += 15

            self.flock()

            # if clock.get_fps() > 60 : flock_stimulation.addBoid()

            pygame.display.update()
            if self.FPS: self.clock.tick(self.FPS)
            else : self.clock.tick()

        pygame.quit()

def main():

    Stimulation(100).stimulate()

if __name__ == '__main__':
    main()