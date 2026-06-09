import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.widgets as widgets
import math

### WŁAŚCIWOŚCI SYMULACJI
base_dt = 0.00001          
frame_time = 0.01
epsilon = 0.0002
r1 = 5
r2 = 5
rboom = 0
ani = None
zderzenie = False
animation_started = False

fig, xx = plt.subplots()
plt.subplots_adjust(bottom=0.3) 
xx.set_visible(False)
xx.set_xlim(0, 10)
xx.set_ylim(0, 10)
xx.grid(True, linestyle='--', alpha=0.3)
xx.set_facecolor('k')  # czarne tło = kosmos


ui_x1 = plt.axes([0.2,0.85,0.6,0.03])        
ui_y1 = plt.axes([0.2,0.80,0.6,0.03])
slider_x1 = widgets.Slider(ui_x1, 'x1', 0, 10, valinit =2)
slider_y1 = widgets.Slider(ui_y1, 'y1', 0, 10, valinit =2)

ui_x2 = plt.axes([0.2,0.75,0.6,0.03])        
ui_y2 = plt.axes([0.2,0.70,0.6,0.03])
slider_x2 = widgets.Slider(ui_x2, 'x2', 0, 10, valinit =4)
slider_y2 = widgets.Slider(ui_y2, 'y2', 0, 10, valinit =4)


ui_v1 = plt.axes([0.2,0.60,0.6,0.03])        
ui_angle1= plt.axes([0.2,0.55,0.6,0.03])
slider_v1 = widgets.Slider(ui_v1, 'v1', 0, 3, valinit =0)
slider_angle1 = widgets.Slider(ui_angle1, 'angle1', 0, 360, valinit =0)

ui_v2 = plt.axes([0.2,0.50,0.6,0.03])        
ui_angle2 = plt.axes([0.2,0.45,0.6,0.03])
slider_v2 = widgets.Slider(ui_v2, 'v2', 0, 3, valinit =0)
slider_angle2 = widgets.Slider(ui_angle2, 'angle2', 0, 360, valinit =0)


ui_m1 = plt.axes([0.2,0.35,0.6,0.03])  
slider_m1 = widgets.Slider(ui_m1, 'm1', 0, 10, valinit =1)
      
ui_m2 = plt.axes([0.2,0.30,0.6,0.03])
slider_m2 = widgets.Slider(ui_m2, 'm2', 0, 10, valinit =1)

ui_button1 = plt.axes([0.4, 0.16, 0.2, 0.05])
confirm_button = widgets.Button(ui_button1, 'Start')

ui_button2 = plt.axes([2, 2, 0.2, 0.05])
reset_button = widgets.Button(ui_button2, 'Reset symulacji')
ui_button2.set_visible(False)



line1, = xx.plot([],[], 'g:')
line2, = xx.plot([],[], 'b:')
body1, = xx.plot([],[], 'ro', markersize = r1)
body2, = xx.plot([],[], 'yo', markersize = r2)
boom, = xx.plot([],[], 'o', color = 'orange', markersize = r2)
gravitycenter, = xx.plot([],[], color='white', marker='+', markersize='3')

speed_text = xx.text(0.02, 0.95, '', transform=xx.transAxes, color = 'white')
energy_text = xx.text(0.02, 0.90, '', transform=xx.transAxes, color = 'white')

x1data, y1data = [], []
x2data, y2data = [], []


def reset(event=None):
    global animation_started, zderzenie, rboom, line1, line2, ani
    if ani:
        ani.event_source.stop()
        ani = None
    
    animation_started = False
    zderzenie = False
    rboom = 0
    
    x1data.clear()
    y1data.clear()
    x2data.clear()
    y2data.clear()
    
    xx.set_visible(False)
    
    ui_button2.set_visible(False)
    ui_button2.set_position([2, 2, 0.2, 0.05])
    
    ui_button1.set_visible(True)
    ui_button1.set_position([0.4, 0.16, 0.2, 0.05])
    
    ui_x1.set_visible(True)
    ui_y1.set_visible(True)
    ui_x2.set_visible(True)
    ui_y2.set_visible(True)
    ui_v1.set_visible(True)
    ui_angle1.set_visible(True)
    ui_v2.set_visible(True)
    ui_angle2.set_visible(True)
    ui_m1.set_visible(True)
    ui_m2.set_visible(True)

    line1.set_data([],[])
    line2.set_data([],[])
    boom.set_data([], [])
    boom.set_alpha(1)

    fig.canvas.draw_idle()

def calc_ax_ay(x1, y1, x2, y2, m2):
    dx = x1 - x2
    dy = y1 - y2
    r = (dx**2 + dy**2)**0.5
    ax = -m2 * dx / r**3
    ay = -m2 * dy / r**3
    return ax, ay

def calc_energy(vx1,vy1,vx2,vy2):
    v1 = math.sqrt(vx1**2 + vy1**2)
    v2 = math.sqrt(vx2**2 + vy2**2)
    r = math.sqrt((x1-x2)**2 + (y1-y2)**2 + 1e-4)
    E = 0.5 * (m1 * v1**2) + 0.5 * (m2 * v2**2) - (m1 * m2) / r
    return E

