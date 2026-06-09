import pygame
import math
pygame.init()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((1500, 900))
        self.clock = pygame.time.Clock()
        
        self.running = True
        self.state = 'start'
        self.selected_body = None
        self.following_com_state = False
        
        self.cam_x = 0
        self.cam_y = 0
        self.cam_speed = 5
        self.zoom = 1
        self.grid_cam_x = 0
        self.grid_cam_y = 0
        
        self.timewarp = 1
        self.timewarp_levels = {
            '1 dzień/s':    86400,
            '1 miesiąc/s':  2_592_000,
            '1 rok/s':      31_536_000,
            '10 lat/s':     315_360_000
        }
        
        self.trail_color = "#615D5D"    
        self.background_color = (15, 15, 15)    
        
        self.dt = 0.1
        self.scale = 0.008
        self.grid_size = 200
        
        self.G_scaled = 4 * math.pi**2
        self.M_sun = 1
        self.star_colors = [
            (0, 0, 255),      # niebieski
            (255, 255, 255),  # biały
            (255, 255, 0),    # żółty
            (255, 140, 0),    # pomarańczowy
            (255, 0, 0),      # czerwony
            (180, 0, 255),    # fioletowy
        ]
        self.planet_colors = [
            (153, 102, 51), 
            (173, 173, 133),
            (115, 153, 0),
            (0, 179, 0),
            (0, 179, 134), 
            (51, 204, 255), 
            (0, 77, 153), 
            (102, 102, 153), 
            (128, 128, 0)
        ]
        self.moon_colors = [
            (210, 190, 160), 
            (60, 60, 60)
        ]
        
        
        self.M_earth = 3e-6 
        self.M_moon = 3.7e-8
        
        self.min_mass = self.M_moon
        self.max_mass = 5 * self.M_sun
        
        self.max_mass_values = {'sun': 5, 'earth': 100, 'moon': 800}
        self.max_radius_values = {'sun': 200, 'earth': 10, 'moon': 3}
        self.min_radius_values = {'sun': 30, 'earth': 1, 'moon': 1}
        self.AU = 200
                
############################################################################################################################################################################################
        
        # OBIEKTY #
        
        self.fonts = {
            'font1': pygame.font.SysFont(None, 60),
            'font2': pygame.font.SysFont('segoe ui', 18)
        }
        
        self.bodies = []
        
        total_mass = sum(b.m for b in self.bodies)
        self.gcx = None
        self.gcy = None
        
        
        self.vectors = [Vector(body = b, game=self) for b in self.bodies]
        self.sliders = []
        self.collisions = []
        self.picker = None
        
        ############## PRZYCISKI ##############
        
        self.start_button = Button(x = 1300, y = 800, width = 180, height = 80, color = "#163e63", text='Start', font = self.fonts['font1'])
        self.back_button = Button(x = 1300, y = 800, width = 180, height = 80, color = "#163e63", text='Return', font = self.fonts['font1'])
        self.del_button = Button(x=1100, y= 800, width = 100, height = 50, color = "#d14a4a", text = 'Delete', font = self.fonts['font2'])
        self.add_button = None
        self.following_com = Button(x=690, y = 820, width = 120, height = 50, color = "#D4AA21", text = 'Follow COM', font = self.fonts['font2'])
        
        self.Sun = Button(x =  40,y = 780, width = 70, height= 30, color="#c7d63a", text='Sun M', font=self.fonts['font2'])
        self.Earth = Button(x = 120,  y = 780, width = 70, height= 30, color="#159fc9", text='Earth M', font=self.fonts['font2'])
        self.Moon = Button(x = 200, y = 780, width = 70, height= 30, color="#51524d", text='Moon M', font=self.fonts['font2'])

        
