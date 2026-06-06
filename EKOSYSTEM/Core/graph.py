import pygame

class Graph:
    def __init__(self, settings):
        self.width = 500
        self.height = 300
        self.settings = settings
        self.roslinozerni_points = []
        self.miesozerni_points = []
        self.padlinozerni_points = []
        self.x = 50
        self.y = 750

    def draw(self):
        screen = self.settings.screen
        pygame.draw.polygon(screen, (0,0,0), [(0, 500), (500, 500), (500, 800), (0, 800)])
        pygame.draw.lines(screen, (255, 255, 255), False,[(50, 550), (50, 750)],2 )
        pygame.draw.lines(screen, (255, 255, 255), False,[(50, 750), (450, 750)],2 )
        
        if len(self.roslinozerni_points) > 2 and len(self.miesozerni_points) > 2 and len(self.padlinozerni_points) > 2:

            pygame.draw.lines(screen, (255, 0, 0), False, self.miesozerni_points, 2)
            pygame.draw.lines(screen, (0, 255, 0), False, self.roslinozerni_points, 2)
            pygame.draw.lines(screen, (0, 0, 255), False, self.padlinozerni_points, 2)