def verlet(frame):
    
    global vx1, vy1, vx2, vy2, x1, y1, x2, y2, m1, m2, r1, r2, ax1, ay1, ax2, ay2, zderzenie, epsilon, rboom, animation_started, cid
    time_acc = 0

    if zderzenie:
        if rboom >= 30:
            ani.event_source.stop()
            reset()
            return
        rboom += 0.1
        boom.set_markersize(rboom)
        boom.set_alpha(1-rboom/31)     
        return
    
    while time_acc < frame_time:
        r = math.sqrt((x1-x2)**2 + (y1-y2)**2 + epsilon**2)
        if r < 0.01:
            zderzenie = True
            boom.set_data([x1],[y1])
            return
        
        dt = base_dt * r
        
        #######ciało 1
        x1_new = x1 + vx1*dt + 0.5*ax1*dt**2
        y1_new = y1 + vy1*dt + 0.5*ay1*dt**2
        
        ax1_new, ay1_new = calc_ax_ay(x1_new, y1_new, x2, y2, m2)

        vx1 += 0.5*(ax1 + ax1_new)*dt
        vy1 += 0.5*(ay1 + ay1_new)*dt
        
        x1,y1 = x1_new, y1_new
        ax1, ay1 = ax1_new, ay1_new

        #######ciało 2
        x2_new = x2 + vx2*dt + 0.5*ax2*dt**2
        y2_new = y2 + vy2*dt + 0.5*ay2*dt**2
        
        ax2_new, ay2_new = calc_ax_ay(x2_new, y2_new, x1, y1, m1)
        
        vx2 += 0.5*(ax2 + ax2_new)*dt
        vy2 += 0.5*(ay2 + ay2_new)*dt
        
        x2,y2 = x2_new, y2_new
        ax2, ay2 = ax2_new, ay2_new
        
        
        
        ### zderzenie i energia
        r = math.sqrt((x1-x2)**2 + (y1-y2)**2)
        if r < 0.01:
            break

        E = calc_energy(vx1,vy1,vx2,vy2)
        error = (E - E0) / E0
        #print(round(error, 2))
        
        v1 = (vx1**2 + vy1**2)**0.5
        v2 = (vx2**2 + vy2**2)**0.5

        speed_text.set_text(f'v1={v1:.2f}, v2={v2:.2f}')
        energy_text.set_text(f'E={E:.3f}')
        
        time_acc += dt

    gcx = (m1 * x1 + m2 * x2) / (m1 + m2)
    gcy = (m1 * y1 + m2 * y2) / (m1 + m2)

    x1data.append(x1)
    y1data.append(y1)
    x2data.append(x2)
    y2data.append(y2)
        
    line1.set_data(x1data, y1data)
    line2.set_data(x2data, y2data)
    gravitycenter.set_data([gcx], [gcy])
    body1.set_data([x1],[y1])
    body2.set_data([x2],[y2])
    
    return body1, body2, gravitycenter, line1, line2, speed_text, energy_text

def start_sim(event):
    
    global ani, animation_started, x1, y1, vx1, vy1, m1, x2, y2, vx2, vy2, m2, ax1, ax2, ay1, ay2, E0
    
    if animation_started:
        return

    x1 = slider_x1.val
    y1 = slider_y1.val
    v1 = slider_v1.val
    angle1 = slider_angle1.val
    theta1 = math.radians(angle1)
    vx1 = v1 * math.cos(theta1)
    vy1 = v1 * math.sin(theta1)
    m1 = slider_m1.val

    x2 = slider_x2.val
    y2 = slider_y2.val
    v2 = slider_v2.val
    angle2 = slider_angle2.val
    theta2 = math.radians(angle2)
    vx2 = v2 * math.cos(theta2)
    vy2 = v2 * math.sin(theta2)
    m2 = slider_m2.val
    
    E0 = calc_energy(vx1,vy1,vx2,vy2)
    ax1, ay1 = calc_ax_ay(x1, y1, x2, y2, m2)
    ax2, ay2 = calc_ax_ay(x2, y2, x1, y1, m1)

    xx.set_visible(True)
    
    ui_button2.set_visible(True)
    ui_button2.set_position([0.4, 0.16, 0.2, 0.05])

    ui_button1.set_visible(False)
    ui_button1.set_position([2, 2, 0.2, 0.05])
    
    ui_x1.set_visible(False)
    ui_y1.set_visible(False)
    ui_x2.set_visible(False)
    ui_y2.set_visible(False)
    ui_v1.set_visible(False)
    ui_angle1.set_visible(False)
    ui_v2.set_visible(False)
    ui_angle2.set_visible(False)
    ui_m1.set_visible(False)
    ui_m2.set_visible(False)

    ani = animation.FuncAnimation(fig, verlet, frames=10000, interval=0.1, blit=False)
    animation_started = True
    
    fig.canvas.draw_idle()
    
confirm_button.on_clicked(start_sim)
reset_button.on_clicked(reset)

plt.show()


        
        
        