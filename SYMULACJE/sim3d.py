import pygame
import math
pygame.init()

screen = pygame.display.set_mode((1500, 900))
clock = pygame.time.Clock()



game = {
    'running': True,
    'state': 'start',
    
    'growing': True,
    'dragging': None,
    
    'trail1': [],
    'trail2': [],
    
    'cam_x': 0,
    'cam_y': 0,
    'cam_speed': 2,
    
    'dt': 0.1,
    'scale': 0.008,
    
    'grid_size': 50
}

body1 = {
    'x': 100,
    'y': 100,
    'r': 10,
    'm': 5,
    'vx': 0,
    'vy': 0,
    'v': 0,
    'ax': 0,
    'ay': 0
}
body2 = {
    'x': 100,
    'y': 200,
    'r': 10,
    'm': 5,
    'vx': 0,
    'vy': 0,
    'v': 0,
    'ax': 0,
    'ay': 0
}
vectors = {
    "dx1": 0,
    "dy1": 0,
    "dx2": 0,
    "dy2": 0,
    "v1": 0,
    "v2": 0
}
collision = {
    'scale': 1,
    'inner_radius': 0,
    'outer_radius': 0,
    'main_radius': 1,    
    'growing': True
}
sliders = {
    'mass1' : pygame.Rect(40, 850, 200, 2),
    'mass2' : pygame.Rect(280, 850, 200, 2),
    'radius1' : pygame.Rect(520, 850, 200, 2),
    'radius2' : pygame.Rect(760, 850, 200, 2),
    
    'mass1_ball' : {'x': 40 + body1['m']/10 * 200, 'y': 851, 'r': 4},
    'mass2_ball' : {'x': 280 + body2['m']/10 * 200, 'y': 851, 'r': 4},
    'radius1_ball' : {'x': 520 + body1['r']/20 * 200, 'y': 851, 'r': 4},
    'radius2_ball' : {'x': 760 + body2['r']/20 * 200, 'y': 851, 'r': 4},
    
    'slider_color' : pygame.Color('#c1c9d6'),
    'ball_color' : pygame.Color("#d17777")
}
buttons = {
    'button1_rect': pygame.Rect(1300, 800, 180, 80),
    'button2_rect': pygame.Rect(1300, 800, 180, 80),
    'button1_col': pygame.Color("#3174DF"),
    'button2_col': pygame.Color("#296dda")
}
fonts = {
    'font1': pygame.font.SysFont(None, 60),
    'font2': pygame.font.SysFont('segoe ui', 18)
}
text = {
    'start_text': fonts['font1'].render("Start", True, (255, 255, 255)),
    'start_rect': None,
    'back_text': fonts['font1'].render("Powrót", True, (255, 255, 255)),
    'back_rect': None
}
text['start_rect'] = text['start_text'].get_rect(center=(1390, 840))
text['back_rect'] = text['back_text'].get_rect(center=(1390, 840))

def calc_ax_ay(x1, y1, x2, y2, m2):
    dx = x1 - x2
    dy = y1 - y2
    r = (dx**2 + dy**2)**0.5
    ax = -m2 * dx / r**3
    ay = -m2 * dy / r**3
    return ax, ay

def draw_text(text, fonts, x, y):
    surface = fonts['font2'].render(text, True, (255,255,255))
    screen.blit(surface, (x, y))

def onclicked(mx,my,x,y):
    dx = mx - x
    dy = my - y
    distance = math.sqrt(dx**2 + dy**2)
    return distance
    
def handle_start_events(event, mouse_pos, body1, body2, dragging):
    
    x1, x2 = body1['x'], body2['x']
    y1, y2 = body1['y'], body2['y']
    r1, r2 = body1['r'], body2['r']
    mx, my = mouse_pos
    
        
    if event.button == 1:    
        distance1 = onclicked(mx,my,x1,y1)
        distance2 = onclicked(mx,my,x2,y2)
        if distance1 < r1:
            dragging = 'body1'
        elif distance2 < r2:
            dragging = 'body2'
                                
        distance = onclicked(mx,my,sliders['mass1_ball']['x'],sliders['mass1_ball']['y'])
        if distance < sliders['mass1_ball']['r']:
            dragging = 'sm1ball'
        distance = onclicked(mx,my,sliders['mass2_ball']['x'],sliders['mass2_ball']['y'])
        if distance < sliders['mass2_ball']['r']:
            dragging = 'sm2ball'
        distance = onclicked(mx,my,sliders['radius1_ball']['x'],sliders['radius1_ball']['y'])
        if distance < sliders['radius1_ball']['r']:
            dragging = 'sv1ball'
        distance = onclicked(mx,my,sliders['radius2_ball']['x'],sliders['radius2_ball']['y'])
        if distance < sliders['radius2_ball']['r']:
            dragging = 'sv2ball'
                            
    if event.button == 3:
        distance1 = onclicked(mx,my,x1,y1)
        distance2 = onclicked(mx,my,x2,y2)
        if distance1 < r1:
            dragging = 'vector1'
        elif distance2 < r2:
            dragging = 'vector2'    
    
    return dragging
    
