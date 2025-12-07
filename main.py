import pygame
import math
import random
import os
import sys

pygame.init()
pygame.mixer.init()

# ---------------------------
# مسار الموارد داخل EXE
# ---------------------------
def resource_path(relative_path):
    """ للحصول على المسار الصحيح للملفات بعد تحويل البرنامج إلى EXE """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# ---------------------------
# إعداد الشاشة
# ---------------------------
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Romantic Heart Animation")
clock = pygame.time.Clock()

# ---------------------------
# ملفات الصوت
# ---------------------------
music_file = resource_path("mixkit-love-in-the-air-41.mp3")
beat_file = resource_path("beat.wav")

if os.path.exists(music_file):
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.play(-1)
else:
    print("لا يوجد ملف موسيقى خارجي، سيتم تجاهل الموسيقى.")

beat_sound = None
if os.path.exists(beat_file):
    beat_sound = pygame.mixer.Sound(beat_file)
else:
    print("لا يوجد ملف صوت نبضة، سيتم تجاهل الصوت.")

# ---------------------------
# Nebula خلفية بسيطة
# ---------------------------
nebula_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for _ in range(300):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    radius = random.randint(50, 150)
    color = (random.randint(50, 120), random.randint(0, 60), random.randint(80, 150), 50)
    pygame.draw.circle(nebula_surface, color, (x, y), radius)

# ---------------------------
# نجوم متحركة ومتوهجة
# ---------------------------
class Star:
    def __init__(self, layer=1):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        self.layer = layer
        self.size = random.uniform(1.0*layer, 2.5*layer)
        self.alpha = random.randint(100, 255)
        self.dx = random.uniform(-0.1*layer, 0.1*layer)
        self.dy = random.uniform(-0.1*layer, 0.1*layer)
        self.twinkle_offset = random.uniform(0, math.pi*2)

    def update(self, time):
        self.x += self.dx
        self.y += self.dy
        if self.x < -10: self.x = WIDTH + 10
        if self.x > WIDTH + 10: self.x = -10
        if self.y < -10: self.y = HEIGHT + 10
        if self.y > HEIGHT + 10: self.y = -10
        pulse = (math.sin(time*0.002 + self.twinkle_offset) + 1)/2
        self.alpha = int(100 + pulse*155)

    def draw(self, surface):
        s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, self.alpha), (int(self.size), int(self.size)), int(self.size))
        surface.blit(s, (self.x, self.y))

stars = [Star(layer=1) for _ in range(150)] + [Star(layer=2) for _ in range(100)]

# ---------------------------
# نقاط القلب
# ---------------------------
def generate_heart_points(y_offset=0):
    scale = min(WIDTH, HEIGHT)//30
    points=[]
    for i in range(0,360,2):
        angle = math.radians(i)
        x = 16*math.sin(angle)**3
        y = 13*math.cos(angle)-5*math.cos(2*angle)-2*math.cos(3*angle)-math.cos(4*angle)
        px = WIDTH//2 + int(x*scale)
        py = HEIGHT//2 - int(y*scale) + y_offset
        points.append((px, py))
    return points, scale

heart_points, heart_scale = generate_heart_points(y_offset=-50)

# ---------------------------
# Gradient Colors كامل
# ---------------------------
def generate_gradient_colors(n):
    colors=[]
    for i in range(n):
        t = i/n
        if t < 0.5:
            colors.append((255,0,0))
        else:
            remaining_t = (t-0.5)/0.5
            if remaining_t<0.2:
                local_t=remaining_t/0.2
                r=int(255*(1-local_t)+255*local_t)
                g=int(0*(1-local_t)+105*local_t)
                b=int(0*(1-local_t)+180*local_t)
                colors.append((r,g,b))
            elif remaining_t<0.4:
                local_t=(remaining_t-0.2)/0.2
                r=int(255*(1-local_t)+148*local_t)
                g=int(105*(1-local_t)+0*local_t)
                b=int(180*(1-local_t)+211*local_t)
                colors.append((r,g,b))
            elif remaining_t<0.6:
                local_t=(remaining_t-0.4)/0.2
                r=int(148*(1-local_t)+0*local_t)
                g=int(0*(1-local_t)+191*local_t)
                b=int(211*(1-local_t)+255*local_t)
                colors.append((r,g,b))
            elif remaining_t<0.8:
                local_t=(remaining_t-0.6)/0.2
                r=int(0*(1-local_t)+255*local_t)
                g=int(191*(1-local_t)+165*local_t)
                b=int(255*(1-local_t)+0*local_t)
                colors.append((r,g,b))
            else:
                local_t=(remaining_t-0.8)/0.2
                r=int(255*(1-local_t)+255*local_t)
                g=int(165*(1-local_t)+255*local_t)
                b=int(0*(1-local_t)+0*local_t)
                colors.append((r,g,b))
    return colors

gradient_colors = generate_gradient_colors(len(heart_points))

