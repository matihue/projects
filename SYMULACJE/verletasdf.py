import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.widgets as widgets
import math

### WŁAŚCIWOŚCI SYMULACJI
base_dt = 0.00001          
frame_time = 0.01
epsilon = 0.0002

### PIERWSZE CIAŁO
x1 = 2
y1 = 3
vx1 = 0
vy1 = 0
m1 = 1
r1 = 5

### DRUGIE CIAŁO
x2 = 7
y2 = 5
vx2 = 0
vy2 = 0
m2 = 4
r2 = 5

### SYMULACJA Z ZACHOWANYM ŚRODKIEM CIĘZKOŚCI
#vx2 = - (m1/m2) * vx1
#vy2 =  - (m1/m2) * vy1

fig, xx = plt.subplots()
xx.set_xlim(0, 10)
xx.set_ylim(0, 10)
xx.grid(True, linestyle='--', alpha=0.3)
xx.set_facecolor('k')  # czarne tło = kosmos

line1, = xx.plot([],[], 'g:')
line2, = xx.plot([],[], 'b:')
body1, = xx.plot([x1],[y1], 'ro', markersize = r1)
body2, = xx.plot([x2],[y2], 'yo', markersize = r2)
gravitycenter, = xx.plot([],[], color='white', marker='+', markersize='3')

speed_text = xx.text(0.02, 0.95, '', transform=xx.transAxes, color = 'white')
energy_text = xx.text(0.02, 0.90, '', transform=xx.transAxes, color = 'white')

x1data, y1data = [], []
x2data, y2data = [], []

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

        
E0 = calc_energy(vx1,vy1,vx2,vy2)
ax1, ay1 = calc_ax_ay(x1, y1, x2, y2, m2)
ax2, ay2 = calc_ax_ay(x2, y2, x1, y1, m1)
zderzenie = False

def verlet(frame):
    
    global vx1, vy1, vx2, vy2, x1, y1, x2, y2, m1, m2, r1, r2, ax1, ay1, ax2, ay2, zderzenie, epsilon
    time_acc = 0
    
    if zderzenie:
        return
    
    while time_acc < frame_time:
        r = math.sqrt((x1-x2)**2 + (y1-y2)**2 + epsilon**2)
        if r < 0.01:
            zderzenie = True
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
        print(round(error, 2))
        
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
        
ani = animation.FuncAnimation(fig, verlet, frames=10000, interval=0.1, blit=False)
plt.show()


        
        
        