def update_start(body1, body2, sliders, vectors, scale, dragging):
    
    if dragging == 'vector1':
            mx, my = pygame.mouse.get_pos()            
            vectors['dx1'] = mx - body1['x']
            vectors['dy1'] = my - body1['y']
            body1['vx'] = vectors['dx1'] * scale
            body1['vy'] = vectors['dy1'] * scale
            vectors['v1'] = math.sqrt(body1['vx']**2 + body1['vy']**2)
            if vectors['v1'] > 10:
                body1['vx'] *= 10 / vectors['v1']
                body1['vy'] *= 10 / vectors['v1']
        
    if dragging == 'vector2':
            mx, my = pygame.mouse.get_pos()
            vectors['dx2'] = mx - body2['x']
            vectors['dy2'] = my - body2['y']
            body2['vx'] = vectors['dx2'] * scale
            body2['vy'] = vectors['dy2'] * scale
            vectors['v2'] = math.sqrt(body2['vx']**2 + body2['vy']**2)
            if vectors['v2'] > 10:
                body2['vx'] *= 10 / vectors['v2']
                body2['vy'] *= 10 / vectors['v2']

    if dragging == 'sm1ball':
            mx, my = pygame.mouse.get_pos()
            if 40 <= mx <= 240:
                sliders['mass1_ball']['x'] = mx
                body1['m'] = (sliders['mass1_ball']['x'] - 40)/200*10
            
    if dragging == 'sm2ball':
            mx, my = pygame.mouse.get_pos()
            if 280 <= mx <= 480:
                sliders['mass2_ball']['x'] = mx
                body2['m'] = (sliders['mass2_ball']['x'] - 280)/200*10
            
    if dragging == 'sv1ball':
            mx, my = pygame.mouse.get_pos()
            if 520 <= mx <= 720:
                sliders['radius1_ball']['x'] = mx
                body1['r'] = (sliders['radius1_ball']['x'] - 520)/200*20
            
    if dragging == 'sv2ball':
            mx, my = pygame.mouse.get_pos()
            if 760 <= mx <= 960:
                sliders['radius2_ball']['x'] = mx
                body2['r'] = (sliders['radius2_ball']['x'] - 760)/200*20
        
    if dragging == 'body1':
            mx, my = pygame.mouse.get_pos()
            body1['x'] = mx
            body1['y'] = my
        
    if dragging == 'body2':
            mx, my = pygame.mouse.get_pos()
            body2['x'] = mx
            body2['y'] = my
    
def draw_start(screen, body1, body2, sliders, vectors, buttons, fonts, text):
        
        pygame.draw.circle(screen, (0, 0, 255), (int(body1['x']), int(body1['y'])), body1['r'])
        pygame.draw.circle(screen, (255, 0, 0), (int(body2['x']), int(body2['y'])), body2['r'])
        pygame.draw.rect(screen, (buttons['button1_col']), buttons['button1_rect'])
        screen.blit(text['start_text'], text['start_rect'])  # rysowanie tekstu
        
        pygame.draw.rect(screen, (sliders['slider_color']), sliders['mass1'])
        pygame.draw.rect(screen, (sliders['slider_color']), sliders['mass2'])
        pygame.draw.rect(screen, (sliders['slider_color']), sliders['radius1'])
        pygame.draw.rect(screen, (sliders['slider_color']), sliders['radius2'])
        
        pygame.draw.circle(screen, (sliders['ball_color']), (sliders['mass1_ball']['x'], sliders['mass1_ball']['y']), sliders['mass1_ball']['r'])
        pygame.draw.circle(screen, (sliders['ball_color']), (sliders['mass2_ball']['x'], sliders['mass2_ball']['y']), sliders['mass2_ball']['r'])
        pygame.draw.circle(screen, (sliders['ball_color']), (sliders['radius1_ball']['x'], sliders['radius1_ball']['y']), sliders['radius1_ball']['r'])
        pygame.draw.circle(screen, (sliders['ball_color']), (sliders['radius2_ball']['x'], sliders['radius2_ball']['y']), sliders['radius2_ball']['r'])
        
        draw_text(f'Masa 1 ciała: {body1['m']:.2f}', fonts, 40, 820)
        draw_text(f'Masa 2 ciała: {body2['m']:.2f}', fonts, 280, 820)
        draw_text(f'Rozmiar 1 ciała: {body1['r']:.2f}', fonts, 520, 820)
        draw_text(f'Rozmiar 2 ciała: {body2['r']:.2f}', fonts, 760, 820)
            
        start1 = (body1['x'], body1['y'])
        end1 = (body1['x'] + vectors['dx1'], body1['y'] + vectors['dy1'])
        start2 = (body2['x'], body2['y'])
        end2 = (body2['x'] + vectors['dx2'], body2['y'] + vectors['dy2'])
        
        pygame.draw.line(screen, (100, 83, 12), start1, end1, 2)
        pygame.draw.line(screen, (100, 83, 12), start2, end2, 2)
        draw_text(f"{vectors['v1']:.2f}", fonts, end1[0]+20, end1[1]+20)
        draw_text(f"{vectors['v2']:.2f}", fonts, end2[0]+20, end2[1]+20)
           