# ---------------------------
# خط يتحرك لرسم القلب
# ---------------------------
class LineDrawer:
    def __init__(self,target,color):
        self.start = (WIDTH//2, HEIGHT//2-50)
        self.target = target
        self.current = list(self.start)
        self.done = False
        self.speed = 0.08 + random.random()*0.03
        self.color = color
    def update(self):
        if not self.done:
            dx=self.target[0]-self.current[0]
            dy=self.target[1]-self.current[1]
            dist=math.hypot(dx,dy)
            if dist<0.5:
                self.current=list(self.target)
                self.done=True
            else:
                self.current[0]+=dx*self.speed
                self.current[1]+=dy*self.speed
    def draw(self,surface):
        pygame.draw.line(surface,self.color,self.start,self.current,3)

lines = [LineDrawer(p,gradient_colors[i]) for i,p in enumerate(heart_points)]
line_index = 0

# ---------------------------
# جسيمات متطايرة حول القلب
# ---------------------------
class Particle:
    def __init__(self,x,y):
        self.x = x + random.randint(-5,5)
        self.y = y + random.randint(-5,5)
        self.size = random.randint(1,3)
        self.alpha = random.randint(100,200)
        self.speed = random.uniform(0.2,1)
        self.color = random.choice([(255,105,180),(255,182,193),(148,0,211),(138,43,226),(0,191,255),(255,165,0),(255,255,0)])
    def update(self):
        self.y -= self.speed
        self.alpha -= 2
        self.x += random.uniform(-0.5,0.5)
    def draw(self,surface):
        if self.alpha>0:
            s=pygame.Surface((self.size*2,self.size*2),pygame.SRCALPHA)
            pygame.draw.circle(s,(*self.color,self.alpha),(self.size,self.size),self.size)
            surface.blit(s,(self.x,self.y))

particles=[]

# ---------------------------
# ---------------------------
love_text="♥ You are my heart, and my forever, Sama ♥,, ♥ Sama, i love you. ♥"
text_progress=0
font_size=max(WIDTH,HEIGHT)//45
font=pygame.font.SysFont("DejaVu Sans",font_size,bold=True)
text_start_time=None
letters_per_second=5
def draw_love_text(surface,text,progress):
    text_to_draw=text[:progress]
    text_surf=font.render(text_to_draw,True,(255,200,220))
    rect=text_surf.get_rect(center=(WIDTH//2,HEIGHT-100))
    surface.blit(text_surf,rect)

# ---------------------------
# Fade-in للقلب
# ---------------------------
heart_alpha=0
def apply_fade(surface):
    global heart_alpha
    heart_alpha=min(255,heart_alpha+3)
    fade_layer=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
    fade_layer.fill((0,0,0,max(0,255-heart_alpha)))
    surface.blit(fade_layer,(0,0))

# ---------------------------
# نبض القلب + توهج + صوت نبض
# ---------------------------
pulse=0
pulse_speed=0.1
pulse_scale=0.06
def draw_pulse(surface):
    global pulse
    pulse+=pulse_speed
    scale_mod=1 + math.sin(pulse)*pulse_scale
    glow_alpha = int(80 + 80 * math.sin(pulse*2))
    for i,p in enumerate(heart_points):
        dx=p[0]-WIDTH//2
        dy=p[1]-(HEIGHT//2-50)
        new_x=WIDTH//2+int(dx*scale_mod)
        new_y=(HEIGHT//2-50)+int(dy*scale_mod)
        s = pygame.Surface((6,6),pygame.SRCALPHA)
        pygame.draw.circle(s,(*gradient_colors[i],glow_alpha),(3,3),3)
        surface.blit(s,(new_x-3,new_y-3))
        pygame.draw.circle(surface,gradient_colors[i],(new_x,new_y),3)
    # تشغيل صوت النبضة بشكل صحيح
    if beat_sound and int((math.sin(pulse)*1000)) % 60 == 0:
        beat_sound.play()

# ---------------------------
# الحلقة الرئيسية
# ---------------------------
running=True
while running:
    dt=clock.tick(60)
    time_now=pygame.time.get_ticks()
    screen.fill((0,0,20))
    screen.blit(nebula_surface,(0,0))

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False

    # النجوم
    for star in stars:
        star.update(time_now)
        star.draw(screen)

    # رسم القلب
    lines_per_frame=6
    for _ in range(lines_per_frame):
        if line_index<len(lines):
            lines[line_index].update()
            if lines[line_index].done:
                line_index+=1

    for i in range(line_index):
        lines[i].draw(screen)
        if random.random()<0.3:
            particles.append(Particle(lines[i].current[0],lines[i].current[1]))
    if line_index<len(lines):
        lines[line_index].draw(screen)
        if random.random()<0.3:
            particles.append(Particle(lines[line_index].current[0],lines[line_index].current[1]))

    # الجسيمات
    for particle in particles[:]:
        particle.update()
        particle.draw(screen)
        if particle.alpha<=0:
            particles.remove(particle)

    # Fade-in + نبض + نص
    if line_index>=len(lines):
        apply_fade(screen)
        draw_pulse(screen)
        if text_start_time is None:
            text_start_time=time_now
        else:
            elapsed=time_now-text_start_time
            text_progress=min(len(love_text),int(elapsed/1000*letters_per_second))
        draw_love_text(screen,love_text,text_progress)

    pygame.display.flip()

pygame.quit()
