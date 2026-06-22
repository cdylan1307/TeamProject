import pygame
import sys
from os.path import join
import os
import random
import math

# Helper function for executable path resolution
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running as executable
        base_path = os.path.dirname(sys.executable)
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

def load_image_safe(path, fallback_color=(255, 0, 255), size=(50, 50)):
    """Safely load an image with fallback"""
    # Try multiple path variations
    paths_to_try = [
        path,
        get_resource_path(path)
    ]
    
    for p in paths_to_try:
        try:
            if os.path.exists(p):
                return pygame.image.load(p).convert_alpha()
        except:
            continue
    
    # Create fallback surface
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill(fallback_color)
    return surf

from src.level2 import start_level_2
import src.level3 as level3  # Import Level 3 package
import src.cutscene as cutscene  # Import cutscene module
from src.leaderboard import LeaderboardManager, GameTimer
from src.animation_system import AnimatedPlayer, AnimatedPatroclus  # Import animation system

### ========================================== ###
### 1. INITIALIZATION & AUDIO SETUP            ###
### ========================================== ###
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1280, 720  
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Achilles and Patroclus")

FPS = 60
clock = pygame.time.Clock()

try:
    pygame.mixer.music.load("audio/backgroundMusic.mp3")
    pygame.mixer.music.play(loops=-1)
except pygame.error:
    print("Warning: audio/backgroundMusic.mp3 not found or could not be loaded.")

def load_sfx(filename):
    audio_path = f"audio/{filename}"
    if os.path.exists(audio_path):
        try: return pygame.mixer.Sound(audio_path)
        except pygame.error: return None
    return None

click_sound = load_sfx("mouse.mp3")
win_sound   = load_sfx("win.mp3")
fail_sound  = load_sfx("fail.mp3")
shoot_sound = load_sfx("shoot.mp3")

### ========================================== ###
### 2. FONTS & COLOR CONFIGURATION            ###
### ========================================== ###
FONT = pygame.font.SysFont("Courier New", 36, bold=True)
SMALL_FONT = pygame.font.SysFont("Courier New", 28, bold=True)

try:
    GAME_FONT = pygame.font.Font("text/Oxanium-Bold.ttf", 64)
    GAME_LARGE_FONT = pygame.font.Font("text/Oxanium-Bold.ttf", 90)  
    GAME_SMALL_FONT = pygame.font.Font("text/Oxanium-Bold.ttf", 24)
    GAME_POPUP_FONT = pygame.font.Font("text/Oxanium-Bold.ttf", 20)
except IOError:
    GAME_FONT = pygame.font.SysFont("Arial", 64, bold=True)
    GAME_LARGE_FONT = pygame.font.SysFont("Arial", 90, bold=True)
    GAME_SMALL_FONT = pygame.font.SysFont("Arial", 24, bold=True)
    GAME_POPUP_FONT = pygame.font.SysFont("Arial", 20, bold=True)

BLUE = (40, 80, 160)
LIGHT_BLUE = (80, 140, 255)
GREEN = (40, 180, 80)
RED = (180, 50, 50)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SHADOW_COLOR = (30, 30, 50)