def cam(cam_x,cam_y,speed):
    
    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        cam_x -= speed
    if keys[pygame.K_d]:
        cam_x += speed
    if keys[pygame.K_w]:
        cam_y -= speed
    if keys[pygame.K_s]:
        cam_y += speed
    
    return cam_x, cam_y

def reset_to_start(game, body1, body2, sliders ,vectors, collision):
    
    game["state"], game['cam_x'], game['cam_y'] = 'start', 0, 0
    game["trail1"].clear(), game["trail2"].clear()
    
    body1['x'], body1['y'], body1['m'], body1['vx'], body1['vy'], body1['r'] = 100, 100, 5, 0, 0, 10
    body2['x'], body2['y'], body2['m'], body2['vx'], body2['vy'], body2['r']  = 100, 200, 5, 0, 0, 10
    
    sliders['mass1_ball']['x'] = 40 + body1['m']/10 * 200
    sliders['mass2_ball']['x'] = 280 + body2['m']/10 * 200
    sliders['radius1_ball']['x'] = 520 + body1['r']/20 * 200
    sliders['radius2_ball']['x'] = 760 + body2['r']/20 * 200
    
    collision['scale'], collision['inner_radius'], collision['outer_radius'], collision['main_radius'], collision['growing'] = 1, 0, 0, 1, True
    
    for i in vectors: vectors[i] = 0
     
def simulation(game, body1, body2):
    for _ in range(10): 
            #################################    CIAŁO 1    #################################

            x1_new = body1['x'] + body1['vx']*game['dt'] + 0.5*body1['ax']*game['dt']**2 
            y1_new = body1['y'] + body1['vy']*game['dt'] + 0.5*body1['ay']*game['dt']**2
                
            ax1_new, ay1_new = calc_ax_ay(x1_new, y1_new, body2['x'], body2['y'], body2['m'])

            body1['vx'] += 0.5*(body1['ax'] + ax1_new)*game['dt']
            body1['vy'] += 0.5*(body1['ay'] + ay1_new)*game['dt']
                
            body1['x'],body1['y'] = x1_new, y1_new
            body1['ax'], body1['ay'] = ax1_new, ay1_new

            #################################    CIAŁO 2    #################################
            
            x2_new = body2['x'] + body2['vx']*game['dt'] + 0.5*body2['ax']*game['dt']**2
            y2_new = body2['y'] + body2['vy']*game['dt'] + 0.5*body2['ay']*game['dt']**2
                
            ax2_new, ay2_new = calc_ax_ay(x2_new, y2_new, body1['x'], body1['y'], body1['m'])
                
            body2['vx'] += 0.5*(body2['ax'] + ax2_new)*game['dt']
            body2['vy'] += 0.5*(body2['ay'] + ay2_new)*game['dt']
                
            body2['x'],body2['y'] = x2_new, y2_new
            body2['ax'], body2['ay'] = ax2_new, ay2_new
            
            #################################    ŚRODEK CIĘŻKOŚCI    #################################
            
            gcx = (body1['m'] * body1['x'] + body2['m'] * body2['x']) / (body1['m'] + body2['m'])
            gcy = (body1['m'] * body1['y'] + body2['m'] * body2['y']) / (body1['m'] + body2['m'])
            
            #################################    ZDERZENIE     #################################
            
            distance = math.sqrt((body1['x']-body2['x'])**2 + (body1['y']-body2['y'])**2)
            
            if distance < body1['r'] + body2['r']:
                game['state'] = 'collision'
            
            #################################    TRAIL    #################################
            
            game['trail1'].append((int(body1['x']), int(body1['y'])))
            game['trail2'].append((int(body2['x']), int(body2['y'])))
            
    return gcx, gcy
    