############################################################################################################################################################################################
      
    def calc_gravity_center(self):
        if len(self.bodies) > 0:
            for body in self.bodies:
                body.m = self.get_real_mass(body)
                
            total_mass = sum(b.m for b in self.bodies)
            if total_mass == 0:
                total_mass += 0.1
            
            self.gcx = sum(b.m * b.x for b in self.bodies) / total_mass
            self.gcy = sum(b.m * b.y for b in self.bodies) / total_mass
       
    def cam(self):
        keys = pygame.key.get_pressed()
        self.cam_speed = 5 / self.zoom
        
        if not self.following_com_state:
            if keys[pygame.K_a]:
                self.cam_x -= self.cam_speed
            if keys[pygame.K_d]:
                self.cam_x += self.cam_speed
            if keys[pygame.K_w]:
                self.cam_y -= self.cam_speed
            if keys[pygame.K_s]:
                self.cam_y += self.cam_speed
        elif self.following_com_state and self.state == 'simulation':
            self.calc_gravity_center()
            self.cam_x = self.gcx - 750 / self.zoom
            self.cam_y = self.gcy - 450 / self.zoom
    
    def handle_timewarp(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            self.timewarp += 1
        if keys[pygame.K_q] and self.timewarp > 1:
            self.timewarp -= 1
            
    def handle_zoom(self, scroll):
        mx, my = pygame.mouse.get_pos()
        
        old_zoom = self.zoom
        
        if scroll == 'up' :
            self.zoom += 0.1
        if scroll == 'down' and self.zoom > 0.11:
            self.zoom -= 0.1
        
        self.cam_x = mx / old_zoom + self.cam_x - mx / self.zoom
        
        self.cam_y = my / old_zoom + self.cam_y - my / self.zoom
          
    def draw_grid(self):
        
        scaled_grid = self.grid_size * self.zoom
        
        first_line_world_x = math.floor(self.cam_x / self.grid_size) * self.grid_size
        first_line_world_y = math.floor(self.cam_y / self.grid_size) * self.grid_size
        
        screen_x = (first_line_world_x - self.cam_x) * self.zoom
        screen_y = (first_line_world_y - self.cam_y) * self.zoom
        
        for x in range(int(screen_x), 1500, int(scaled_grid)):
            pygame.draw.line(self.screen, (25,25,35), (x,0), (x,900), 1)
            
        for y in range(int(screen_y), 900, int(scaled_grid)):
            pygame.draw.line(self.screen, (25,25,35), (0,y), (1500,y), 1) 
       
    def handle_start_events(self, event):
        
        mx, my = pygame.mouse.get_pos()
            
        if event.button == 1:    
            
            #### SPRAWDZANIE CZY CIAŁO JEST KLIKNIĘTE ####
            clicked = []
            for body in self.bodies:
                distance = onclicked(mx, my, (body.x - self.cam_x) * self.zoom, (body.y - self.cam_y) * self.zoom)
                if distance < body.r * self.zoom:
                    body.dragging = True
                    self.selected_body = body
                    self.sliders.clear()
                    self.sliders.append(Slider(40, 850, body.mass_multiplier, 0 ,self.max_mass_values[body.mass_unit]))
                    self.sliders.append(Slider(380, 850, body.r, self.min_radius_values[body.mass_unit],self.max_radius_values[body.mass_unit]))
                    self.picker = Picker(x=380, y= 780, size = 20, body_type ='planet')
                    clicked.append(body)
            
            #### SPRAWDZANIE PICKERA ####
            if self.selected_body:
                for button in self.picker.picker:
                    if button.rect.collidepoint(mx, my):
                        self.selected_body.color = button.color
                        clicked.append(button)
                
            #### SPRAWDZANIE PRZYCISKU USUWANIA CIAŁ ####
            if self.state == 'start' and self.selected_body and self.del_button and self.del_button.rect.collidepoint(mx, my):
                i = self.bodies.index(self.selected_body)
                self.bodies.remove(self.selected_body)
                self.vectors.pop(i)
                self.selected_body = None
                self.sliders.clear()
                clicked.append(self.del_button)

            #### SPRAWDZANIE PRZYCISKÓW JEDNOSTEK MASY W SLIDERACH ####                
            if self.selected_body and len(self.sliders) == 2:
                if self.Sun.rect.collidepoint(mx, my):
                    clicked.append(self.Sun)
                    self.selected_body.mass_unit = 'sun'
                    self.selected_body.color = self.star_colors[0]
                    self.sliders[0].max_value = self.max_mass_values['sun']
                    self.selected_body.mass_multiplier = (self.sliders[0].x_ball - self.sliders[0].x) / self.sliders[0].width * self.sliders[0].max_value
                    self.sliders[0].x_ball = self.sliders[0].x + self.sliders[0].width * (self.selected_body.mass_multiplier / (self.max_mass_values['sun']))      
                    self.picker.body_type = 'star'
                    
                if self.Earth.rect.collidepoint(mx, my):
                    clicked.append(self.Earth)
                    self.selected_body.mass_unit = 'earth'
                    self.selected_body.color = self.planet_colors[0]
                    self.sliders[0].max_value = self.max_mass_values['earth']
                    self.selected_body.mass_multiplier = (self.sliders[0].x_ball - self.sliders[0].x) / self.sliders[0].width * self.sliders[0].max_value
                    self.sliders[0].x_ball = self.sliders[0].x + self.sliders[0].width * (self.selected_body.mass_multiplier / self.max_mass_values['earth'])
                    self.picker.body_type = 'planet'
                    
                if self.Moon.rect.collidepoint(mx, my):
                    clicked.append(self.Moon)
                    self.selected_body.mass_unit = 'moon'
                    self.selected_body.color = self.moon_colors[0]
                    self.sliders[0].max_value = self.max_mass_values['moon']
                    self.selected_body.mass_multiplier = (self.sliders[0].x_ball - self.sliders[0].x) / self.sliders[0].width * self.sliders[0].max_value
                    self.sliders[0].x_ball = self.sliders[0].x + self.sliders[0].width * (self.selected_body.mass_multiplier / self.max_mass_values['moon'])
                    self.picker.body_type = 'moon'
                
                self.sliders[1].max_value = self.max_radius_values[self.selected_body.mass_unit]
                self.sliders[1].min_value = self.min_radius_values[self.selected_body.mass_unit]
                self.selected_body.r = self.sliders[1].calc_val()
                
                for slider in self.sliders:
                    if self.selected_body:
                        distance = onclicked(mx,my,slider.x_ball,slider.y_ball)
                        if distance < slider.r_ball:
                            slider.dragging = True
                            clicked.append(slider)

            if clicked == []:   
                
            #### SPRAWDZANIE PRZYCISKU DODAWANIA CIAŁ ####    
                if self.state == 'start' and self.add_button and self.add_button.rect.collidepoint(mx, my):
                    self.bodies.append(Body(x = (self.add_button.rect.x / self.zoom) + self.cam_x , y = (self.add_button.rect.y / self.zoom) + self.cam_y , m=5, r=10, game=self))
                    self.vectors.append(Vector(body=self.bodies[-1], game=self))
                    self.add_button = None  
                
            #### ODKLIKIWANIE CIAł ####
                self.selected_body = None
                
            #### SPRAWDZANIE PRZYCISKU STARTU SYMULACJI    
            if self.start_button.rect.collidepoint(mx, my):
                for body in self.bodies:
                    body.m = game.get_real_mass(body)
                self.state = 'simulation'      
            
        #### SCHOWANIE PRZYCISKU DODAWANIA CIAŁ PO KLIKNIĘCIU PRAWYM ####
        if event.button == 3:
            if self.add_button and self.add_button.rect.collidepoint(mx, my):
                self.add_button = None
                return

        #### SPRAWDZANIE KLIKNIĘCIA PRAWYM NA PUSTE POLE LUB CIAŁO ####
            clicked = []
            for i, body in enumerate(self.bodies):
                distance = onclicked(mx,my,(body.x-self.cam_x)*self.zoom,(body.y-self.cam_y)*self.zoom)
                if distance < body.r * self.zoom:
                    self.vectors[i].dragging = True
                    clicked.append(body)
            if clicked == []:
                self.add_button = Button(x=mx, y=my, width=85, height=30, color="#614545", text='Add body', font=self.fonts['font2'])               
                       
    def update_start(self):
            
        for body in self.bodies:
            if body.dragging:
                mx, my = pygame.mouse.get_pos()
                body.x = (mx / self.zoom) + self.cam_x
                body.y = (my / self.zoom) + self.cam_y
                                            
        for vector in self.vectors:
            if vector.dragging == True:
                mx, my = pygame.mouse.get_pos()
                vector.update(mx, my)
        
        if self.selected_body and len(self.sliders) == 2:
            mx, my = pygame.mouse.get_pos()
            
            value = self.sliders[0].update(mx) if self.sliders[0].dragging else None
            if value is not None:
                
                self.selected_body.mass_multiplier = value
            
            value = self.sliders[1].update(mx) if self.sliders[1].dragging else None
            if value is not None:
                self.selected_body.r = value
            
            self.picker.picker_buttons(self)
            
        self.calc_gravity_center()           
                 
    def draw_start(self):
        
        ### SELECT BODY GLOW ###
        if self.selected_body:
            screen_x = (self.selected_body.x - self.cam_x) * self.zoom
            screen_y = (self.selected_body.y - self.cam_y) * self.zoom
            screen_r = (self.selected_body.r) * self.zoom
            pygame.draw.circle(self.screen, (0, 243, 255), (int(screen_x), int(screen_y)), screen_r + 1)
            
        ### SELECT MASS UNIT BUTTON GLOW ###
        if self.selected_body:  
            if self.selected_body.mass_unit == 'sun':
                glow = ButtonGlow(self.Sun)
            elif self.selected_body.mass_unit == 'earth':
                glow = ButtonGlow(self.Earth)
            elif self.selected_body.mass_unit == 'moon': 
                glow = ButtonGlow(self.Moon)
            glow.draw(self.screen)
            
        ### SELECT BUTTONS GLOW ###
        if self.start_button.rect.collidepoint(pygame.mouse.get_pos()):
            glow = ButtonGlow(self.start_button)
            glow.draw(self.screen)
        
        if self.add_button and self.add_button.rect.collidepoint(pygame.mouse.get_pos()):
            glow = ButtonGlow(self.add_button)
            glow.draw(self.screen)
        
        if self.selected_body and self.del_button:
            if self.del_button.rect.collidepoint(pygame.mouse.get_pos()):
                glow = ButtonGlow(self.del_button)
                glow.draw(self.screen)
            self.del_button.draw(self.screen)
            
        ### BODIES ###
        for body in self.bodies:
            screen_x = (body.x - self.cam_x) * self.zoom
            screen_y = (body.y - self.cam_y) * self.zoom
            screen_r = body.r * self.zoom
            pygame.draw.circle(self.screen, (body.color), (int(screen_x), int(screen_y)), int(screen_r))

        ### VECTORS ###
        for vector in self.vectors:
            vector.draw(self.screen, self.fonts)
        
        ### START BUTTON ###
        self.start_button.draw(self.screen)
        
        ### ADD BUTTON ###
        if self.add_button is not None:
            self.add_button.draw(self.screen)
            
        ### SLIDERS ###
        if self.selected_body and len(self.sliders) == 2:
            for slider in self.sliders:
                slider.draw(self.screen)
               
        #### PICKER ####
        if self.selected_body:
            self.picker.draw_picker(self.screen)
               
        ### MASS UNIT BUTTONS ###         
            self.Sun.draw(self.screen)
            self.Earth.draw(self.screen)
            self.Moon.draw(self.screen)
            
        ### DISPLAYED SLIDER MASS & RADIUS ###        
            draw_text(f'Masa: {self.selected_body.mass_multiplier:.2f} {self.selected_body.mass_unit}', self.fonts, self.sliders[0].x, 820)
            draw_text(f'Rozmiar: {self.selected_body.r:.2f}', self.fonts, self.sliders[1].x, 820)
            
        ### GRAVITY CENTER ###
        if len(self.bodies) > 0:
            screen_gcx = (self.gcx - self.cam_x) * self.zoom 
            screen_gcy = (self.gcy - self.cam_y) * self.zoom
            pygame.draw.circle(self.screen, (255, 0, 0), (int(screen_gcx), int(screen_gcy)), 3)
       
    def handle_sim_events(self, event):
        mx, my = pygame.mouse.get_pos()
        
        if event.button == 1:
        
        ### POWRÓT DO EDYTORA ###
            if self.back_button.rect.collidepoint(mx, my):
                self.reset_to_start()
                self.state = 'start'
                
        ### ŚLEDZENIE ŚRODKA CIĘŻKOŚCI ###
            if self.following_com.rect.collidepoint(mx, my):
                self.following_com_state = not self.following_com_state
                self.following_com.set_text('Unfollow COM' if self.following_com_state else 'Follow COM')                
       
    def update_simulation(self):
        steps = min(self.timewarp, 50)
        dt = self.dt * (self.timewarp / steps)
        for _ in range(int(steps)):
            
            for body in self.bodies:
                x_new = body.x + body.vx*dt + 0.5*body.ax*dt**2
                y_new = body.y + body.vy*dt + 0.5*body.ay*dt**2
                body.x, body.y = x_new, y_new

            
            for body in self.bodies:
                ax_new = 0
                ay_new = 0
                for other in self.bodies:
                    if other is not body:
                        ax, ay = body.calc_acceleration(other)
                        ax_new += ax
                        ay_new += ay
        
                body.vx += 0.5*(body.ax + ax_new)*dt
                body.vy += 0.5*(body.ay + ay_new)*dt
                
                body.ax, body.ay = ax_new, ay_new
            
            #################################    ŚRODEK CIĘŻKOŚCI    #################################
            
            self.calc_gravity_center()
            
            #################################    ZDERZENIE     #################################
             
            for i, body in enumerate(self.bodies):
                for other in self.bodies[i+1:]:
                    if other is not body:
                        distance = math.sqrt((body.x - other.x)**2 + (body.y - other.y)**2)
                        if distance < body.r + other.r:
                            Collision(body, other, self).momentum()
                        
            
            #################################    TRAIL    #################################
            
            for body in self.bodies:
                body.trail.append((int(body.x), int(body.y)))
                
                if len(body.trail) > 5000:
                    body.trail.pop(0)
               
    def draw_simulation(self):
        
        ### BODIES ###    
        for body in self.bodies:
            screen_x = (body.x - self.cam_x) * self.zoom
            screen_y = (body.y - self.cam_y) * self.zoom
            screen_gcx = (self.gcx - self.cam_x) * self.zoom 
            screen_gcy = (self.gcy - self.cam_y) * self.zoom
            
            screen_r = body.r * self.zoom
            
            pygame.draw.circle(self.screen, (body.color), (int(screen_x), int(screen_y)), int(screen_r))
            pygame.draw.circle(self.screen, (255, 0, 0), (int(screen_gcx), int(screen_gcy)), 3)
            
        ### TRAILS ###
            if len(body.trail) > 1:
                trail_screen = [((x - self.cam_x) *self.zoom , (y - self.cam_y) *self.zoom ) for x, y in body.trail]
                pygame.draw.lines(self.screen, self.trail_color, False, trail_screen, 1)
        
        ### TEXT ###
        draw_text('W: Up', self.fonts, 10, 787)
        draw_text('S: Down', self.fonts, 10, 807)
        draw_text('A: Right', self.fonts, 10, 827)
        draw_text('D: Left', self.fonts, 10, 847)
        draw_text(f'Q / E : Timewarp: x{self.timewarp:.2f}', self.fonts, 10, 867)

        ### BACK BUTTON ###
        if self.back_button.rect.collidepoint(pygame.mouse.get_pos()):
            glow = ButtonGlow(self.back_button)
            glow.draw(self.screen) 
        self.back_button.draw(self.screen)
        
        ### FOLLOW COM BUTTON ###
        self.following_com.draw(self.screen)
           
    def reset_to_start(self):
        
        self.state, self.cam_x, self.cam_y = 'start', 0, 0
        
        for body, vector in zip(self.bodies, self.vectors):
            body.reset()
            vector.reset()
        
        if len(self.sliders) == 2:
            for slider in self.sliders:
                slider.reset()
        
        self.calc_gravity_center()
        
        self.selected_body = None
        self.following_com_state = False
        self.timewarp = 1
        self.zoom = 1
               
    def get_real_mass(self, body):
        if body.mass_unit == 'sun':
            return body.mass_multiplier * self.M_sun
        if body.mass_unit == 'earth':
            return body.mass_multiplier * self.M_earth
        if body.mass_unit == 'moon':
            return body.mass_multiplier * self.M_moon
    
class Body:
    def __init__(self, x, y, m, r, game):
        self.game = game
        
        self.start_x = x
        self.start_y = y
        self.start_m = m
        self.start_r = r
        
        self.x = x
        self.y = y
        self.m = m
        self.r = r
        
        self.vx = self.vy = self.ax = self.ay = 0
        self.trail = []
        self.dragging = False
        
        self.mass_multiplier = 10
        self.mass_unit = 'earth'  
        self.color = self.game.planet_colors[0]
        
    def reset(self):
        self.x = self.start_x
        self.y = self.start_y

        self.vx = self.vy = self.ax = self.ay = 0
        self.trail.clear()
        
    def calc_acceleration(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        r = (dx**2+dy**2)**0.5
        if r < 0.1:
            return 0, 0
        
        ax = -self.game.G_scaled * other.m * dx / r**3
        ay = -self.game.G_scaled * other.m * dy / r**3
        return ax, ay   
        
class Slider:
    def __init__(self, x, y, attribute, min_value, max_value):
        self.x = x
        self.y = y
        self.attribute = attribute
        self.max_value = max_value
        self.min_value = min_value
        self.color = pygame.Color('#c1c9d6')
        self.width = 300
        self.height = 2
        self.x_ball = x + self.width * ((attribute - min_value) / (max_value - min_value))
        self.y_ball = 851
        self.r_ball = 4
        self.color_ball = pygame.Color("#d17777")
        self.dragging = False
        
    def draw(self, screen):
        pygame.draw.rect(screen, (self.color), (self.x, self.y, self.width, self.height))
        pygame.draw.circle(screen, (self.color_ball), (self.x_ball, self.y_ball), self.r_ball)
        
    def update(self, mx):
        mx_clamped = max(self.x, min(mx, self.x + self.width))
        self.x_ball = mx_clamped
        value = (self.x_ball - self.x) / self.width * (self.max_value - self.min_value) + self.min_value
        return value
    
    def calc_val(self):
        val = (self.x_ball - self.x) / self.width * (self.max_value - self.min_value) + self.min_value
        return val

    def reset(self):
        self.x_ball = self.x + self.width * (self.attribute/self.max_value)
            
class Button:
    def __init__(self, x, y, width, height, color, text, font):
        self.rect = pygame.Rect(x,y,width,height)
        self.color = color
        self.font = font
        self.surface = self.font.render(text, True, (255, 255, 255))
        self.text_rect = self.surface.get_rect(center=self.rect.center)
        self.border_radius = 8
        
    def draw(self, screen):
        pygame.draw.rect(screen, (self.color), self.rect, border_radius=self.border_radius)
        screen.blit(self.surface, self.text_rect)  # rysowanie tekstu
    
    def set_text(self, text):
        self.surface = self.font.render(text, True, (255, 255, 255))
        self.text_rect = self.surface.get_rect(center=self.rect.center)
               
class ButtonGlow(Button):
    def __init__(self, button):
        margin = 2
        super().__init__(
            x = button.rect.x - margin,
            y = button.rect.y - margin,
            width = button.rect.width + margin * 2,
            height = button.rect.height + margin * 2,
            color = "#c8d0d8",
            text = '',
            font = pygame.font.SysFont(None, 1)
        )

class Picker:
    def __init__(self,x,y,size,body_type):        
        self.x = x
        self.y = y
        self.size = size
        self.body_type = body_type
        self.picker = []
        
    def picker_buttons(self, game):
        self.picker = []
        if self.body_type == 'star':
            for i, star_color in enumerate(game.star_colors):
                self.picker.append(Button(x = self.x + i * self.size, y = self.y, width = self.size, height = self.size, color = star_color, text='', font =game.fonts['font2']))
        elif self.body_type == 'planet':
            for i, planet_color in enumerate(game.planet_colors):
                self.picker.append(Button(x = self.x + i * self.size, y = self.y, width = self.size, height = self.size, color = planet_color, text='', font =game.fonts['font2']))
        elif self.body_type == 'moon':
            for i, moon_color in enumerate(game.moon_colors):
                self.picker.append(Button(x = self.x + i * self.size, y = self.y, width = self.size, height = self.size, color = moon_color, text='', font =game.fonts['font2']))
                
    def draw_picker(self, screen):
        for i in self.picker:
            i.border_radius = 0
            i.draw(screen)
                
class Vector:
    def __init__(self, body, game):
        self.game = game
        self.dx = self.dy = self.v = 0
        self.body = body
        self.dragging = False

    def update(self, mx, my):
        self.dx = mx - (self.body.x - self.game.cam_x) * self.game.zoom
        self.dy = my - (self.body.y - self.game.cam_y) * self.game.zoom
        self.body.vx = (mx / self.game.zoom + self.game.cam_x - self.body.x) * 0.008
        self.body.vy = (my / self.game.zoom + self.game.cam_y - self.body.y) * 0.008

        self.v = math.sqrt(self.body.vx**2 + self.body.vy**2)
        
        if self.v > 10:
            self.body.vx *= 10 / self.v
            self.body.vy *= 10 / self.v
        
    def draw(self, screen, fonts):
        screen_dx = self.body.vx / 0.008 * self.game.zoom
        screen_dy = self.body.vy / 0.008 * self.game.zoom
        
        screen_x = (self.body.x - self.game.cam_x) * self.game.zoom
        screen_y = (self.body.y - self.game.cam_y) * self.game.zoom
        
        start = (screen_x, screen_y)
        end = (screen_x + screen_dx, screen_y + screen_dy)
        pygame.draw.line(screen, (100, 83, 12), start, end, 2)
        self.surface = fonts['font2'].render(f"{self.v:.2f}", True, (255,255,255))
        screen.blit(self.surface, (end[0]+20, end[1]+20))
        
    def reset(self):
        self.dx = self.dy = self.v = 0

class Collision:
    def __init__(self, body1, body2, game):
        
        self.game = game
        self.body1 = body1
        self.body2 = body2
        
        self.core_body = self.body1 if self.body1.m > self.body2.m else self.body2
        self.other_body = self.body1 if self.core_body == self.body2 else self.body2
        
        self.collision_multiplier = self.other_body.m / self.core_body.m
        
    def momentum(self):
        new_vx  = (self.core_body.m * self.core_body.vx + self.other_body.m * self.other_body.vx) / (self.core_body.m + self.other_body.m)
        new_vy  = (self.core_body.m * self.core_body.vy + self.other_body.m * self.other_body.vy) / (self.core_body.m + self.other_body.m)
        
        self.core_body.m += self.other_body.m
        self.core_body.r += self.collision_multiplier * self.other_body.r       
        self.core_body.vx = new_vx
        self.core_body.vy = new_vy
        
        i = self.game.bodies.index(self.other_body)
        self.game.bodies.remove(self.other_body)
        self.game.vectors.pop(i)

    def change_color(self):
        mass_ratio = self.core_body / self.other_body
        

game = Game()

def draw_text(text, fonts, x, y):
    surface = fonts['font2'].render(text, True, (255,255,255))
    game.screen.blit(surface, (x, y))

def onclicked(mx, my, x, y):
    dx = mx - x
    dy = my - y
    distance = math.sqrt(dx**2 + dy**2)
    return distance

while game.running:
    for event in pygame.event.get():    
        
        if event.type == pygame.QUIT:
            game.running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            mouse_pos = mx, my
            
            if game.state == 'start':    
                game.handle_start_events(event)
                continue
                    
            if game.state == 'simulation':
                game.handle_sim_events(event)
        
        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                scroll = 'up'
            if event.y < 0:
                scroll = 'down'
            game.handle_zoom(scroll)
            
        if event.type == pygame.MOUSEBUTTONUP:
            for body, vector in zip(game.bodies, game.vectors):
                body.dragging = False
                vector.dragging = False
                for slider in game.sliders:
                    slider.dragging = False
                    
                    
                    
    #################################    START    #################################
    
    if game.state == 'start':
        
        game.update_start()
        
        game.screen.fill(game.background_color)
        
        game.draw_grid()
        
        game.draw_start()
        
        game.cam()
         
    #################################    SIMULATION    #################################
    
    if game.state == 'simulation':
        
        game.handle_timewarp()
        
        game.update_simulation()
        
        game.screen.fill(game.background_color)
            
        game.draw_grid()
            
        game.draw_simulation() 
        
        game.cam()

        
    pygame.display.flip()
    game.clock.tick(600) 
    

#### KOLIZJE - dorobić wizualny efekt kolizji

