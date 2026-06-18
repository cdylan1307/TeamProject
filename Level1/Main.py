import pygame
import sys
from os.path import join
import os
import random
import math

from level2 import start_level_2
import level3  # Import Level 3 package

### ========================================== ###
### 1. INITIALIZATION & AUDIO SETUP            ###
### ========================================== ###
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1280, 720  
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Game - Master Engine")

FPS = 60
clock = pygame.time.Clock()

try:
    pygame.mixer.music.load("backgroundMusic.mp3")
    pygame.mixer.music.play(loops=-1)
except pygame.error:
    print("Warning: backgroundMusic.mp3 not found or could not be loaded.")

def load_sfx(filename):
    if os.path.exists(filename):
        try: return pygame.mixer.Sound(filename)
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
PLACEHOLDER_BG = (25, 25, 35)

menu_shadow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
menu_shadow.fill((0, 0, 0, 120))

### ========================================== ###
### 3. ASSETS & SCROLLING CONFIGURATION        ###
### ========================================== ###
background = None
if os.path.exists("jungle.jpg"):
    background = pygame.image.load("jungle.jpg").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
else:
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(PLACEHOLDER_BG)

bg_scroll_x = 0
BG_SCROLL_SPEED = 40  

settings_bg = None
if os.path.exists("settings.png"):
    settings_bg = pygame.image.load("settings.png").convert()
    settings_bg = pygame.transform.scale(settings_bg, (WIDTH, HEIGHT))

game_bg = None
if os.path.exists("images/lv1background.png"):
    game_bg = pygame.image.load("images/lv1background.png").convert()
elif os.path.exists("forest.png"):
    game_bg = pygame.image.load("forest.png").convert()

if game_bg:
    game_bg = pygame.transform.scale(game_bg, (WIDTH, HEIGHT))
else:
    game_bg = pygame.Surface((WIDTH, HEIGHT))
    game_bg.fill((40, 40, 40))

try:
    rock_image = pygame.image.load("rock.png").convert_alpha()
    rock_image = pygame.transform.scale(rock_image, (25, 25))
except FileNotFoundError:
    rock_image = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.circle(rock_image, (120, 120, 120), (10, 10), 10)

heart_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
pygame.draw.circle(heart_surf, (220, 40, 40), (6, 8), 6)
pygame.draw.circle(heart_surf, (220, 40, 40), (18, 8), 6)
pygame.draw.polygon(heart_surf, (220, 40, 40), [(0, 10), (12, 24), (24, 10)])

all_sprites = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()
projectile_sprites = pygame.sprite.Group()

