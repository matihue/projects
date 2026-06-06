import pygame

class Settings:
    def __init__(self):             
        ### WORLD ###
        self.world_width = 500
        self.world_height = 500
        self.screen = pygame.display.set_mode((self.world_width, self.world_height+300))
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
        self.miesozercy = 30
        self.roslinozercy = 100
        self.padlinozercy = 70
        
        self.trees = 1000
        self.grass = 5
        self.rocks = 0
        self.water = 5
    
        self.chunk_size = 50

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
                'starting_Q': {
                    (0, 3, 3, 'low'): {
                        'eat': 500,
                        'go_to_food': 300
                    },
                    (3, 3, 0, 'high'): {
                        'reproduce': 700,
                        'go_to_partner': 400
                    }
                },
                'actions': ['go_to_food', 'go_to_partner', 'wander','eat','reproduce'],
                'color': (214, 85, 58),
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
                'starting_Q': {
                    (0, 3, 3, 'low'): {
                        'eat': 300,
                        'go_to_food': 100
                    },
                    (3, 0, 3, 'medium'): {
                        'flee': 400
                    },
                    (3, 3, 0, 'high'): {
                        'reproduce': 500,
                        'go_to_partner': 300
                    }
                        
                },
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
                'starting_Q': {
                    (0, 3, 3, 'low'): {
                        'eat': 400,
                        'go_to_food': 200
                    },
                    (3, 3, 0, 'high'): {
                        'reproduce': 500,
                        'go_to_partner': 300
                    }      
                },
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