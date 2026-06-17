import math
import sys
import pygame

pygame.init()
pygame.font.init()

# 1280 x 720 Screen Setup
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bottom Zone Bound Game - Clone Edition")
clock = pygame.time.Clock()

# Fonts
FONT_SCORE = pygame.font.SysFont("Arial", 30, bold=True)
FONT_WIN = pygame.font.SysFont("Arial", 80, bold=True)
FONT_BUTTON = pygame.font.SysFont("Arial", 40, bold=True)

# -------------------
# Adjustable Settings
# -------------------
ENEMY_SCALE = 0.3          # Scale animation frames (1.0 = original size)
ENEMY_SPEED = 2            # Enemy walking speed
MIN_DISTANCE = 300         # Distance the enemy tries to keep from the player

# --- SHOOT SPEED COOLDOWN ---
ENEMY_SHOOT_COOLDOWN = 30 

FRAME_DELAY = 2            # Manages enemy walking frame speeds
ARROW_SPEED = 5            # Dodgeable arrow speed
ARROW_SCALE = 0.5          # Change this to resize the arrows (1.0 = original size)

# --- ADJUSTABLE ARROW RANGE ---
ARROW_MAX_RANGE = 500      

PLAYER_SPEED = 5           # Player WASD movement speed
SWORD_SCALE = 0.5          # Visual size scaling factor for your sword asset

# --- SWORD ATTACK RANGE ---
SWORD_RANGE_BONUS = 30     

# Playable Rect Boundaries (1280 x 480 at the bottom)
MIN_X = 0
MAX_X = WIDTH              
MIN_Y = 503                
MAX_Y = HEIGHT             

# Game Rules
WIN_TARGET = 20
START_HEARTS = 5

# --- NEW CLONE TIMER VALUES (60 FPS) ---
CLONE_DURATION_LIMIT = 3 * 60  # 3 seconds active duration
CLONE_COOLDOWN_LIMIT = 6 * 60  # 6 seconds recovery cooldown

# -------------------
# Asset Loading
# -------------------
try:
    background = pygame.image.load("sea.jpg").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except pygame.error:
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill((0, 105, 148))

# Load and scale enemy attack animation
attack_frames = []
for i in range(1, 11):
    frame = pygame.image.load(f"ac{i}.png").convert_alpha()
    new_size = (int(frame.get_width() * ENEMY_SCALE), int(frame.get_height() * ENEMY_SCALE))
    attack_frames.append(pygame.transform.scale(frame, new_size))

# Load projectile and scale it dynamically
projectile_raw_img = pygame.image.load("arrow.png").convert_alpha()
arrow_w = int(projectile_raw_img.get_width() * ARROW_SCALE)
arrow_h = int(projectile_raw_img.get_height() * ARROW_SCALE)
projectile_base_img = pygame.transform.scale(projectile_raw_img, (arrow_w, arrow_h))

# Load player image
player_img = pygame.image.load("player.png").convert_alpha()

# Load and correctly scale sword swing frames
sword_frames = []
for i in range(1, 4):
    frame = pygame.image.load(f"sword{i}.png").convert_alpha()
    new_size = (int(frame.get_width() * SWORD_SCALE), int(frame.get_height() * SWORD_SCALE))
    sword_frames.append(pygame.transform.scale(frame, new_size))

