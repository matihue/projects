import random

class Plant:
    def __init__(self, plant_type, number, world):
        self.type = 'plant'
        self.plant_type = plant_type
        self.world = world
        self.settings = self.world.settings
        self.number = number
        self.preset = self.settings.presets[self.plant_type]

        self.x = random.randint(1, self.world.width)
        self.y = random.randint(1, self.world.height)
        self.chunk_x = self.x // self.settings.chunk_size
        self.chunk_y = self.y // self.settings.chunk_size

        self.size = random.randint(*self.preset['size'])
        self.energy_stored = random.randint(*self.preset['energy_stored'])
        self.life_cost = self.preset['life_cost']
        self.color = self.preset['color']

        self.eaten = False
        
    def update(self):
        self.energy_stored -= self.life_cost
        
        if self.energy_stored <= 0:    
            self.eaten = True