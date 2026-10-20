import pygame
import math
import random
import sys

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 900, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multilingual Heart with Fireworks")
clock = pygame.time.Clock()

# --- Configuration & Colors ---
FONT_SIZE = 13
font = pygame.font.SysFont("Consolas", FONT_SIZE, bold=True)

# The repeating string containing "I love you" in multiple languages
LOVE_TEXT = (
    "Ich liebe dich Ti amo Aku cinta kamu 愛してる Te amo Je t'aime 사랑해 "
    "Seni seviyorum Σ' αγαπώ Ik hou van jou Я тебя люблю Eu te amo "
    "Szeretlek Jag älskar dig "
)

# --- Firework Particle System ---
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 7)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.alpha = 255
        self.fade_speed = random.uniform(3, 7)
        self.radius = random.randint(2, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05  # Gravity effect
        self.alpha -= self.fade_speed

    def draw(self, surface):
        if self.alpha > 0:
            # Create a small surface for alpha blending (glow effect)
            s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, int(self.alpha))
            pygame.draw.circle(s, color_with_alpha, (self.radius, self.radius), self.radius)
            surface.blit(s, (int(self.x - self.radius), int(self.y - self.radius)))

class Firework:
    def __init__(self):
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(100, HEIGHT // 2)
        # Festive bright firework colors
        self.color = random.choice([
            (255, 255, 255), (255, 50, 50), (50, 255, 50), 
            (50, 100, 255), (255, 255, 50), (255, 50, 255), (50, 255, 255)
        ])
        self.particles = [Particle(self.x, self.y, self.color) for _ in range(60)]

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alpha > 0]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

# --- ASCII Heart Mathematical Generator ---
def get_heart_mask(width, height, scale=17):
    """Generates an grid layout determining if a coordinate falls inside a mathematical heart shape."""
    mask = []
    center_x = width // 2
    center_y = height // 2 - 40
    
    for y in range(0, height, FONT_SIZE - 2):
        row = []
        for x in range(0, width, FONT_SIZE - 5):
            # Normalize coordinates to map onto the heart equations
            nx = (x - center_x) / scale
            ny = -(y - center_y) / scale
            
            # Standard algebraic heart curve equation: (x^2 + y^2 - 1)^3 - x^2 * y^3 <= 0
            if (nx**2 + ny**2 - 1)**3 - (nx**2) * (ny**3) <= 0:
                row.append(True)
            else:
                row.append(False)
        mask.append(row)
    return mask

# Initialize objects
fireworks = []
heart_mask = get_heart_mask(WIDTH, HEIGHT, scale=18)
text_index = 0

# --- Main Animation Loop ---
running = True
while running:
    # Handle window exits
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. Background Fill (Dark Charcoal)
    screen.fill((15, 15, 18))

    # 2. Launch Background Fireworks randomly
    if random.random() < 0.04 and len(fireworks) < 5:
        fireworks.append(Firework())

    # Update and Draw Fireworks
    for f in fireworks:
        f.update()
        f.draw(screen)
    fireworks = [f for f in fireworks if len(f.particles) > 0]

    # 3. Overlay the Multilingual Glowing Heart Text
    text_pointer = text_index
    current_y = 40
    
    for row in heart_mask:
        current_x = 25
        for is_inside_heart in row:
            if is_inside_heart:
                # Grab the next character from our multilingual love string
                char = LOVE_TEXT[text_pointer % len(LOVE_TEXT)]
                text_pointer += 1
                
                # Render character with a warm glowing neon pink/red color
                char_surface = font.render(char, True, (255, 60, 95))
                screen.blit(char_surface, (current_x, current_y))
            
            # Space out characters cleanly across the matrix layout
            current_x += FONT_SIZE - 5
        current_y += FONT_SIZE - 2

    # Slow translation shift creates a subtle moving wave text effect inside the heart
    if random.random() < 0.2:
        text_index = (text_index + 1) % len(LOVE_TEXT)

    # Refresh Screen at standard 60 FPS
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