chiron_walk_frames = []
for i in range(6):
    try:
        chiron_walk_frames.append(pygame.image.load(join("animations", "Chiron", "Walking", f"Chiron_Walk_{i}.png")).convert_alpha())
    except FileNotFoundError:
        fallback = pygame.Surface((50, 50))
        fallback.fill((255, 0, 0))
        chiron_walk_frames.append(fallback)

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

        pygame.draw.rect(SCREEN, BLACK, self.rect.inflate(6, 6))
        pygame.draw.rect(SCREEN, current_color, self.rect)

        text_surface = FONT.render(self.text, False, WHITE)
        SCREEN.blit(
            text_surface,
            (
                self.rect.centerx - text_surface.get_width() // 2,
                self.rect.centery - text_surface.get_height() // 2,
            ),
        )

    def clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if click_sound: click_sound.play()
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

    def clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if click_sound: click_sound.play()
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
        try:
            self.image = pygame.image.load(join("images", "player.png")).convert_alpha()
        except FileNotFoundError:
            self.image = pygame.Surface((50, 50))
            self.image.fill((0, 255, 0))
            
        self.rect = self.image.get_rect(center = (WIDTH / 2, HEIGHT / 2))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2()
        self.speed = 300
        self.health = 3 
        self.stones_left = 20  
        self.invincible_timer = 0
    
    def update(self, dt):
        if self.invincible_timer > 0:
            self.invincible_timer -= dt
        self.movement(dt)
 
    def movement(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = (int(keys[pygame.K_RIGHT]) or int(keys[pygame.K_d])) - (int(keys[pygame.K_LEFT]) or int(keys[pygame.K_a]))
        self.direction.y = (int(keys[pygame.K_DOWN]) or int(keys[pygame.K_s])) - (int(keys[pygame.K_UP]) or int(keys[pygame.K_w]))
        
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
        self.rect.center += self.direction * self.speed * dt


class Chiron(pygame.sprite.Sprite):
    def __init__(self, groups, speed, player_ref, border_rect):
        super().__init__(groups)
        self.group = groups
        self.player = player_ref
        self.scale = 0.75
        self.border = border_rect

        if os.path.exists(join("animations","Chiron","Walking","Chiron_Walk_0.png")):
            try:
                self.image = pygame.image.load(join("animations","Chiron","Walking","Chiron_Walk_0.png")).convert_alpha()
                self.image = pygame.transform.scale_by(self.image, self.scale)
            except:
                self.image = pygame.Surface((60, 60))
                self.image.fill((255, 0, 0))
        else:
            self.image = pygame.Surface((60, 60))
            self.image.fill((255, 0, 0))

        self.teleport_randomly()
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = speed
        self.frames = chiron_walk_frames
        self.frame_index = 0

    def teleport_randomly(self):
        self.rect = self.image.get_rect(
            center=(
                random.randint(self.border.left + 40, self.border.right - 40),
                random.randint(self.border.top + 40, self.border.bottom - 40)
            )
        )

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


class Patroclus(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.group = groups
        try:
            self.image = pygame.image.load(join("images", "player.png")).convert_alpha()
        except FileNotFoundError:
            self.image = pygame.Surface((40, 40))
            self.image.fill((200, 200, 255))
            
        self.rect = self.image.get_rect(center = (WIDTH / 2 - 20, HEIGHT / 2 + 20))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2()
        self.speed = 260 

    def update(self, dt):
        target_x = player.rect.x - 40
        target_y = player.rect.y + 40
        enemy_vector = pygame.math.Vector2(target_x - self.rect.x, target_y - self.rect.y)
        
        if enemy_vector.length() > 5:  
            enemy_vector = enemy_vector.normalize()
            self.rect.center += enemy_vector * self.speed * dt


### ========================================== ###
### 5. INSTANTIATION & INITIAL VARIABLE STATES ###
### ========================================== ###
border = pygame.Rect(200, 100, 880, 520)

buttons = [
    PixelButton("START", WIDTH // 2 - 100, 240, 200, 60),
    PixelButton("SETTINGS", WIDTH // 2 - 100, 320, 200, 60),
    PixelButton("CREDITS", WIDTH // 2 - 100, 400, 200, 60),
    PixelButton("QUIT", WIDTH // 2 - 100, 480, 200, 60),
]

music_toggle = ToggleButton(WIDTH // 2 - 20, 260)
sound_toggle = ToggleButton(WIDTH // 2 - 20, 360)

btn_level2 = PixelButton("GO TO LEVEL 2", WIDTH // 2 - 150, HEIGHT // 2 + 50, 300, 60, GREEN, (60, 220, 100))
btn_restart = PixelButton("RESTART GAME", WIDTH // 2 - 150, HEIGHT // 2 + 50, 300, 60, RED, (220, 70, 70))

# Level UI Context Managers
btn_continue_l2 = PixelButton("CONTINUE L2", WIDTH // 2 - 150, HEIGHT // 2 - 40, 300, 60, BLUE, LIGHT_BLUE)
btn_continue_l3 = PixelButton("CONTINUE L3", WIDTH // 2 - 150, HEIGHT // 2 - 40, 300, 60, BLUE, LIGHT_BLUE)
btn_restart_fresh = PixelButton("RESTART", WIDTH // 2 - 150, HEIGHT // 2 + 40, 300, 60, RED, (220, 70, 70))

scene = "splash"  
credits_y = HEIGHT
start_round = False
current_active_level = 1

kill_count = 0
WIN_TARGET = 3 
harm_text_popups = []  

audio_win_played = False
audio_fail_played = False

bard_companion = Bard(window_height=HEIGHT, scale=1.35)

player = Player(all_sprites)
patroclus = Patroclus(all_sprites)
enemy_instance = Chiron((all_sprites, enemy_sprites), 0, player, border)

triangle_center_x = WIDTH // 2
triangle_center_y = HEIGHT // 2 - 10
triangle_points = [
    (triangle_center_x - 30, triangle_center_y - 40), 
    (triangle_center_x - 30, triangle_center_y + 40), 
    (triangle_center_x + 40, triangle_center_y)
]
triangle_bounding_rect = pygame.Rect(triangle_center_x - 35, triangle_center_y - 45, 80, 90)

def reset_entire_game():
    global kill_count, harm_text_popups, start_round, player, enemy_instance, patroclus, audio_win_played, audio_fail_played
    all_sprites.empty()
    enemy_sprites.empty()
    projectile_sprites.empty()
    kill_count = 0
    harm_text_popups.clear()
    start_round = False
    audio_win_played = False
    audio_fail_played = False
    player = Player(all_sprites)
    patroclus = Patroclus(all_sprites)
    enemy_instance = Chiron((all_sprites, enemy_sprites), 0, player, border)
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.play(loops=-1)
    except: pass

def handle_gameplay_collisions():
    global kill_count, enemy_instance
    if not player.alive(): return

    projectile_hits = pygame.sprite.spritecollide(enemy_instance, projectile_sprites, True, pygame.sprite.collide_mask)
    if projectile_hits and enemy_instance.alive():
        enemy_instance.kill()
        kill_count += 1
        if kill_count < WIN_TARGET:
            enemy_instance = Chiron((all_sprites, enemy_sprites), 150, player, border)

    if pygame.sprite.collide_mask(player, enemy_instance) and enemy_instance.alive():
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
                    if click_sound: click_sound.play()
                    scene = "menu"

        elif scene == "menu":
            if event.type == pygame.KEYDOWN:
                # SECRET HOTKEY 'K': Jump instantly into Level 3 from the menu screen
                if event.key == pygame.K_k:
                    current_active_level = 3
                    status = level3.start_level_3(bard_companion)
                    if status == "escaped":
                        scene = "level3_choice"
                    else:
                        scene = "menu"

            if buttons[0].clicked(event):
                if current_active_level == 2:
                    scene = "level2_choice"
                elif current_active_level == 3:
                    scene = "level3_choice"
                else:
                    reset_entire_game()
                    scene = "game"
            elif buttons[1].clicked(event):
                scene = "settings"
            elif buttons[2].clicked(event):
                credits_y = HEIGHT
                scene = "credits"
            elif buttons[3].clicked(event):
                pygame.quit()
                sys.exit()

        elif scene == "level2_choice":
            if btn_continue_l2.clicked(event):
                status, checkpoint = start_level_2(
                    bard_companion,
                    sound_toggle.enabled
                )

                if status == "escaped":
                    current_active_level = 2
                    scene = "menu"

                elif status == "completed":
                    current_active_level = 3
                    status_l3 = level3.start_level_3(bard_companion)
                    scene = "level3_choice" if status_l3 == "escaped" else "menu"
            elif btn_restart_fresh.clicked(event):
                current_active_level = 1
                reset_entire_game()
                scene = "game"

        elif scene == "level3_choice":
            if btn_continue_l3.clicked(event):
                status = level3.start_level_3(bard_companion)
                if status == "escaped":
                    current_active_level = 3
                    scene = "menu"
                else:
                    current_active_level = 1
                    scene = "menu"
            elif btn_restart_fresh.clicked(event):
                current_active_level = 1
                reset_entire_game()
                scene = "game"

        elif scene == "settings":
            if music_toggle.clicked(event):
                if music_toggle.enabled:
                    pygame.mixer.music.set_volume(1.0)
                else:
                    pygame.mixer.music.set_volume(0.0)
            sound_toggle.clicked(event)
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
                    if event.key == pygame.K_1:
                        start_round = True
                        enemy_instance.speed = 150
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: 
                if start_round and kill_count < WIN_TARGET and player.health > 0:
                    if player.stones_left > 0:
                        player.stones_left -= 1
                        if sound_toggle.enabled and shoot_sound is not None:
                            shoot_sound.play()
                        
                        angle = math.atan2(mouse_pos[1] - player.rect.centery, mouse_pos[0] - player.rect.centerx)
                        RockProjectile(player.rect.centerx, player.rect.centery, angle, (all_sprites, projectile_sprites))
            
            # --- FIXED LOGIC BRANCH ---
            if kill_count >= WIN_TARGET and btn_level2.clicked(event):
                status, checkpoint = start_level_2(
                        bard_companion,
                        sound_toggle.enabled
                )

                if status == "escaped":
                    current_active_level = 2
                    scene = "menu"

                elif status == "completed":
                    current_active_level = 3
                    status_l3 = level3.start_level_3(bard_companion)
                    if status_l3 == "escaped":
                        current_active_level = 3
                        scene = "menu"
                    else:
                        current_active_level = 1
                        scene = "menu"
                
            if (player.health <= 0 or (player.stones_left <= 0 and not projectile_sprites and kill_count < WIN_TARGET)) and btn_restart.clicked(event):
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
        SCREEN.blit(menu_shadow, (0, 0))
        shadow_surf = GAME_LARGE_FONT.render("PIXEL GAME", True, SHADOW_COLOR)
        SCREEN.blit(shadow_surf, (WIDTH // 2 - shadow_surf.get_width() // 2 + 5, 105))
        title_surf = GAME_LARGE_FONT.render("PIXEL GAME", True, WHITE)
        SCREEN.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 100))
        
        is_hovered = triangle_bounding_rect.collidepoint(mouse_pos)
        button_color = LIGHT_BLUE if is_hovered else BLUE
        
        pygame.draw.polygon(SCREEN, BLACK, [ (p[0]+4, p[1]+4) for p in triangle_points ]) 
        pygame.draw.polygon(SCREEN, button_color, triangle_points)
        
        start_label = FONT.render("Start", True, WHITE)
        SCREEN.blit(start_label, (WIDTH // 2 - start_label.get_width() // 2, triangle_center_y + 70))

    elif scene == "menu":
        SCREEN.blit(menu_shadow, (0, 0))
        title_shadow = FONT.render("PIXEL GAME", False, SHADOW_COLOR)
        SCREEN.blit(title_shadow, (WIDTH // 2 - title_shadow.get_width() // 2 + 3, 83))
        title = FONT.render("PIXEL GAME", False, WHITE)
        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        for button in buttons:
            button.draw()

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
        sound_text = SMALL_FONT.render("Game Sounds", False, WHITE)
        SCREEN.blit(music_text, (WIDTH // 2 - 240, 270))
        SCREEN.blit(sound_text, (WIDTH // 2 - 240, 370))
        music_toggle.draw()
        sound_toggle.draw()
        hint = pygame.font.SysFont("Courier New", 20).render("Press ESC to return", False, WHITE)
        SCREEN.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 550))

    elif scene == "credits":
        credits_lines = ["PIXEL GAME", "", "Created by Team 2", "", "Alan Haugh", "Dylan Mooney", "Cillian Lynch", "Jihan Xu"]
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
        
        if kill_count < WIN_TARGET and player.health > 0 and not is_out_of_ammo:
            if start_round:
                all_sprites.update(dt)
                handle_gameplay_collisions()
                if player.alive(): player.rect.clamp_ip(border)
                if enemy_instance.alive(): enemy_instance.rect.clamp_ip(border)
                if patroclus.alive(): patroclus.rect.clamp_ip(border)

            if start_round and player.alive():
                pygame.draw.line(SCREEN, (0, 255, 0, 150), player.rect.center, mouse_pos, 2)
                pygame.draw.circle(SCREEN, (0, 255, 0), mouse_pos, 6, 1)

            all_sprites.draw(SCREEN)
            bard_companion.update()
            bard_companion.draw(SCREEN)

            hud_bubble_width = 40 + (player.health * 32)
            health_bubble = pygame.Surface((hud_bubble_width, 46), pygame.SRCALPHA)
            pygame.draw.rect(health_bubble, (20, 20, 30, 180), (0, 0, hud_bubble_width, 46), border_radius=10)
            pygame.draw.rect(health_bubble, WHITE, (0, 0, hud_bubble_width, 46), width=2, border_radius=10)
            for i in range(player.health):
                health_bubble.blit(heart_surf, (20 + (i * 32), 11))
            SCREEN.blit(health_bubble, (20, 20))

            ammo_txt = GAME_SMALL_FONT.render(f"Stones Left: {player.stones_left}", True, WHITE)
            kills_txt = GAME_SMALL_FONT.render(f"Kills: {kill_count}/{WIN_TARGET}", True, GREEN if kill_count >= WIN_TARGET else WHITE)
            
            panel_w = max(ammo_txt.get_width(), kills_txt.get_width()) + 40
            stats_bubble = pygame.Surface((panel_w, 90), pygame.SRCALPHA)
            pygame.draw.rect(stats_bubble, (20, 20, 30, 180), (0, 0, panel_w, 90), border_radius=12)
            pygame.draw.rect(stats_bubble, WHITE, (0, 0, panel_w, 90), width=2, border_radius=12)
            stats_bubble.blit(ammo_txt, (20, 12))
            stats_bubble.blit(kills_txt, (20, 50))
            SCREEN.blit(stats_bubble, (WIDTH - panel_w - 20, 20))

            if not start_round:
                prompt_surface = GAME_SMALL_FONT.render("Press '1' to start the round", True, WHITE)
                SCREEN.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, 50)))

            for popup in harm_text_popups[:]:
                popup[2] -= dt
                SCREEN.blit(popup[0], popup[1])
                if popup[2] <= 0:
                    harm_text_popups.remove(popup)

        elif kill_count >= WIN_TARGET:
            if not audio_win_played:
                if win_sound: win_sound.play()
                audio_win_played = True
            SCREEN.fill((20, 25, 20))
            text_surface = GAME_FONT.render('You Win!', True, GREEN)
            SCREEN.blit(text_surface, text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
            btn_level2.draw()

        elif player.health <= 0 or is_out_of_ammo:
            if not audio_fail_played:
                if fail_sound: fail_sound.play()
                audio_fail_played = True
            SCREEN.fill((25, 20, 20))
            reason_str = "You Ran Out of Ammo!" if is_out_of_ammo else "You Lose!"
            text_surface = GAME_FONT.render(reason_str, True, RED)
            SCREEN.blit(text_surface, text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
            btn_restart.draw()

    pygame.display.flip()