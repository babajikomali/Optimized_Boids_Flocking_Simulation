import importlib
from BoidsFlock import BoidsFlock
from Rectangle import Rectangle
from QuadTree import QuadTree
from Point import Point
import pygame

class Simulation(BoidsFlock):

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

    def simulate(self):

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
                f"FPS : {int(self.clock.get_fps())}", True, Simulation.COLOR_RED)
            self.screen.blit(text_surface, (self.screen_width-150, text_y))
            text_y += 15
            text_surface = self.FONT.render(
                f"Boids : {self.boids}", True, Simulation.COLOR_RED)
            self.screen.blit(text_surface, (self.screen_width-150, text_y))
            text_y += 15

            self.hashflock()

            # if clock.get_fps() > 60 : flock_stimulation.addBoid()

            pygame.display.update()
            if self.FPS:
                self.clock.tick(self.FPS)
            else:
                self.clock.tick()

        pygame.quit()