### ========================================== ###
### 2.5. HELPER FUNCTIONS FOR EFFECTS          ###
### ========================================== ###
def draw_health_bar(surface, x, y, current_health, max_health, width=50, height=6):
    """Draw a health bar above an enemy"""
    # Background (black border)
    pygame.draw.rect(surface, BLACK, (x - width // 2 - 1, y - 1, width + 2, height + 2))
    # Red background (lost health)
    pygame.draw.rect(surface, RED, (x - width // 2, y, width, height))
    # Green foreground (current health)
    health_width = int((current_health / max_health) * width)
    if health_width > 0:
        pygame.draw.rect(surface, GREEN, (x - width // 2, y, health_width, height))

class BloodSpray:
    """Blood spray particle effect when enemy is hit"""
    def __init__(self, x, y):
        self.particles = []
        # Create 8-15 blood particles
        num_particles = random.randint(8, 15)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.uniform(0.3, 0.6),  # Lifetime in seconds
                'size': random.randint(3, 7)
            })
    
    def update(self, dt):
        """Update particle positions and lifetimes"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['vy'] += 200 * dt  # Gravity
            particle['life'] -= dt
            if particle['life'] <= 0:
                self.particles.remove(particle)
        return len(self.particles) > 0  # Return True if still alive
    
    def draw(self, surface):
        """Draw blood particles"""
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 0.6))  # Fade out
            color = (180, 0, 0, min(255, alpha))
            # Create a temporary surface with per-pixel alpha
            particle_surf = pygame.Surface((particle['size'], particle['size']), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color, (particle['size'] // 2, particle['size'] // 2), particle['size'] // 2)
            surface.blit(particle_surf, (int(particle['x']), int(particle['y'])))

# Global list to store active blood spray effects
blood_sprays = []

PLACEHOLDER_BG = (25, 25, 35)

menu_shadow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
menu_shadow.fill((0, 0, 0, 120))

### ========================================== ###
### 3. ASSETS & SCROLLING CONFIGURATION        ###
### ========================================== ###
background = None
bg_paths = [
    get_resource_path("backgrounds/jungle.jpg"),
    "backgrounds/jungle.jpg"
]

for bg_path in bg_paths:
    try:
        if os.path.exists(bg_path):
            background = pygame.image.load(bg_path).convert()
            background = pygame.transform.scale(background, (WIDTH, HEIGHT))
            break
    except:
        continue

if not background:
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(PLACEHOLDER_BG)

bg_scroll_x = 0
BG_SCROLL_SPEED = 80  

settings_bg = None
if os.path.exists("settings.png"):
    settings_bg = pygame.image.load("settings.png").convert()
    settings_bg = pygame.transform.scale(settings_bg, (WIDTH, HEIGHT))

game_bg = None
game_bg_paths = [
    get_resource_path("images/lv1background.png"),
    "images/lv1background.png",
    get_resource_path("backgrounds/forest.png"),
    "backgrounds/forest.png"
]

for bg_path in game_bg_paths:
    try:
        if os.path.exists(bg_path):
            game_bg = pygame.image.load(bg_path).convert()
            break
    except:
        continue

if game_bg:
    game_bg = pygame.transform.scale(game_bg, (WIDTH, HEIGHT))
else:
    game_bg = pygame.Surface((WIDTH, HEIGHT))
    game_bg.fill((40, 40, 40))

rock_image = load_image_safe("sprites/rock.png", (120, 120, 120), (25, 25))
rock_image = pygame.transform.scale(rock_image, (25, 25))

heart_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
pygame.draw.circle(heart_surf, (220, 40, 40), (6, 8), 6)
pygame.draw.circle(heart_surf, (220, 40, 40), (18, 8), 6)
pygame.draw.polygon(heart_surf, (220, 40, 40), [(0, 10), (12, 24), (24, 10)])

all_sprites = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()
projectile_sprites = pygame.sprite.Group()

chiron_walk_frames = []
for i in range(6):
    frame_path = get_resource_path(join("animations", "Chiron", "Walking", f"Chiron_Walk_{i}.png"))
    frame = load_image_safe(frame_path, (255, 0, 0), (50, 50))
    chiron_walk_frames.append(frame)

### ========================================== ###
### 4. UI & ENTITY CLASSES                     ###
### ========================================== ###
class Bard:
    FRAME_DURATION = 100

    def __init__(self, window_height: int, scale: float = 1.0):
        self.frames = self._load_frames(scale)
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.x = 15
        self.y = (window_height // 2) - (self.frames[0].get_height() // 2)

    def _load_frames(self, scale: float) -> list[pygame.Surface]:
        # Handle both executable and script environments
        if getattr(sys, 'frozen', False):
            # Running as executable
            base_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        bard_idle_path = os.path.join(base_dir, "images", "Bard Idle")
        if not os.path.exists(bard_idle_path):
            bard_idle_path = os.path.join(base_dir, "..", "images", "Bard Idle")
            
        frames = []
        for i in range(3):
            frame_path = os.path.join(bard_idle_path, f"pixil-frame-{i}.png")
            try:
                frame = pygame.image.load(frame_path).convert_alpha()
            except FileNotFoundError:
                frame = pygame.Surface((40, 60), pygame.SRCALPHA)
                frame.fill((200, 100, 200, 150))
                pygame.draw.rect(frame, WHITE, (5, 5, 30, 50), 2)
            if scale != 1:
                frame = pygame.transform.scale_by(frame, scale)
            frames.append(frame)
        return frames

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.FRAME_DURATION:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time

    def draw(self, surface: pygame.Surface):
        surface.blit(self.frames[self.current_frame], (self.x, self.y))


class PixelButton:
    def __init__(self, text, x, y, w, h, color=BLUE, hover_color=LIGHT_BLUE):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.hover_color = hover_color

    def draw(self):
        mouse = pygame.mouse.get_pos()
        current_color = self.hover_color if self.rect.collidepoint(mouse) else self.color

        # Draw shadow (offset down and right)
        shadow_rect = self.rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(SCREEN, (0, 0, 0, 120), shadow_rect, border_radius=5)
        
        # Draw main button
        pygame.draw.rect(SCREEN, current_color, self.rect, border_radius=5)
        
        # Draw button border
        pygame.draw.rect(SCREEN, BLACK, self.rect, 2, border_radius=5)

        text_surface = FONT.render(self.text, False, WHITE)
        SCREEN.blit(
            text_surface,
            (
                self.rect.centerx - text_surface.get_width() // 2,
                self.rect.centery - text_surface.get_height() // 2,
            ),
        )

    def clicked(self, event, game_sounds_enabled=True):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if game_sounds_enabled and click_sound: 
                click_sound.play()
            return True
        return False


class ToggleButton:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 120, 50)
        self.enabled = True

    def draw(self):
        color = GREEN if self.enabled else RED
        text = "ON" if self.enabled else "OFF"

        pygame.draw.rect(SCREEN, BLACK, self.rect.inflate(6, 6))
        pygame.draw.rect(SCREEN, color, self.rect)

        label = SMALL_FONT.render(text, False, WHITE)
        SCREEN.blit(label, (self.rect.centerx - label.get_width() // 2, self.rect.centery - label.get_height() // 2))

    def clicked(self, event, game_sounds_enabled=True):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if game_sounds_enabled and click_sound: 
                click_sound.play()
            self.enabled = not self.enabled
            return True
        return False


class RockProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, angle_rad, groups):
        super().__init__(groups)
        self.image = rock_image
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 600
        self.direction = pygame.Vector2(math.cos(angle_rad), math.sin(angle_rad))

    def update(self, dt):
        self.rect.centerx += self.direction.x * self.speed * dt
        self.rect.centery += self.direction.y * self.speed * dt
        if not SCREEN.get_rect().colliderect(self.rect):
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.group = groups
        
        # Initialize animated player
        self.animated_player = AnimatedPlayer(WIDTH // 2, HEIGHT // 2, scale=1.2)
        
        # Create image from animated player for sprite functionality
        self.image = load_image_safe("sprites/player.png", (0, 255, 0), (50, 50))
            
        self.rect = self.image.get_rect(center = (WIDTH / 2, HEIGHT / 2))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2()
        self.speed = 300
        self.health = 2  # Reduced from 3 to 2
        self.stones_left = 20  
        self.invincible_timer = 0
        self.throw_cooldown = 0  # Cooldown timer for rock throwing
    
    def update(self, dt):
        if self.invincible_timer > 0:
            self.invincible_timer -= dt
        if self.throw_cooldown > 0:
            self.throw_cooldown -= dt
        self.movement(dt)
        
        # Update animated player position and animation
        self.animated_player.x = self.rect.x
        self.animated_player.y = self.rect.y
        self.animated_player.update()
 
    def movement(self, dt):
        keys = pygame.key.get_pressed()
        
        # Calculate direction for the main game sprite
        self.direction.x = (int(keys[pygame.K_RIGHT]) or int(keys[pygame.K_d])) - (int(keys[pygame.K_LEFT]) or int(keys[pygame.K_a]))
        self.direction.y = (int(keys[pygame.K_DOWN]) or int(keys[pygame.K_s])) - (int(keys[pygame.K_UP]) or int(keys[pygame.K_w]))
        
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
        
        # Move the main sprite
        self.rect.center += self.direction * self.speed * dt
        
        # Update animated player movement for animation purposes
        self.animated_player.update_movement(keys)
    
    def draw_animated(self, surface):
        """Draw the animated version of the player"""
        self.animated_player.draw(surface)


class Chiron(pygame.sprite.Sprite):
    def __init__(self, groups, speed, player_ref, border_rect):
        super().__init__(groups)
        self.group = groups
        self.player = player_ref
        self.scale = 0.75
        self.border = border_rect
        self.max_health = 9  # Maximum health (increased from 8 to 9)
        self.health = 9  # Current health

        if os.path.exists(get_resource_path("animations/Chiron/Walking/Chiron_Walk_0.png")):
            self.image = load_image_safe("animations/Chiron/Walking/Chiron_Walk_0.png", (255, 0, 0), (60, 60))
            try: 
                self.image = pygame.transform.scale_by(self.image, self.scale)
            except: 
                pass
        else:
            self.image = pygame.Surface((60, 60))
            self.image.fill((255, 0, 0))

        self.teleport_randomly()
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = speed
        self.frames = chiron_walk_frames
        self.frame_index = 0

    def teleport_randomly(self):
        # Spawn randomly within the circular boundary
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(50, circle_radius - 50)  # Keep some margin from edge
        spawn_x = circle_center_x + math.cos(angle) * distance
        spawn_y = circle_center_y + math.sin(angle) * distance
        
        self.rect = self.image.get_rect(center=(int(spawn_x), int(spawn_y)))

    def update(self, dt):
        if self.frames:
            self.frame_index += 10 * dt
            if self.frame_index < len(self.frames):
                self.image = self.frames[int(self.frame_index)]
                try: self.image = pygame.transform.scale_by(self.image, self.scale)
                except: pass
            else:
                self.frame_index = 0
        
        if self.player.alive():
            enemy_vector = pygame.math.Vector2(self.player.rect.centerx - self.rect.centerx,
                                               self.player.rect.centery - self.rect.centery)
            if enemy_vector.length() > 0:
                enemy_vector = enemy_vector.normalize()
            self.rect.center += enemy_vector * self.speed * dt
    
    def draw_health_bar(self, surface):
        """Draw health bar above Chiron"""
        if self.health < self.max_health:  # Only show if damaged
            draw_health_bar(surface, self.rect.centerx, self.rect.top - 10, self.health, self.max_health, width=60, height=7)


class Patroclus(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.group = groups
        
        # Initialize animated Patroclus
        self.animated_patroclus = AnimatedPatroclus(WIDTH // 2 - 20, HEIGHT // 2 + 20, scale=1.0)
        
        self.image = load_image_safe("sprites/player.png", (200, 200, 255), (40, 40))
            
        self.rect = self.image.get_rect(center = (WIDTH / 2 - 20, HEIGHT / 2 + 20))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2()
        self.speed = 260 

    def update(self, dt):
        target_x = player.rect.x - 40
        target_y = player.rect.y + 40
        
        # Update animated Patroclus
        self.animated_patroclus.follow_player(target_x, target_y)
        healing_result = self.animated_patroclus.update()
        
        # Sync positions
        self.rect.x = int(self.animated_patroclus.x)
        self.rect.y = int(self.animated_patroclus.y)
        
        # Return healing result so it can be handled at the game loop level
        return healing_result
    
    def draw_animated(self, surface):
        """Draw the animated version of Patroclus"""
        self.animated_patroclus.draw(surface)


### ========================================== ###
### 5. INSTANTIATION & INITIAL VARIABLE STATES ###
### ========================================== ###
# Circular boundary instead of rectangular
circle_center_x = WIDTH // 2
circle_center_y = HEIGHT // 2
circle_radius = 300

# Keep the border rect for compatibility but define circle boundary
border = pygame.Rect(200, 100, 880, 520)

def keep_in_circle(sprite, center_x, center_y, radius):
    """Keep a sprite within a circular boundary"""
    # Calculate distance from sprite center to circle center
    dx = sprite.rect.centerx - center_x
    dy = sprite.rect.centery - center_y
    distance = math.sqrt(dx*dx + dy*dy)
    
    # If outside the circle, move back to the edge
    if distance > radius:
        # Calculate the angle and place sprite at circle edge
        angle = math.atan2(dy, dx)
        sprite.rect.centerx = center_x + math.cos(angle) * radius
        sprite.rect.centery = center_y + math.sin(angle) * radius

buttons = [
    PixelButton("START", WIDTH // 2 - 100, 240, 200, 60),
    PixelButton("ENDLESS", WIDTH // 2 - 100, 320, 200, 60),  # Wider to fit text
    PixelButton("SETTINGS", WIDTH // 2 - 100, 400, 200, 60),
    PixelButton("CREDITS", WIDTH // 2 - 100, 480, 200, 60),
    PixelButton("QUIT", WIDTH // 2 - 100, 560, 200, 60),
]

music_toggle = ToggleButton(WIDTH // 2 - 20, 220)
sound_toggle = ToggleButton(WIDTH // 2 - 20, 320)
game_sounds_toggle = ToggleButton(WIDTH // 2 - 20, 420)

btn_level2 = PixelButton("GO TO LEVEL 2", WIDTH // 2 - 150, HEIGHT // 2 + 50, 300, 60, GREEN, (60, 220, 100))
btn_restart = PixelButton("RESTART GAME", WIDTH // 2 - 150, HEIGHT // 2 + 50, 300, 60, RED, (220, 70, 70))

# Level UI Context Managers
btn_continue_l2 = PixelButton("CONTINUE L2", WIDTH // 2 - 150, HEIGHT // 2 - 40, 300, 60, BLUE, LIGHT_BLUE)
btn_continue_l3 = PixelButton("CONTINUE L3", WIDTH // 2 - 150, HEIGHT // 2 - 40, 300, 60, BLUE, LIGHT_BLUE)
btn_restart_fresh = PixelButton("RESTART", WIDTH // 2 - 150, HEIGHT // 2 + 40, 300, 60, RED, (220, 70, 70))

# Global timer and leaderboard
game_timer = GameTimer()
leaderboard = LeaderboardManager()
player_name = ""
current_player_name = ""

scene = "splash"  
credits_y = HEIGHT
start_round = False
current_active_level = 1

kill_count = 0
WIN_TARGET = 1  # Changed to 1 - only need to defeat 1 Chiron enemy
harm_text_popups = []  

audio_win_played = False
audio_fail_played = False

bard_companion = Bard(window_height=HEIGHT, scale=1.35)

player = Player(all_sprites)
patroclus = Patroclus(all_sprites)
enemy_instance = Chiron((all_sprites, enemy_sprites), 0, player, border)
# Removed enemy_instance2 - only one Chiron now

triangle_center_x = WIDTH // 2
triangle_center_y = HEIGHT // 2 - 10
triangle_points = [
    (triangle_center_x - 30, triangle_center_y - 40), 
    (triangle_center_x - 30, triangle_center_y + 40), 
    (triangle_center_x + 40, triangle_center_y)
]
triangle_bounding_rect = pygame.Rect(triangle_center_x - 35, triangle_center_y - 45, 80, 90)

def reset_entire_game():
    global kill_count, harm_text_popups, start_round, player, enemy_instance, patroclus, audio_win_played, audio_fail_played, blood_sprays
    all_sprites.empty()
    enemy_sprites.empty()
    projectile_sprites.empty()
    kill_count = 0
    harm_text_popups.clear()
    start_round = False
    audio_win_played = False
    audio_fail_played = False
    blood_sprays = []  # Reset blood sprays
    player = Player(all_sprites)
    patroclus = Patroclus(all_sprites)
    enemy_instance = Chiron((all_sprites, enemy_sprites), 0, player, border)
    # Removed enemy_instance2 - only one Chiron now
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.play(loops=-1)
    except: pass

def handle_gameplay_collisions():
    global kill_count, enemy_instance, blood_sprays
    if not player.alive(): return

    # Check collision for the single enemy
    if enemy_instance.alive():
        projectile_hits = pygame.sprite.spritecollide(enemy_instance, projectile_sprites, True, pygame.sprite.collide_mask)
        if projectile_hits:
            # Decrement health by the number of projectiles that hit
            enemy_instance.health -= len(projectile_hits)
            # Create blood spray effect for each hit
            for _ in range(len(projectile_hits)):
                blood_sprays.append(BloodSpray(enemy_instance.rect.centerx, enemy_instance.rect.centery))
            if enemy_instance.health <= 0:
                enemy_instance.kill()
                kill_count += 1
                # Respawn enemy until WIN_TARGET is reached
                if kill_count < WIN_TARGET:
                    enemy_instance = Chiron((all_sprites, enemy_sprites), 150, player, border)

        if pygame.sprite.collide_mask(player, enemy_instance):
            if player.invincible_timer <= 0:
                player.health -= 1
                player.invincible_timer = 1.0
                enemy_instance.teleport_randomly()
                
                text_surf = GAME_POPUP_FONT.render("You are harmed!", True, WHITE)
                w, h = text_surf.get_width() + 20, text_surf.get_height() + 16
                
                bubble_surf = pygame.Surface((w, h), pygame.SRCALPHA)
                pygame.draw.rect(bubble_surf, (200, 40, 40, 230), (0, 0, w, h), border_radius=8) 
                pygame.draw.rect(bubble_surf, WHITE, (0, 0, w, h), width=2, border_radius=8)
                bubble_surf.blit(text_surf, (10, 8))
                
                rand_x = random.randint(220, WIDTH - 400)
                rand_y = random.randint(120, HEIGHT - 160)
                harm_text_popups.append([bubble_surf, (rand_x, rand_y), 1.5])
                harm_text_popups.append([bubble_surf, (rand_x, rand_y), 1.5])

### ========================================== ###
### 6. CORE APPLICATION LOOP                   ###
### ========================================== ###
while True:
    dt = clock.tick(FPS) / 1000
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if scene == "splash":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if triangle_bounding_rect.collidepoint(event.pos):
                    if game_sounds_toggle.enabled and click_sound: 
                        click_sound.play()
                    scene = "menu"

        elif scene == "name_input":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if player_name.strip():  # Make sure name isn't empty
                        current_player_name = player_name.strip()
                        
                        # Start timer first
                        game_timer.start()
                        
                        # Pause timer during cutscene 
                        game_timer.pause()
                        
                        # Play Level 1 cutscene
                        cutscene_result = cutscene.play_cutscene(SCREEN, "level1")
                        
                        # Resume timer after cutscene
                        game_timer.resume()
                        
                        reset_entire_game()
                        scene = "game"
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    scene = "menu"
                    player_name = ""
                else:
                    # Add character to name (limit to 15 characters)
                    if len(player_name) < 15 and event.unicode.isprintable():
                        player_name += event.unicode
        
        elif scene == "endless_name_input":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if player_name.strip():  # Make sure name isn't empty
                        current_player_name = player_name.strip()
                        # Start endless mode
                        from src import endless_mode
                        endless_mode.start_endless_mode(bard_companion, current_player_name, game_sounds_toggle.enabled)
                        scene = "menu"
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    scene = "menu"
                    player_name = ""
                else:
                    # Add character to name (limit to 15 characters)
                    if len(player_name) < 15 and event.unicode.isprintable():
                        player_name += event.unicode

        elif scene == "menu":
            if event.type == pygame.KEYDOWN:
                # SECRET HOTKEY 'K': Jump instantly into Level 3 from the menu screen
                if event.key == pygame.K_k:
                    current_active_level = 3
                    status = level3.start_level_3(bard_companion, game_timer, current_player_name, game_sounds_toggle.enabled)
                    if status == "escaped":
                        scene = "level3_choice"
                    else:
                        scene = "menu"
                # HOTKEY '2': Go back to splash screen (triangle button page)
                elif event.key == pygame.K_2:
                    scene = "splash"

            if buttons[0].clicked(event, game_sounds_toggle.enabled):
                if current_active_level == 2:
                    scene = "level2_choice"
                elif current_active_level == 3:
                    scene = "level3_choice"
                else:
                    # Go to name input screen instead of directly starting
                    player_name = ""
                    scene = "name_input"
            elif buttons[1].clicked(event, game_sounds_toggle.enabled):
                # ENDLESS MODE button
                player_name = ""
                scene = "endless_name_input"
            elif buttons[2].clicked(event, game_sounds_toggle.enabled):
                scene = "settings"
            elif buttons[3].clicked(event, game_sounds_toggle.enabled):
                credits_y = HEIGHT
                scene = "credits"
            elif buttons[4].clicked(event, game_sounds_toggle.enabled):
                pygame.quit()
                sys.exit()

        elif scene == "level2_choice":
            if btn_continue_l2.clicked(event, game_sounds_toggle.enabled):
                status, checkpoint = start_level_2(
                    bard_companion,
                    sound_toggle.enabled,
                    None,  # checkpoint
                    game_timer,  # timer
                    current_player_name,  # player name
                    game_sounds_toggle.enabled  # game sounds
                )

                if status == "escaped":
                    current_active_level = 2
                    scene = "menu"

                elif status == "completed":
                    current_active_level = 3
                    status_l3 = level3.start_level_3(bard_companion, game_timer, current_player_name, game_sounds_toggle.enabled)
                    scene = "level3_choice" if status_l3 == "escaped" else "menu"
            elif btn_restart_fresh.clicked(event, game_sounds_toggle.enabled):
                # Go to name input for fresh restart
                player_name = ""
                current_active_level = 1
                scene = "name_input"

        elif scene == "level3_choice":
            if btn_continue_l3.clicked(event, game_sounds_toggle.enabled):
                status = level3.start_level_3(bard_companion, game_timer, current_player_name, game_sounds_toggle.enabled)
                if status == "escaped":
                    current_active_level = 3
                    scene = "menu"
                elif status == "completed":
                    # Game completed! Stop timer and add to leaderboard
                    final_time = game_timer.stop()
                    if current_player_name:
                        leaderboard.add_score(current_player_name, final_time)
                    current_active_level = 1
                    # Show credits at the end
                    credits_y = HEIGHT
                    scene = "credits"
                else:
                    current_active_level = 1
                    scene = "menu"
            elif btn_restart_fresh.clicked(event, game_sounds_toggle.enabled):
                # Go to name input for fresh restart
                player_name = ""
                current_active_level = 1
                scene = "name_input"

        elif scene == "settings":
            if music_toggle.clicked(event, game_sounds_toggle.enabled):
                if music_toggle.enabled:
                    pygame.mixer.music.set_volume(1.0)
                else:
                    pygame.mixer.music.set_volume(0.0)
            sound_toggle.clicked(event, game_sounds_toggle.enabled)
            game_sounds_toggle.clicked(event, game_sounds_toggle.enabled)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                scene = "menu"

        elif scene == "credits":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                scene = "menu"

        elif scene == "game":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    scene = "menu"
                if kill_count < WIN_TARGET and player.health > 0:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        start_round = True
                        enemy_instance.speed = 150  # Set speed for single enemy
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                if start_round and kill_count < WIN_TARGET and player.health > 0:
                    if player.stones_left > 0 and player.throw_cooldown <= 0:  # Check cooldown
                        player.stones_left -= 1
                        player.throw_cooldown = 0.5  # Set 0.5 second cooldown (reduced from 1.0)
                        if game_sounds_toggle.enabled and shoot_sound is not None:
                            shoot_sound.play()
                        
                        # Removed attack animation - just shoot without animation
                        
                        angle = math.atan2(mouse_pos[1] - player.rect.centery, mouse_pos[0] - player.rect.centerx)
                        RockProjectile(player.rect.centerx, player.rect.centery, angle, (all_sprites, projectile_sprites))
            
            # --- FIXED LOGIC BRANCH ---
            if kill_count >= WIN_TARGET and btn_level2.clicked(event, game_sounds_toggle.enabled):
                status, checkpoint = start_level_2(
                        bard_companion,
                        sound_toggle.enabled,
                        None,  # checkpoint
                        game_timer,  # timer
                        current_player_name,  # player name
                        game_sounds_toggle.enabled  # game sounds
                )

                if status == "escaped":
                    current_active_level = 2
                    scene = "menu"

                elif status == "completed":
                    current_active_level = 3
                    status_l3 = level3.start_level_3(bard_companion, game_timer, current_player_name, game_sounds_toggle.enabled)
                    if status_l3 == "escaped":
                        current_active_level = 3
                        scene = "menu"
                    elif status_l3 == "completed":
                        # Game completed! Stop timer and add to leaderboard
                        final_time = game_timer.stop()
                        if current_player_name:
                            leaderboard.add_score(current_player_name, final_time)
                        current_active_level = 1
                        # Show credits at the end
                        credits_y = HEIGHT
                        scene = "credits"
                    else:
                        current_active_level = 1
                        scene = "menu"
                
            if (player.health <= 0 or (player.stones_left <= 0 and not projectile_sprites and kill_count < WIN_TARGET)) and btn_restart.clicked(event, game_sounds_toggle.enabled):
                reset_entire_game()

    ### ==================== ###
    ### DRAW AND SCENE LOGIC ###
    ### ==================== ###
    if scene in ["splash", "menu", "credits", "level2_choice", "level3_choice"]:
        bg_scroll_x -= BG_SCROLL_SPEED * dt
        if bg_scroll_x <= -WIDTH:
            bg_scroll_x = 0
        SCREEN.blit(background, (bg_scroll_x, 0))
        SCREEN.blit(background, (bg_scroll_x + WIDTH, 0))
    elif scene == "settings":
        if settings_bg: SCREEN.blit(settings_bg, (0, 0))
        else: SCREEN.fill((40, 40, 60))
    elif scene == "game":
        SCREEN.blit(game_bg, (0, 0))

    if scene == "splash":
        shadow_surf = GAME_LARGE_FONT.render("ACHILLES AND PATROCLUS", True, SHADOW_COLOR)
        SCREEN.blit(shadow_surf, (WIDTH // 2 - shadow_surf.get_width() // 2 + 5, 105))
        title_surf = GAME_LARGE_FONT.render("ACHILLES AND PATROCLUS", True, WHITE)
        SCREEN.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 100))
        
        is_hovered = triangle_bounding_rect.collidepoint(mouse_pos)
        button_color = LIGHT_BLUE if is_hovered else BLUE
        
        pygame.draw.polygon(SCREEN, BLACK, [ (p[0]+4, p[1]+4) for p in triangle_points ]) 
        pygame.draw.polygon(SCREEN, button_color, triangle_points)
        
        start_label = FONT.render("Start", True, WHITE)
        start_shadow = FONT.render("Start", True, SHADOW_COLOR)
        SCREEN.blit(start_shadow, (WIDTH // 2 - start_shadow.get_width() // 2 + 3, triangle_center_y + 70 + 3))
        SCREEN.blit(start_label, (WIDTH // 2 - start_label.get_width() // 2, triangle_center_y + 70))

    elif scene == "name_input":
        SCREEN.blit(menu_shadow, (0, 0))
        
        # Title
        title = FONT.render("ENTER YOUR NAME", False, WHITE)
        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 200))
        
        # Input box
        input_box = pygame.Rect(WIDTH // 2 - 200, 300, 400, 60)
        pygame.draw.rect(SCREEN, WHITE, input_box)
        pygame.draw.rect(SCREEN, BLACK, input_box, 3)
        
        # Player name text
        name_text = FONT.render(player_name + "|", False, BLACK)
        text_rect = name_text.get_rect(center=(input_box.centerx, input_box.centery))
        SCREEN.blit(name_text, text_rect)
        
        # Instructions
        instruction1 = SMALL_FONT.render("Type your name and press ENTER to start", False, WHITE)
        instruction2 = SMALL_FONT.render("Press ESC to go back", False, WHITE)
        SCREEN.blit(instruction1, (WIDTH // 2 - instruction1.get_width() // 2, 400))
        SCREEN.blit(instruction2, (WIDTH // 2 - instruction2.get_width() // 2, 430))
    
    elif scene == "endless_name_input":
        SCREEN.blit(menu_shadow, (0, 0))
        
        # Title
        title = FONT.render("ENDLESS MODE", False, GOLD if hasattr(pygame, 'GOLD') else (255, 215, 0))
        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
        
        subtitle = SMALL_FONT.render("ENTER YOUR NAME", False, WHITE)
        SCREEN.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 220))
        
        # Input box
        input_box = pygame.Rect(WIDTH // 2 - 200, 300, 400, 60)
        pygame.draw.rect(SCREEN, WHITE, input_box)
        pygame.draw.rect(SCREEN, BLACK, input_box, 3)
        
        # Player name text
        name_text = FONT.render(player_name + "|", False, BLACK)
        text_rect = name_text.get_rect(center=(input_box.centerx, input_box.centery))
        SCREEN.blit(name_text, text_rect)
        
        # Instructions
        instruction1 = SMALL_FONT.render("Type your name and press ENTER to start", False, WHITE)
        instruction2 = SMALL_FONT.render("Press ESC to go back", False, WHITE)
        SCREEN.blit(instruction1, (WIDTH // 2 - instruction1.get_width() // 2, 400))
        SCREEN.blit(instruction2, (WIDTH // 2 - instruction2.get_width() // 2, 430))

    elif scene == "menu":
        SCREEN.blit(menu_shadow, (0, 0))
        title_shadow = FONT.render("ACHILLES AND PATROCLUS", False, SHADOW_COLOR)
        SCREEN.blit(title_shadow, (WIDTH // 2 - title_shadow.get_width() // 2 + 3, 83))
        title = FONT.render("ACHILLES AND PATROCLUS", False, WHITE)
        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        
        for button in buttons:
            button.draw()
        
        # Show leaderboard on the right side
        leaderboard_title = SMALL_FONT.render("TOP PLAYERS", False, WHITE)
        SCREEN.blit(leaderboard_title, (WIDTH - 380, 200))
        
        leaderboard_lines = leaderboard.get_leaderboard_text()
        for i, line in enumerate(leaderboard_lines):
            text = SMALL_FONT.render(line, False, WHITE)
            SCREEN.blit(text, (WIDTH - 380, 240 + i * 30))

    elif scene == "level2_choice":
        SCREEN.blit(menu_shadow, (0, 0))
        choice_title = FONT.render("LEVEL 2 PAUSED", False, WHITE)
        SCREEN.blit(choice_title, (WIDTH // 2 - choice_title.get_width() // 2, HEIGHT // 2 - 140))
        btn_continue_l2.draw()
        btn_restart_fresh.draw()

    elif scene == "level3_choice":
        SCREEN.blit(menu_shadow, (0, 0))
        choice_title = FONT.render("LEVEL 3 PAUSED", False, WHITE)
        SCREEN.blit(choice_title, (WIDTH // 2 - choice_title.get_width() // 2, HEIGHT // 2 - 140))
        btn_continue_l3.draw()
        btn_restart_fresh.draw()

    elif scene == "settings":
        title = FONT.render("SETTINGS", False, WHITE)
        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        music_text = SMALL_FONT.render("Music", False, WHITE)
        #sound_text = SMALL_FONT.render("All Sounds", False, WHITE)
        game_sounds_text = SMALL_FONT.render("Game Sound", False, WHITE)
        SCREEN.blit(music_text, (WIDTH // 2 - 240, 230))
        #SCREEN.blit(sound_text, (WIDTH // 2 - 240, 330))
        SCREEN.blit(game_sounds_text, (WIDTH // 2 - 240, 430))
        music_toggle.draw()
        #sound_toggle.draw()
        game_sounds_toggle.draw()
        hint = pygame.font.SysFont("Courier New", 20).render("Press ESC to return", False, WHITE)
        SCREEN.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 550))

    elif scene == "credits":
        credits_lines = [
            "ACHILLES AND PATROCLUS",
            "",
            "Created by Team 2",
            "",
            "Alan Haugh",
            "Dylan Mooney",
            "Cillian Lynch",
            "Jihan Xu",
            "",
            "",
            "Thanks for playing!"
        ]
        credits_y -= 2
        line_spacing = 50
        for i, line in enumerate(credits_lines):
            text = SMALL_FONT.render(line, False, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, credits_y + i * line_spacing))
            SCREEN.blit(text, text_rect)
        if credits_y + (len(credits_lines) * line_spacing) < 0:
            credits_y = HEIGHT

    elif scene == "game":
        is_out_of_ammo = (player.stones_left <= 0 and not projectile_sprites and kill_count < WIN_TARGET)
        
        # Always update Patroclus for healing, regardless of game state
        if player.health > 0:  # Only if player is alive
            healing_result = patroclus.update(dt)
            
            # Handle healing if Patroclus completed healing animation
            if healing_result == "healing_complete":
                old_health = player.health
                player.health = min(player.health + 1, 3)
                print(f"✓ HEALED: Player health {old_health} → {player.health}")
        
        if kill_count < WIN_TARGET and player.health > 0 and not is_out_of_ammo:
            if start_round:
                # Update other sprites 
                player.update(dt)
                enemy_instance.update(dt)  # Update single enemy
                
                # Update projectiles
                projectile_sprites.update(dt)
                
                handle_gameplay_collisions()
                if player.alive(): keep_in_circle(player, circle_center_x, circle_center_y, circle_radius)
                if enemy_instance.alive(): keep_in_circle(enemy_instance, circle_center_x, circle_center_y, circle_radius)
                if patroclus.alive(): keep_in_circle(patroclus, circle_center_x, circle_center_y, circle_radius)

            if start_round and player.alive():
                pygame.draw.line(SCREEN, (0, 255, 0, 150), player.rect.center, mouse_pos, 2)
                pygame.draw.circle(SCREEN, (0, 255, 0), mouse_pos, 6, 1)

            # Draw sprites with animations
            for sprite in all_sprites:
                if sprite == player:
                    player.draw_animated(SCREEN)
                elif sprite == patroclus:
                    patroclus.draw_animated(SCREEN)
                else:
                    SCREEN.blit(sprite.image, sprite.rect)
                    # Draw health bar for Chiron
                    if isinstance(sprite, Chiron):
                        sprite.draw_health_bar(SCREEN)
            
            # Draw blood spray effects
            for spray in blood_sprays[:]:
                if not spray.update(dt):
                    blood_sprays.remove(spray)
                spray.draw(SCREEN)
            
            bard_companion.update()
            bard_companion.draw(SCREEN)

            hud_bubble_width = 40 + (player.health * 32)
            health_bubble = pygame.Surface((hud_bubble_width, 46), pygame.SRCALPHA)
            pygame.draw.rect(health_bubble, (20, 20, 30, 180), (0, 0, hud_bubble_width, 46), border_radius=10)
            pygame.draw.rect(health_bubble, WHITE, (0, 0, hud_bubble_width, 46), width=2, border_radius=10)
            for i in range(player.health):
                health_bubble.blit(heart_surf, (20 + (i * 32), 11))
            SCREEN.blit(health_bubble, (20, 20))

            # Removed ammo display
            kills_txt = GAME_SMALL_FONT.render(f"Kills: {kill_count}/{WIN_TARGET}", True, GREEN if kill_count >= WIN_TARGET else WHITE)
            
            # Add timer display
            if current_player_name and game_timer.is_running:
                timer_txt = GAME_SMALL_FONT.render(f"Time: {game_timer.format_time()}", True, WHITE)
                player_txt = GAME_SMALL_FONT.render(f"Player: {current_player_name}", True, WHITE)
            else:
                timer_txt = None
                player_txt = None
            
            panel_height = 52 + (60 if timer_txt else 0)  # Reduced height since no ammo
            panel_w = kills_txt.get_width() + 40
            if timer_txt:
                panel_w = max(panel_w, timer_txt.get_width() + 40, player_txt.get_width() + 40)
            
            stats_bubble = pygame.Surface((panel_w, panel_height), pygame.SRCALPHA)
            pygame.draw.rect(stats_bubble, (20, 20, 30, 180), (0, 0, panel_w, panel_height), border_radius=12)
            pygame.draw.rect(stats_bubble, WHITE, (0, 0, panel_w, panel_height), width=2, border_radius=12)
            
            y_offset = 12
            stats_bubble.blit(kills_txt, (20, y_offset))  # Kills now at top
            
            if timer_txt and player_txt:
                y_offset += 38
                stats_bubble.blit(timer_txt, (20, y_offset))
                y_offset += 30
                stats_bubble.blit(player_txt, (20, y_offset))
            
            SCREEN.blit(stats_bubble, (WIDTH - panel_w - 20, 20))

            if not start_round:
                prompt_surface = GAME_SMALL_FONT.render("Press SPACE or ENTER to start the round", True, WHITE)
                SCREEN.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, 50)))
                
                # Pause timer while waiting for '1' to start
                if game_timer.is_running and not game_timer.is_paused:
                    game_timer.pause()
            else:
                # Resume timer when round actually starts
                if game_timer.is_running and game_timer.is_paused:
                    game_timer.resume()

            for popup in harm_text_popups[:]:
                popup[2] -= dt
                SCREEN.blit(popup[0], popup[1])
                if popup[2] <= 0:
                    harm_text_popups.remove(popup)

        elif kill_count >= WIN_TARGET:
            if not audio_win_played:
                if game_sounds_toggle.enabled and win_sound: win_sound.play()
                audio_win_played = True
            SCREEN.fill((20, 25, 20))
            text_surface = GAME_FONT.render('You Win!', True, GREEN)
            SCREEN.blit(text_surface, text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
            btn_level2.draw()

        elif player.health <= 0 or is_out_of_ammo:
            if not audio_fail_played:
                if game_sounds_toggle.enabled and fail_sound: fail_sound.play()
                audio_fail_played = True
            SCREEN.fill((25, 20, 20))
            reason_str = "You Ran Out of Ammo!" if is_out_of_ammo else "You Lose!"
            text_surface = GAME_FONT.render(reason_str, True, RED)
            SCREEN.blit(text_surface, text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
            btn_restart.draw()

    pygame.display.flip()