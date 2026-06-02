import math
import random
import copy
import itertools
import pygame
pygame.init()

def find_direction(x1, y1, x2, y2):
    distance_x = x2-x1
    distance_y = y2-y1

    if distance_x < 0:
        x = -1
    elif distance_x == 0:
        x = 0
    elif distance_x > 0:
        x = 1

    if distance_y < 0:
        y = -1
    elif distance_y == 0:
        y = 0
    elif distance_y > 0:
        y = 1
    
    return x, y

def avg(x,y):
    return (x+y)/2

def distance(x1,y1, x2,y2):
    dx = x2 - x1
    dy = y2 - y1

    return (dx**2 + dy**2)

class Settings:
    def __init__(self):             
        ### WORLD ###
        self.world_width = 1000
        self.world_height = 1000
        self.screen = pygame.display.set_mode((self.world_width, self.world_height))
        self.clock = pygame.time.Clock()
        self.background_color = (34, 71, 32)
        
        ### CHOICES ###
        self.directions = [-1, 1]
        self.surfaces = ['x', 'y']
        self.cross = [True, False]
        self.genders = ['female', 'male']

        ### AI ###
        self.learning_rate = 0.1
        self.gamma = 0.9

        ### LOOP SETTINGS ###
        self.iterator = 0
        self.running = True

        ### VALUES ###
        self.miesozercy = 0
        self.roslinozercy = 100
        self.padlinozercy = 0
        
        self.trees = 1000
        self.grass = 2
        self.rocks = 0
        self.water = 5
    
        self.chunk_size = 100

        ### PRESETS ###
        self.presets = {
            'miesozerne' : {
                'size': [3,5],
                'energy': [1000, 1500],
                'vision': [70, 190],
                'speed': [2,5],
                'energy_to_reproduce': 800,
                'life_cost': 4,
                'food_group': 'animal',
                'food_names': ['roslinozerne'],
                'reproduction_cooldown': 30,
                'starting_Q': {},
                'actions': ['go_to_food', 'go_to_partner', 'wander','eat','reproduce'],
                'color': (214, 85, 58)
            },
            'roslinozerne' : {
                'size': [1,3],
                'energy': [700, 1000],
                'vision': [90, 150],
                'speed': [3,6],
                'energy_to_reproduce': 900,
                'life_cost': 3,
                'food_group': 'plant',
                'food_names': ['tree', 'grass'],
                'reproduction_cooldown': 60,
                'starting_Q': {},
                'actions': ['go_to_food', 'go_to_partner', 'flee','wander','eat','reproduce'],
                'color': (17, 242, 54)
            },
            'padlinozerne' : {
                'size': [2,3],
                'energy': [800, 1200],
                'vision': [150, 200],
                'speed': [5,6],
                'energy_to_reproduce': 800,
                'life_cost': 3,
                'food_group': 'object',
                'food_names': ['corpse'],
                'reproduction_cooldown': 40,
                'starting_Q': {},
                'actions': ['go_to_food', 'go_to_partner', 'flee','wander','eat','reproduce'],
                'color': (122, 98, 16)
            },
            'tree': {
                'size': [3,6],
                'energy_stored': [2000, 3000],
                'life_cost': 1,
                'color': (38, 130, 26)
            },
            'grass': {
                'size': [50, 80],
                'energy_stored': [15000, 18000],
                'life_cost': 1,
                'color': (111, 145, 106)
            },
            'rock': {
                'color': (64, 63, 63)
            },
            'corpse':{
                'color': (222, 221, 181)
            },
            'water': {
                'color': (34, 71, 140) 
            }
            
        }
    

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

    def __repr__(self):

        return f"{self.object_type}(id={self.number}, x={getattr(self, 'x', None)}, y={getattr(self, 'y', None)})"

