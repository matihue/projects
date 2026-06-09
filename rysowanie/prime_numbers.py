import pygame
pygame.init()


class Sett:
    def __init__(self):
        self.screen = pygame.display.set_mode((1000, 800))
        self.clock = pygame.time.Clock()
        self.r = True
        self.background_color = (0,0,0)
      
        self.primes = set()     
        num = 100000  

        for i in range(2,num):
            is_prime = True
            for p in range(2, int(i**0.5)+1):
                if i % p == 0:
                    is_prime = False
                    break
            if is_prime:
                self.primes.add(i)
            
                
class Draw:
    def __init__(self, sett):
        self.x = 500
        self.y = 100
        self.sett = sett
        
        self.positions = ['up', 'right', 'down', 'left']
        self.pos_index = 0
        
        self.pos_x = 0
        self.pos_y = 0
        
        self.num = 0
        
        self.camera_x = 0
        self.camera_y = 0
        
        self.points = [(self.x, self.y)]
        
    def update(self):
        self.num += 1
        if self.num in self.sett.primes:
            if self.pos_index == 3:
                self.pos_index = 0
            else:
                self.pos_index += 1
            
        if self.positions[self.pos_index] == 'up':
            self.pos_y = -1
            self.pos_x = 0
        elif self.positions[self.pos_index] == 'right':
            self.pos_x = 1
            self.pos_y = 0
        elif self.positions[self.pos_index] == 'down':
            self.pos_y = 1
            self.pos_x = 0
        elif self.positions[self.pos_index] == 'left':
            self.pos_x = -1
            self.pos_y = 0
       
        self.x += self.pos_x
        self.y += self.pos_y
        
        self.points.append((self.x, self.y))
        
    def draw(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.camera_y -= 2
        if keys[pygame.K_s]:
            self.camera_y += 2
        if keys[pygame.K_a]:
            self.camera_x -= 2
        if keys[pygame.K_d]:
            self.camera_x += 2
        
        moved_points = []
        
        for x, y in self.points:
            moved_points.append((x-self.camera_x, y-self.camera_y))        
        
        if len(moved_points) > 1:  
            pygame.draw.lines(self.sett.screen, (255,255,255), False, moved_points, 1)
        
        
        
        
      
sett = Sett()
        
draw = Draw(sett=sett)
        
while sett.r:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sett.r = False
                
    draw.update()
    
    sett.screen.fill(sett.background_color)
        
    draw.draw() 
                
    pygame.display.flip()
    sett.clock.tick(1000)

        
        