def draw_simulation(body1, body2, game, gcx, gcy, buttons, text):
    
    screen_x1 = body1['x'] - game['cam_x'] 
    screen_y1 = body1['y'] - game['cam_y'] 
        
    screen_x2 = body2['x'] - game['cam_x'] 
    screen_y2 = body2['y'] - game['cam_y']
        
    screen_gcx = gcx - game['cam_x'] 
    screen_gcy = gcy - game['cam_y']
        
    trail1_screen = [(x - game['cam_x'] , y - game['cam_y'] ) for x, y in game['trail1']]
    trail2_screen = [(x - game['cam_x'] , y - game['cam_y'] ) for x, y in game['trail2']]
          
    if len(game['trail1']) > 1:
        pygame.draw.lines(screen, (0, 255, 0), False, trail1_screen, 2)
    if len(game['trail2']) > 1:
        pygame.draw.lines(screen, (0, 255, 0), False, trail2_screen, 2)

    pygame.draw.circle(screen, (0, 0, 255), (int(screen_x1), int(screen_y1)), body1['r'])
    pygame.draw.circle(screen, (255, 0, 0), (int(screen_x2), int(screen_y2)), body2['r'])
    pygame.draw.circle(screen, (255, 0, 0), (int(screen_gcx), int(screen_gcy)), 3)
    
    pygame.draw.rect(screen, (buttons['button2_col']), buttons['button2_rect'])
    screen.blit(text['back_text'], text['back_rect'])  # rysowanie tekstu

def collisions(game, collision):

    if collision['growing']:
        collision['main_radius'] += collision['scale']**3
        collision['scale'] -= 0.001
        if collision['scale'] <= 0.0001:
            collision['growing'] = False
    else:
        collision['main_radius'] -= collision['scale']**3
        collision['scale'] += 0.0001
        if collision['main_radius'] <= 5:
            collision['main_radius'] = 5
            collision['inner_radius'] += 0.01
            if collision['inner_radius'] > 13:
                collision['inner_radius'] = 13
                collision['outer_radius'] += 0.08
                if collision['outer_radius'] > 15:
                    collision['outer_radius'] = 15

def draw_collisions(game, collision, body1, buttons, text):
    
    pos_x = body1['x'] - game['cam_x']
    pos_y = body1['y'] - game['cam_y']
        
    pygame.draw.circle(screen, (232, 251, 243),  (int(pos_x), int(pos_y)) , int(collision['outer_radius']))
    pygame.draw.circle(screen, (255, 12, 0), (int(pos_x), int(pos_y)) , int(collision['inner_radius']))
    pygame.draw.circle(screen, (255, 102, 0), (int(pos_x), int(pos_y)) , int(collision['main_radius']))
    
    pygame.draw.rect(screen, (buttons['button2_col']), buttons['button2_rect'])
    screen.blit(text['back_text'], text['back_rect'])  # rysowanie tekstu
    
def draw_grid(screen, game):
    
    for x in range(-game['cam_x'] % game['grid_size'], 1500, game['grid_size']):
        pygame.draw.line(screen, (33,33,33), (x,0), (x,900), 1)
            
    for y in range(-game['cam_y'] % game['grid_size'], 900, game['grid_size']):
        pygame.draw.line(screen, (33,33,33), (0,y), (1500,y), 1) 


while game['running']:
    for event in pygame.event.get():    
        
        if event.type == pygame.QUIT:
            game['running'] = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            mouse_pos = mx, my
            
            if game['state'] == 'start':    
                game['dragging'] = handle_start_events(event, mouse_pos, body1, body2, game['dragging'])
                
            if game['state'] == 'start' and buttons['button1_rect'].collidepoint(mx, my):
                game['state'] = 'simulation'
                continue
                    
            if game['state'] in ['simulation', 'collision'] and buttons['button2_rect'].collidepoint(mx, my):
                reset_to_start(game, body1, body2, sliders, vectors, collision)
                game['state'] = 'start'
                continue   
                
        if event.type == pygame.MOUSEBUTTONUP:
                button = None
                game['dragging'] = None
                
    if game['state'] == 'simulation' or game['state'] == 'collision':
        game['cam_x'], game['cam_y'] = cam(game['cam_x'],game['cam_y'],game['cam_speed'])
        
    #################################    START    #################################
    
    if game['state'] == 'start':
        
        update_start(body1, body2, sliders, vectors, game['scale'], game['dragging'])
        
        screen.fill((0, 0, 0))
        
        draw_grid(screen, game)
        
        draw_start(screen, body1, body2, sliders, vectors, buttons, fonts, text)
         
    #################################    SYMULACJA    #################################
    
    if game['state'] == 'simulation':
        
        gcx, gcy = simulation(game, body1, body2)
        
        screen.fill((0, 0, 0))
            
        draw_grid(screen, game)    
            
        draw_simulation(body1, body2, game, gcx, gcy, buttons, text)    
        
    #################################    KOLIZJA    #################################
    
    if game['state'] == 'collision':  
        
        collisions(game, collision)
        
        screen.fill((0, 0, 0))
        
        draw_grid(screen, game)
        
        draw_collisions(game, collision, body1, buttons, text)
        
        
    pygame.display.flip()
    clock.tick(600)