class Animal:
    def __init__(self, animal_type, number, world):
        self.type = 'animal'
        self.animal_type = animal_type
        self.number = number
        self.world = world
        self.settings = self.world.settings
        self.preset = self.settings.presets[animal_type]

        self.x = random.randint(1, self.world.width)
        self.y = random.randint(1, self.world.height)
        self.chunk_x = self.x // self.settings.chunk_size
        self.chunk_y = self.y // self.settings.chunk_size

        self.age = 1

        self.size = random.randint(*self.preset['size'])
        self.energy = random.randint(*self.preset['energy'])
        self.base_energy = self.energy
        self.vision = random.randint(*self.preset['vision'])
        self.speed = random.randint(*self.preset['speed'])
        self.energy_to_reproduce = self.preset['energy_to_reproduce']
        self.life_cost = self.preset['life_cost']

        self.mutation_tendence = random.random()
        self.gender = random.choice(self.settings.genders)     
        self.reproduction_cooldown = 0

        self.threat = 'miesozerne' if self.animal_type == 'roslinozerne' or self.animal_type == 'padlinozerne' else None
        
        self.food_group = self.preset['food_group']
        self.food_names = self.preset['food_names']

        self.dead = False   

        self.Q = copy.deepcopy(self.preset['starting_Q'])

        self.actions = self.preset['actions']
        
        self.child = None
        
        self.epsilon = 1
        self.color = self.preset['color']

    def update(self):
        self.x = max(0, min(self.world.width, self.x))
        self.y = max(0, min(self.world.height, self.y)) 

        self.age += 1
        self.reproduction_cooldown -= 1 if self.reproduction_cooldown > 0 else 0
                
        self.energy -= (
            self.size * 0.2 # koszt zycia zwiazany z rozmiarem
            + self.life_cost
        )

        if self.energy <= 0 or self.age > 500 + random.randint(-100, 100):
            self.dead = True
    
        self.epsilon = max(0.1, self.epsilon - 0.001)
            
    def can_reproduce_with(self, other):
        return (
            other is not self and
            distance(self.x, self.y, other.x, other.y) <= (self.size + other.size + 2)**2 and
            self.animal_type == other.animal_type and
            self.gender != other.gender and
            self.reproduction_cooldown == 0 and
            other.reproduction_cooldown == 0 and
            self.age > 15 and
            other.age > 15 and
            self.energy > self.energy_to_reproduce and
            other.energy > other.energy_to_reproduce
        )

    def death(self):
        if self.dead == True:
            corpse = Object(object_type='corpse', number=1, world = self.world)
            corpse.x = self.x
            corpse.y = self.y
            corpse.chunk_x = corpse.x // self.settings.chunk_size
            corpse.chunk_y = corpse.y // self.settings.chunk_size
            self.world.object.append(corpse)
            self.world.chunks[(corpse.chunk_x, corpse.chunk_y)][corpse.type][corpse.object_type].append(corpse)
            return self      
        else:
            return None

    def go_to(self, closest):
        if closest is None:
            return False
        
        old_dist_cat = self.distance_category(distance(self.x, self.y, closest.x, closest.y))
        x,y = find_direction(self.x, self.y, closest.x, closest.y)
        self.x += x * self.speed
        self.y += y * self.speed
        new_dist_cat = self.distance_category(distance(self.x, self.y, closest.x, closest.y))
        if old_dist_cat > new_dist_cat:
            return True
        else:
            return False
        
    def eat(self, food):
        if food and distance(self.x, self.y, food.x, food.y) < (self.size + food.size)**2:
            if food.type == 'plant':
                if food.eaten:
                    return
                if food.plant_type in self.food_names:
                    requested = random.randint(200,500)
                    actual = min(requested, food.energy_stored)
                    self.energy += actual
                    food.energy_stored -= actual
                    if food.energy_stored <= 0:
                        food.eaten = True
                        food.energy_stored = 0
                    return True

            if food.type == 'animal':
                if food.dead:
                    return

                if food.animal_type in self.food_names:
                    food.dead = True
                    self.energy += food.energy * 0.7
                    return True
                                
            if food.type == 'object':
                if food.eaten:
                    return
                if food.object_type in self.food_names:
                    food.eaten = True
                    self.energy += 300
                    return True
        else:
            return False
     
    def reproduce(self, partner):

        if partner and self.can_reproduce_with(partner):

            self.energy -= 300
            partner.energy -= 300
            self.reproduction_cooldown = partner.reproduction_cooldown = self.preset['reproduction_cooldown']
                    
            child = Animal(animal_type = self.animal_type, number = self.number, world = self.world)
                            
            child.mutation_tendence = min(1, max(0, (avg(self.mutation_tendence, partner.mutation_tendence) + random.uniform(-0.2, +0.2))))
            child.vision = max(0, (avg(self.vision, partner.vision) + random.uniform(-3*child.mutation_tendence,3*child.mutation_tendence)))
            child.speed = max(0, avg(self.speed, partner.speed) + random.uniform(-2*child.mutation_tendence, 2*child.mutation_tendence))
            child.size = max(0, avg(self.size, partner.size) + random.uniform(-2*child.mutation_tendence, 2*child.mutation_tendence))
            child.energy = avg(self.base_energy, partner.base_energy) * 0.4
            child.Q = copy.deepcopy(self.Q)

            child.actions = self.preset['actions']
                    
            for stan, akcja in child.Q.items():
                for action in child.actions:
                    if action not in akcja:
                        akcja[action] = 0                            
                        
            child.x, child.y = self.x, self.y

            child.chunk_x = child.x // self.settings.chunk_size
            child.chunk_y = child.y // self.settings.chunk_size

            return child
                
        return False                        
                              
    def flee(self, threat):
        if threat:
            x,y = find_direction(self.x, self.y, threat.x, threat.y)
            self.x -= x * self.speed
            self.y -= y * self.speed
            return True
        else:
            return False
    
    def wander(self):
        if random.choice(self.settings.cross) == True:
            self.x += random.choice(self.settings.directions) * self.speed / 1.41 
            self.y += random.choice(self.settings.directions) * self.speed / 1.41
        else:
            if random.choice(self.settings.surfaces) == 'x':
                self.x += random.choice(self.settings.directions) * self.speed
            elif random.choice(self.settings.surfaces) == 'y':
                self.y += random.choice(self.settings.directions) * self.speed
                                                                           
    def distance_category(self, dist):
        if dist is None:
            return 3
        if dist <= (self.vision / 9)**2:
            return 0
        elif dist <= (self.vision / 3)**2:
            return 1
        else:
            return 2

    def find_closest(self):
        closest_threat = None

        chunks = self.world.get_near_chunks(self.chunk_x, self.chunk_y, self.vision, self.settings.chunk_size)

        if self.threat:
            
            for chunk in chunks:

                threats = chunk['animal'][self.threat]
            
                for threat in threats:     
                    if distance(self.x, self.y, threat.x, threat.y) <= self.vision**2:
                    
                        if closest_threat:

                            if distance(self.x, self.y, threat.x, threat.y) <= distance(self.x,self.y, closest_threat.x,closest_threat.y):
                                closest_threat = threat 
                    
                        elif not closest_threat:
                            closest_threat = threat

        closest_food = None
        closest_partner = None
        for chunk in chunks:
            for name in self.food_names:
                for food in chunk[self.food_group][name]:
            
                    if distance(self.x, self.y, food.x, food.y) <= self.vision**2:
                
                        if closest_food:
                                
                            if distance(self.x, self.y, food.x, food.y) <= distance(self.x,self.y, closest_food.x,closest_food.y):
                                closest_food = food

                        elif not closest_food:
                            closest_food = food
            
            for partner in chunk[self.type][self.animal_type]:
                if partner.gender != self.gender:
                    dist = distance(self.x, self.y, partner.x, partner.y) 
                    if dist <= self.vision**2:

                        if closest_partner:
                            if dist <= distance(self.x, self.y, closest_partner.x, closest_partner.y):
                                closest_partner = partner

                        elif not closest_partner:
                            closest_partner = partner

        return closest_food, closest_threat, closest_partner

    def get_state(self):
        closest_food, closest_threat, closest_partner = self.find_closest()

        if self.energy <= 400:
         energy_level = 'low'
        elif self.energy <= 900:
            energy_level = 'medium'
        else:
            energy_level = 'high' 
            
        food_dist = self.distance_category(distance(self.x, self.y, closest_food.x, closest_food.y) if closest_food else None)
        
        threat_dist = self.distance_category(distance(self.x, self.y, closest_threat.x, closest_threat.y) if closest_threat else None)
        
        partner_dist = self.distance_category(distance(self.x, self.y, closest_partner.x, closest_partner.y) if closest_partner else None)   
            
        stan = (food_dist, threat_dist, partner_dist, energy_level)
        
        return stan

    def execute_action(self, stan, akcja, closest_food, closest_partner, closest_threat):
        nagroda = 0
        a, threat_dist, c, energy_level = stan
        
        if self.dead:
            nagroda -= 500
        
        if akcja == 'go_to_food':
            if self.go_to(closest_food):
                if energy_level == 'low':
                    nagroda += 50
                elif energy_level == 'medium':
                    nagroda += 20
                elif energy_level == 'high':
                    nagroda += 1
            else:
                if energy_level == 'low':
                    nagroda -= 30
                elif energy_level == 'medium':
                    nagroda -= 15
                elif energy_level == 'high':
                    nagroda += 8
            
        if akcja == 'go_to_partner':
            if self.go_to(closest_partner):
                if energy_level == 'low':
                    nagroda -= 30
                elif energy_level == 'medium':
                    nagroda += 5
                elif energy_level == 'high':
                    nagroda += 60
            else:
                if energy_level == 'low':
                    nagroda += 10
                elif energy_level == 'medium':
                    nagroda -= 4
                elif energy_level == 'high':
                    nagroda -= 30
        
        if akcja == 'eat':
            if self.eat(closest_food):
                if energy_level == 'low':
                    nagroda += 50
                elif energy_level == 'medium':
                    nagroda += 20
                elif energy_level == 'high':
                    nagroda += 3
            else:
                if energy_level == 'low':
                    nagroda -= 40
                elif energy_level == 'medium':
                    nagroda -= 18
                elif energy_level == 'high':
                    nagroda -= 2

        elif akcja == 'reproduce':
            child = self.reproduce(closest_partner)
            if child:
                if energy_level == 'low':
                    nagroda -= 20
                elif energy_level == 'medium':
                    nagroda += 70
                elif energy_level == 'high':
                    nagroda += 200
                self.child = child
            else:
                if energy_level == 'low':
                    nagroda -= 20
                elif energy_level == 'medium':
                    nagroda -= 30
                elif energy_level == 'high':
                    nagroda -= 50
            
        elif akcja == 'flee':
            if self.flee(closest_threat):
                if threat_dist == 0:
                    nagroda += 40
                elif threat_dist == 1:
                    nagroda += 15
                elif threat_dist == 2:
                    nagroda += 3
                else:
                    nagroda -= 5    
            else:
                if threat_dist == 0:
                    nagroda -= 50
                elif threat_dist == 1:
                    nagroda -= 20
                elif threat_dist == 2:
                    nagroda -= 3
                else:
                    nagroda += 1
                
        elif akcja == 'wander':
            self.wander()
            if energy_level == 'low':
                nagroda -= 10
            elif energy_level == 'medium':
                nagroda -= 6
            elif energy_level == 'high':
                nagroda -= 1
                
        if self.settings.iterator % 10 == 0:
            nagroda += 2
        
        return nagroda       

    def ai(self):

        nagroda = 0
        
        stan = self.get_state()
        
        closest_food, closest_threat, closest_partner = self.find_closest()
        
        if stan not in self.Q:
            self.Q[stan] = {akcja: 0 for akcja in self.actions}

        if random.random() < self.epsilon:
            akcja = random.choice(self.actions)
        else:
            akcja = max(self.Q[stan], key=self.Q[stan].get)

        nagroda += self.execute_action(stan, akcja, closest_food, closest_partner, closest_threat)

        nowy_stan = self.get_state()

        if nowy_stan not in self.Q:
            self.Q[nowy_stan] = {akcja: 0 for akcja in self.actions}

        blad = nagroda + self.settings.gamma * max(self.Q[nowy_stan].values()) - self.Q[stan][akcja]
        self.Q[stan][akcja] = self.Q[stan][akcja] + self.settings.learning_rate * blad

        self.x = max(0, min(self.world.width, self.x))
        self.y = max(0, min(self.world.height, self.y))
            

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
        
            
    def print_info(self):

        def stats(group):
            if len(group) == 0:
                return {
                    "count": 0,
                    "speed": 0,
                    "vision": 0,
                    "size": 0,
                    "energy": 0
                }

            return {
                "count": len(group),
                "speed": round(sum(a.speed for a in group) / len(group), 2),
                "vision": round(sum(a.vision for a in group) / len(group), 2),
                "size": round(sum(a.size for a in group) / len(group), 2),
                "energy": round(sum(a.energy for a in group) / len(group), 2)
            }
        
        mieso_list = []
        rosli_list = []
        padli_list = []
        trees_list = []

        for animal in self.animal:
            if animal.animal_type == 'miesozerne':
                mieso_list.append(animal)
            elif animal.animal_type == 'roslinozerne':
                rosli_list.append(animal)
            elif animal.animal_type == 'padlinozerne':
                padli_list.append(animal)

        for plant in self.plant:
            if plant.plant_type == 'tree':
                trees_list.append(plant)
                

        mieso = stats(mieso_list)
        rosli = stats(rosli_list)
        padli = stats(padli_list)

        print("\n" + "=" * 90)
        print(f"ITERACJA: {self.settings.iterator}")
        print("=" * 90)

        print(
            f"{'STAT':<15}"
            f"{'MIESOZERNE':<20}"
            f"{'ROSLINOZERNE':<20}"
            f"{'PADLINOZERNE':<20}"
        )

        print("-" * 90)

        print(
            f"{'LICZBA':<15}"
            f"{mieso['count']:<20}"
            f"{rosli['count']:<20}"
            f"{padli['count']:<20}"
        )

        print(
            f"{'SPEED':<15}"
            f"{mieso['speed']:<20}"
            f"{rosli['speed']:<20}"
            f"{padli['speed']:<20}"
        )

        print(
            f"{'VISION':<15}"
            f"{mieso['vision']:<20}"
            f"{rosli['vision']:<20}"
            f"{padli['vision']:<20}"
        )

        print(
            f"{'SIZE':<15}"
            f"{mieso['size']:<20}"
            f"{rosli['size']:<20}"
            f"{padli['size']:<20}"
        )

        print(
            f"{'ENERGY':<15}"
            f"{mieso['energy']:<20}"
            f"{rosli['energy']:<20}"
            f"{padli['energy']:<20}"
        )

        print("=" * 90)
    
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


world = World()

world.render()

while world.settings.running:
    for event in pygame.event.get():    
        if event.type == pygame.QUIT:
            world.settings.running = False
    
    
    world.settings.iterator += 1

    if world.settings.iterator % 1 == 0:
        world.print_info()
    
    world.update_world()
    
    world.settings.screen.fill(world.settings.background_color)
    
    world.draw()
        
    pygame.display.flip()
    world.settings.clock.tick(600) 