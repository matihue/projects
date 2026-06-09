import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math

angle = 25
v = 100
dt = 0.01
g = 9.81

x = 0
y = 0
vx = v * math.cos(math.radians(angle))
vy = v * math.sin(math.radians(angle))

historia_x = [x]
historia_y = [y]

fig, ax = plt.subplots()
line, = ax.plot(historia_x, historia_y)
ax.set_xlim(0, 100)
ax.set_ylim(0, 50)
ax.set_xlabel("Odległość (m)")
ax.set_ylabel("Wysokość (m)")
ax.grid(True)

def update(frame):
    global x, y, vx, vy, historia_x, historia_y
    
    if y < 0:   # jeśli spadnie na ziemię, zatrzymaj animację
        return line,
    
    # update pozycji i prędkości
    x += vx * dt
    y += vy * dt
    vy -= g * dt
    
    historia_x.append(x)
    historia_y.append(y)
    
    line.set_data(historia_x, historia_y)
    return line,

ani = animation.FuncAnimation(fig, update, frames=1000, interval=10, blit=True)
plt.show()