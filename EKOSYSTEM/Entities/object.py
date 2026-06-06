import random

class Object:

    def __init__(self, object_type, number, world):
        self.type = 'object'
        self.object_type = object_type
        self.world = world
        self.settings = self.world.settings
        self.preset = self.settings.presets[self.object_type]

        self.number = number

        self.x = random.randint(1, self.world.width)
        self.y = random.randint(1, self.world.height)
        self.chunk_x = self.x // self.settings.chunk_size
        self.chunk_y = self.y // self.settings.chunk_size
        
        self.color = self.preset['color']
        self.size = random.randint(1, 4)

        self.eaten = False