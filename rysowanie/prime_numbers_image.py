from PIL import Image, ImageDraw
import os

class Sett:
    def __init__(self):
        self.size = 25000
        self.img = Image.new("RGB", (self.size, self.size), "black")
        self.draw = ImageDraw.Draw(self.img)
   
        self.num = 100000000
        
        self.primes = self.sieve(self.num+1)

    def sieve(self, n):
        prime = bytearray(b"\x01") * n
        prime[0:2] = b"\x00\x00"

        for i in range(2, int(n**0.5) + 1):
            if prime[i]:
                prime[i*i:n:i] = b"\x00" * len(prime[i*i:n:i])

        return prime
            
                
class Draw:
    def __init__(self, sett):
        self.sett = sett
        self.x = 3000
        self.y = 3000
        
        
        self.positions = ['up', 'right', 'down', 'left']
        self.pos_index = 0
        
        self.pos_x = 0
        self.pos_y = 0
        
        self.num = 0
        
        self.camera_x = 0
        self.camera_y = 0
        
        self.points = [(self.x, self.y)]
        
    def update(self):
        self.num += 1
        if self.sett.primes[self.num]:
            if self.pos_index == 3:
                self.pos_index = 0
            else:
                self.pos_index += 1
            
        if self.positions[self.pos_index] == 'up':
            self.pos_y = -1
            self.pos_x = 0
        elif self.positions[self.pos_index] == 'right':
            self.pos_x = 1
            self.pos_y = 0
        elif self.positions[self.pos_index] == 'down':
            self.pos_y = 1
            self.pos_x = 0
        elif self.positions[self.pos_index] == 'left':
            self.pos_x = -1
            self.pos_y = 0
        
    def draw(self):
        self.sett.draw.line((self.x, self.y, self.x + self.pos_x, self.y + self.pos_y), fill="white")
        
        self.x += self.pos_x
        self.y += self.pos_y
        
      
sett = Sett()
        
draw = Draw(sett=sett)
        
for _ in range(sett.num):
                
    draw.update()
    
    draw.draw() 
                

sett.img.save("C:/Users/suwaj/OneDrive/Pulpit/prime_walk_moved.png")
print("zapisano")