# -------------------
# Helper to Draw Red Heart Vector Icons
# -------------------
def draw_heart(surface, x, y, size=24):
    """Draws a crisp geometric red heart onto the target screen position"""
    color = (255, 40, 60)
    # Left Circle
    pygame.draw.circle(surface, color, (x - size // 4, y - size // 4), size // 4)
    # Right Circle
    pygame.draw.circle(surface, color, (x + size // 4, y - size // 4), size // 4)
    # Bottom Triangle tip connection Points
    points = [(x - size // 2, y - size // 6), (x + size // 2, y - size // 6), (x, y + size // 2)]
    pygame.draw.polygon(surface, color, points)

# -------------------
# Game State Reset Function
# -------------------
def reset_game():
    global enemy_x, enemy_y, player_x, player_y, kill_count, heart_value
    global current_frame, frame_counter, is_swinging, sword_frame_idx
    global sword_counter, projectile_spawned, has_hit_enemy, projectiles
    global game_won, game_lost, flash_timer, shoot_timer
    global clones_active, clone_duration_timer, clone_cooldown_timer

    enemy_x = 200
    enemy_y = 500  
    player_x = 900
    player_y = 500  
    
    kill_count = 0
    heart_value = START_HEARTS
    
    current_frame = 0
    frame_counter = 0
    projectile_spawned = False
    
    is_swinging = False
    sword_frame_idx = 0
    sword_counter = 0
    has_hit_enemy = False
    
    projectiles = []
    game_won = False
    game_lost = False
    flash_timer = 0
    shoot_timer = 0  
    
    # Reset Timer State Variables
    clones_active = False
    clone_duration_timer = 0
    clone_cooldown_timer = 0

# Initialize variables on launch
reset_game()

# -------------------
# Main Game Loop
# -------------------
running = True

while running:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_clicked = True
        
        if event.type == pygame.KEYDOWN and not game_won and not game_lost:
            # Trigger sword slash when Space is pressed
            if event.key == pygame.K_SPACE and not is_swinging:
                is_swinging = True
                sword_frame_idx = 0
                sword_counter = 0
                has_hit_enemy = False
            
            # Deploy Clones if they aren't active and not recovering on cooldown
            if event.key == pygame.K_u:
                if not clones_active and clone_cooldown_timer == 0:
                    clones_active = True
                    clone_duration_timer = CLONE_DURATION_LIMIT

    # Update active gameplay conditions
    if not game_won and not game_lost:
        # -------------------
        # Update Ability Core Clock Timers
        # -------------------
        if clones_active:
            clone_duration_timer -= 1
            if clone_duration_timer <= 0:
                clones_active = False
                clone_cooldown_timer = CLONE_COOLDOWN_LIMIT
        elif clone_cooldown_timer > 0:
            clone_cooldown_timer -= 1

        # -------------------
        # Player Movement (WASD)
        # -------------------
        keys = pygame.key.get_pressed()
        player_moving = False
        
        if keys[pygame.K_w]:
            player_y -= PLAYER_SPEED
            player_moving = True
        if keys[pygame.K_s]:
            player_y += PLAYER_SPEED
            player_moving = True
        if keys[pygame.K_a]:
            player_x -= PLAYER_SPEED
            player_moving = True
        if keys[pygame.K_d]:
            player_x += PLAYER_SPEED
            player_moving = True

        # Clamp Player to boundaries
        player_x = max(MIN_X, min(MAX_X, player_x))
        player_y = max(MIN_Y, min(MAX_Y, player_y))

        # -------------------
        # Calculate Combat Formations Positions
        # -------------------
        positions_to_check = [(player_x, player_y)] 
        if clones_active:
            clone1_x, clone1_y = player_x + 60, player_y - 45  
            clone2_x, clone2_y = player_x + 60, player_y + 45  
            positions_to_check.append((clone1_x, clone1_y))
            positions_to_check.append((clone2_x, clone2_y))

        # -------------------
        # Enemy AI Movement
        # -------------------
        ex_dx = player_x - enemy_x
        ex_dy = player_y - enemy_y
        dist_to_player = math.hypot(ex_dx, ex_dy)

        if player_moving and dist_to_player > MIN_DISTANCE:
            if dist_to_player == 0: 
                dist_to_player = 1
            
            enemy_x += (ex_dx / dist_to_player) * ENEMY_SPEED
            enemy_y += (ex_dy / dist_to_player) * ENEMY_SPEED

        # Clamp Enemy to boundaries
        enemy_x = max(MIN_X, min(MAX_X, enemy_x))
        enemy_y = max(MIN_Y, min(MAX_Y, enemy_y))

        # -------------------
        # Sword Animation Tracking & Frame Updates
        # -------------------
        if is_swinging:
            sword_counter += 1
            if sword_counter >= 4:  
                sword_counter = 0
                sword_frame_idx += 1
                if sword_frame_idx >= len(sword_frames):
                    is_swinging = False
                    sword_frame_idx = 0

        # -------------------
        # Attack Animation & Dynamic Arrow Spawning
        # -------------------
        frame_counter += 1
        if frame_counter >= FRAME_DELAY:  
            frame_counter = 0
            current_frame += 1

            if current_frame >= len(attack_frames):
                current_frame = 0

        # Run firing speed check separate from walk loops
        shoot_timer += 1
        if shoot_timer >= ENEMY_SHOOT_COOLDOWN:
            shoot_timer = 0  
            
            spawn_x = enemy_x + (60 * ENEMY_SCALE)
            spawn_y = enemy_y + (20 * ENEMY_SCALE)
            
            dx = player_x - spawn_x
            dy = player_y - spawn_y
            distance = math.hypot(dx, dy)
            if distance == 0: 
                distance = 1
                
            vx = (dx / distance) * ARROW_SPEED
            vy = (dy / distance) * ARROW_SPEED
            angle = -math.degrees(math.atan2(dy, dx))

            projectiles.append({
                "x": spawn_x,
                "y": spawn_y,
                "vx": vx,
                "vy": vy,
                "angle": angle,
                "distance_traveled": 0  
            })

        # -------------------
        # Collisions & Projectile Updates
        # -------------------
        enemy_image = attack_frames[current_frame]
        enemy_rect = enemy_image.get_rect(center=(int(enemy_x), int(enemy_y)))
        
        # Build collection of weapon hitboxes across active entities
        active_sword_hitboxes = []
        for pos in positions_to_check:
            px, py = pos
            current_sword_img = sword_frames[sword_frame_idx]
            sword_rect = current_sword_img.get_rect(center=(int(px - 45), int(py)))
            sword_hitbox = sword_rect.inflate(SWORD_RANGE_BONUS * 2, SWORD_RANGE_BONUS * 2)
            active_sword_hitboxes.append(sword_hitbox)

        # Check if any swinging sword in the entire group sweeps across the enemy
        if is_swinging and not has_hit_enemy:
            for hitbox in active_sword_hitboxes:
                if hitbox.colliderect(enemy_rect):
                    # --- DYNAMIC SCORE INCREMENT ---
                    # Awards 3 kills if claws/clones are deployed; otherwise standard 1 kill.
                    if clones_active:
                        kill_count += 3
                    else:
                        kill_count += 1
                        
                    has_hit_enemy = True 
                    if kill_count >= WIN_TARGET:
                        game_won = True
                    break

        # Update arrows and process dual collision filters (Sword Range Block vs Player Damage)
        projectiles_to_keep = []
        for projectile in projectiles:
            projectile["x"] += projectile["vx"]
            projectile["y"] += projectile["vy"]
            
            step_distance = math.hypot(projectile["vx"], projectile["vy"])
            projectile["distance_traveled"] += step_distance

            arrow_rect = projectile_base_img.get_rect(center=(int(projectile["x"]), int(projectile["y"])))
            
            # Action 1: If any deployed entities swing and parry an arrow, wipe it out
            blocked_by_sword = False
            if is_swinging:
                for hitbox in active_sword_hitboxes:
                    if hitbox.colliderect(arrow_rect):
                        blocked_by_sword = True
                        break
            if blocked_by_sword:
                continue  
            
            # Action 2: Check if projectile hits any physical entity body space
            hit_entity = False
            for pos in positions_to_check:
                px, py = pos
                ent_rect = player_img.get_rect(center=(int(px), int(py)))
                if arrow_rect.colliderect(ent_rect):
                    hit_entity = True
                    break
            
            if hit_entity:
                heart_value -= 1
                flash_timer = 5 
                if heart_value <= 0:
                    game_lost = True
                continue 
                
            # Keep arrow safe within range limits
            if (-50 < projectile["x"] < WIDTH + 50 and 
                -50 < projectile["y"] < HEIGHT + 50 and 
                projectile["distance_traveled"] < ARROW_MAX_RANGE):
                projectiles_to_keep.append(projectile)

        projectiles = projectiles_to_keep

    # -------------------
    # Render / Drawing
    # -------------------
    screen.blit(background, (0, 0))

    # Render Active Entities Layer (Leader and Flank Shadows)
    for pos in positions_to_check:
        px, py = pos
        ent_draw_rect = player_img.get_rect(center=(int(px), int(py)))
        screen.blit(player_img, ent_draw_rect)

        # Synchronize weapon drawing directly onto the entity node coordinates
        if is_swinging:
            current_sword_img = sword_frames[sword_frame_idx]
            sword_draw_rect = current_sword_img.get_rect(center=(int(px - 30), int(py)))
            screen.blit(current_sword_img, sword_draw_rect)
        else:
            idle_sword_img = sword_frames[0]
            sword_draw_rect = idle_sword_img.get_rect(center=(int(px - 15), int(py - 5)))
            screen.blit(idle_sword_img, sword_draw_rect)

    # Render Enemy
    enemy_rect = attack_frames[current_frame].get_rect(center=(int(enemy_x), int(enemy_y)))
    screen.blit(attack_frames[current_frame], enemy_rect)

    # Draw arrows scaled to current parameters
    for projectile in projectiles:
        rotated_arrow = pygame.transform.rotate(projectile_base_img, projectile["angle"])
        projectile_rect = rotated_arrow.get_rect(center=(int(projectile["x"]), int(projectile["y"])))
        screen.blit(rotated_arrow, projectile_rect)

    # Damage Flash Indicator Layer
    if flash_timer > 0:
        flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        flash_surf.fill((255, 0, 0, 75)) 
        screen.blit(flash_surf, (0, 0))
        flash_timer -= 1

    # UI: HUD Displays (Score Counter text string)
    score_surface = FONT_SCORE.render(f"Kills: {kill_count} / {WIN_TARGET}", True, (255, 255, 255))
    screen.blit(score_surface, (20, 20))
    
    # --- UI: RENDER CLONE SPECIAL COOLDOWN TEXT METRICS ---
    if clones_active:
        time_left = max(0.0, clone_duration_timer / 60.0)
        cooldown_text = f"CLONES ACTIVE: {time_left:.1f}s"
        cooldown_color = (0, 255, 255)  # Cyan
    elif clone_cooldown_timer > 0:
        time_left = max(0.0, clone_cooldown_timer / 60.0)
        cooldown_text = f"CLONE COOLDOWN: {time_left:.1f}s"
        cooldown_color = (255, 165, 0)  # Orange
    else:
        cooldown_text = "CLONES SQUAD [U]: READY"
        cooldown_color = (0, 255, 0)    # Green

    cooldown_surface = FONT_SCORE.render(cooldown_text, True, cooldown_color)
    screen.blit(cooldown_surface, (WIDTH - cooldown_surface.get_width() - 20, 20))
    
    # UI: Draw Red Heart Icons inline across the screen row space
    for h in range(max(0, heart_value)):
        draw_heart(screen, x=35 + (h * 35), y=75, size=24)

    # UI: Victory Sequence
    if game_won:
        win_surface = FONT_WIN.render("YOU WIN!", True, (0, 255, 100))
        win_rect = win_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        screen.blit(win_surface, win_rect)
        
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False

    # UI: Defeat State Menu Interaction Loop
    if game_lost:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 20, 20, 200))
        screen.blit(overlay, (0, 0))

        lost_surface = FONT_WIN.render("Lost try again", True, (255, 50, 50))
        lost_rect = lost_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        screen.blit(lost_surface, lost_rect)

        btn_width, btn_height = 240, 65
        btn_rect = pygame.Rect((WIDTH // 2 - btn_width // 2, HEIGHT // 2 + 50), (btn_width, btn_height))
        
        if btn_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (80, 80, 80), btn_rect, border_radius=10) 
            if mouse_clicked:
                reset_game() 
        else:
            pygame.draw.rect(screen, (45, 45, 45), btn_rect, border_radius=10) 
            
        pygame.draw.rect(screen, (200, 200, 200), btn_rect, 3, border_radius=10) 

        btn_text = FONT_BUTTON.render("Try Again", True, (255, 255, 255))
        btn_text_rect = btn_text.get_rect(center=btn_rect.center)
        screen.blit(btn_text, btn_text_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()