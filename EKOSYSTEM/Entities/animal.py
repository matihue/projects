import random
import copy

import Core.helpers as helpers
from Entities.object import Object

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
        
        self.epsilon = 0.6
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
    
        self.epsilon = max(0.05, self.epsilon - 0.005)
            
    def can_reproduce_with(self, other):
        return (
            other is not self and
            helpers.distance(self.x, self.y, other.x, other.y) <= (self.size + other.size + 2)**2 and
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
        
        old_dist_cat = self.distance_category(helpers.distance(self.x, self.y, closest.x, closest.y))
        x,y = helpers.find_direction(self.x, self.y, closest.x, closest.y)
        self.x += x * self.speed
        self.y += y * self.speed
        new_dist_cat = self.distance_category(helpers.distance(self.x, self.y, closest.x, closest.y))
        if old_dist_cat > new_dist_cat:
            return True
        else:
            return False
        
    def eat(self, food):
        if food and helpers.distance(self.x, self.y, food.x, food.y) < (self.size + food.size)**2:
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
                            
            child.mutation_tendence = min(1, max(0, (helpers.avg(self.mutation_tendence, partner.mutation_tendence) + random.uniform(-0.2, +0.2))))
            child.vision = max(0, (helpers.avg(self.vision, partner.vision) + random.uniform(-3*child.mutation_tendence,3*child.mutation_tendence)))
            child.speed = max(0, helpers.avg(self.speed, partner.speed) + random.uniform(-2*child.mutation_tendence, 2*child.mutation_tendence))
            child.size = max(0, helpers.avg(self.size, partner.size) + random.uniform(-2*child.mutation_tendence, 2*child.mutation_tendence))
            child.energy = helpers.avg(self.base_energy, partner.base_energy) * 0.4
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
            x,y = helpers.find_direction(self.x, self.y, threat.x, threat.y)
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
                    if helpers.distance(self.x, self.y, threat.x, threat.y) <= self.vision**2:
                    
                        if closest_threat:

                            if helpers.distance(self.x, self.y, threat.x, threat.y) <= helpers.distance(self.x,self.y, closest_threat.x,closest_threat.y):
                                closest_threat = threat 
                    
                        elif not closest_threat:
                            closest_threat = threat

        closest_food = None
        closest_partner = None
        for chunk in chunks:
            for name in self.food_names:
                for food in chunk[self.food_group][name]:
            
                    if helpers.distance(self.x, self.y, food.x, food.y) <= self.vision**2:
                
                        if helpers.is_valid_food(food):
                                
                            if closest_food and helpers.distance(self.x, self.y, food.x, food.y) <= helpers.distance(self.x,self.y, closest_food.x,closest_food.y):
                                closest_food = food

                        elif not closest_food:
                            closest_food = food
            
            for partner in chunk[self.type][self.animal_type]:
                if partner.gender != self.gender:
                    dist = helpers.distance(self.x, self.y, partner.x, partner.y) 
                    if dist <= self.vision**2:

                        if closest_partner:
                            if dist <= helpers.distance(self.x, self.y, closest_partner.x, closest_partner.y):
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
            
        food_dist = self.distance_category(helpers.distance(self.x, self.y, closest_food.x, closest_food.y) if closest_food else None)
        
        threat_dist = self.distance_category(helpers.distance(self.x, self.y, closest_threat.x, closest_threat.y) if closest_threat else None)
        
        partner_dist = self.distance_category(helpers.distance(self.x, self.y, closest_partner.x, closest_partner.y) if closest_partner else None)   
            
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
                    nagroda -= 1
            
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
            self.Q[stan] = {action: 0 for action in self.actions}
            
        for action in self.actions:
            if action not in self.Q[stan]:
                self.Q[stan][action] = 0

        if random.random() < self.epsilon:
            akcja = random.choice(self.actions)
        else:
            akcja = max(self.Q[stan], key=self.Q[stan].get)

        nagroda += self.execute_action(stan, akcja, closest_food, closest_partner, closest_threat)

        nowy_stan = self.get_state()

        if nowy_stan not in self.Q:
            self.Q[nowy_stan] = {action: 0 for action in self.actions}
            
        for action in self.actions:
            if action not in self.Q[nowy_stan]:
                self.Q[nowy_stan][action] = 0

        blad = nagroda + self.settings.gamma * max(self.Q[nowy_stan].values()) - self.Q[stan][akcja]
        self.Q[stan][akcja] = self.Q[stan][akcja] + self.settings.learning_rate * blad

        self.x = max(0, min(self.world.width, self.x))
        self.y = max(0, min(self.world.height, self.y))