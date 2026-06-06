import pygame
pygame.init()

import time

from Entities.animal import Animal
from Entities.object import Object
from Entities.plant import Plant

from Core.settings import Settings
from Core.graph import Graph
import Core.helpers as helpers
            
class World:
    def __init__(self):
        self.settings = Settings()
        self.width = self.settings.world_width
        self.height = self.settings.world_height

        self.chunks = {}
        for x in range(self.width // self.settings.chunk_size + 1):
            for y in range(self.height // self.settings.chunk_size + 1):
                self.chunks[(x, y)] = {
                    'plant': {
                        'tree':[],
                        'grass':[]
                    },
                    'object': {
                        'rock': [],
                        'water': [],
                        'corpse': []
                    },
                    'animal': {
                        'miesozerne':[],
                        'roslinozerne':[],
                        'padlinozerne':[]
                    }
                }
                
        self.plant = []

        self.object = []

        self.animal = []
        
        self.graph = Graph(self.settings)

        self.miesozerni = []
        self.roslinozerni = []
        self.padlinozerni = []

    def render(self):
        for i in range(self.settings.trees):
            self.plant.append(Plant(plant_type='tree', number = i, world = self))

        for i in range(self.settings.grass):
            self.plant.append(Plant(plant_type='grass', number = i, world = self))

        for i in range(self.settings.water):
            self.object.append(Object(object_type='water', number = i, world = self))
            
        for i in range(self.settings.rocks):  
            self.object.append(Object(object_type='rock', number=i, world = self))

        for i in range(self.settings.miesozercy):
            self.animal.append(Animal(animal_type='miesozerne', number = i, world=self))
        for i in range(self.settings.roslinozercy):
            self.animal.append(Animal(animal_type='roslinozerne', number = i, world=self))
        for i in range(self.settings.padlinozercy):
            self.animal.append(Animal(animal_type='padlinozerne', number = i, world=self))

        for ani in self.animal:
            self.chunks[(ani.chunk_x, ani.chunk_y)]['animal'][ani.animal_type].append(ani)

        for obj in self.object:
            self.chunks[(obj.chunk_x, obj.chunk_y)]['object'][obj.object_type].append(obj)

        for plt in self.plant:
            self.chunks[(plt.chunk_x, plt.chunk_y)]['plant'][plt.plant_type].append(plt)
            
    def draw(self):
        for plt in self.plant:
            pygame.draw.circle(self.settings.screen, (plt.color), (int(plt.x), int(plt.y)), int(plt.size))
        for obj in self.object:
            pygame.draw.circle(self.settings.screen, (obj.color), (int(obj.x), int(obj.y)), int(obj.size))
        for ani in self.animal:
            pygame.draw.circle(self.settings.screen, (ani.color), (int(ani.x), int(ani.y)), int(ani.size))
    
    def get_near_chunks(self, cx, cy, vision, chunk_size):
        r = int(vision // chunk_size + 1)
        chunks = []

        for dx in range(-r, r+1):
            for dy in range(-r, r+1):
                key = (cx + dx, cy + dy)
                if key in self.chunks:
                    chunks.append(self.chunks[key])

        return chunks

    def update_world(self):
        eaten_plants = []
        new_children = []
        dead_animals = []

        for plant in self.plant:
            plant.update()        

            if plant.eaten == True:
                eaten_plants.append(plant)
                self.chunks[(plant.chunk_x, plant.chunk_y)][plant.type][plant.plant_type].remove(plant)

        for animal in self.animal:
            old_chunk = (animal.chunk_x, animal.chunk_y)
        
            animal.update()
            animal.ai()
        
            new_chunk = (
                int(animal.x) // animal.settings.chunk_size,
                int(animal.y) // animal.settings.chunk_size
            )
            
            if old_chunk != new_chunk:
                old_list = self.chunks[(old_chunk)][animal.type][animal.animal_type]
                if animal in old_list:
                    old_list.remove(animal)

                animal.chunk_x, animal.chunk_y = new_chunk

                self.chunks[(new_chunk)][animal.type][animal.animal_type].append(animal)

            if animal.child:
                new_children.append(animal.child)
                self.chunks[(animal.child.chunk_x, animal.child.chunk_y)][animal.child.type][animal.child.animal_type].append(animal.child)
                animal.child = None

            dead = animal.death()
            if dead:
                dead_animals.append(animal)
                self.chunks[(dead.chunk_x, dead.chunk_y)][dead.type][dead.animal_type].remove(dead)
                                                                                                                        
        eaten_objects = []
        for object in self.object:
            if object.eaten == True:
                eaten_objects.append(object)
                self.chunks[(object.chunk_x, object.chunk_y)][object.type][object.object_type].remove(object)

        self.animal = [
            animal
            for animal in self.animal
            if animal not in dead_animals
        ]

        self.object = [
            object
            for object in self.object
            if object not in eaten_objects
        ]

        self.plant = [
            plant
            for plant in self.plant
            if plant not in eaten_plants
        ]

        self.animal.extend(new_children)

    def update_lists(self):
        self.miesozerni = []
        self.padlinozerni = []
        self.roslinozerni = []
        
        for animal in self.animal:
            if animal.animal_type == 'miesozerne':
                self.miesozerni.append(animal)
            elif animal.animal_type == 'roslinozerne':
                self.roslinozerni.append(animal)
            elif animal.animal_type == 'padlinozerne':
                self.padlinozerni.append(animal)

    def update_graph(self):
        self.graph.x += 1
        if self.graph.x > 400:
            self.graph.x = 50
            self.graph.miesozerni_points = []
            self.graph.roslinozerni_points = []
            self.graph.padlinozerni_points = []
        
        self.graph.miesozerni_points.append((self.graph.x, 750 - int(len(self.miesozerni) / 1.5)))
        self.graph.roslinozerni_points.append((self.graph.x, 750 - int(len(self.roslinozerni) / 1.5)))
        self.graph.padlinozerni_points.append((self.graph.x, 750 - int(len(self.padlinozerni) / 1.5)))



world = World()

world.render()

while world.settings.running:
    for event in pygame.event.get():    
        if event.type == pygame.QUIT:
            world.settings.running = False
    
    world.update_lists()
    
    world.settings.iterator += 1

    if world.settings.iterator % 1 == 0:
        helpers.print_info(world)

    world.update_world()
    
    world.settings.screen.fill(world.settings.background_color)
    
    world.draw()
    
    world.update_graph()
    
    world.graph.draw()
        
    pygame.display.flip()
    world.settings.clock.tick(600) 