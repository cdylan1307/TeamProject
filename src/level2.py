import math
import sys
import os
import pygame
import random
from .level3 import start_level_3
from .dealer import Dealer  # Import the Dealer class
from . import cutscene  # Import cutscene module
from .animation_system import AnimatedPlayer, AnimatedPatroclus  # Import animation system

WIDTH, HEIGHT = 1280, 720
MIN_X, MAX_X = 0, WIDTH
MIN_Y, MAX_Y = 450, HEIGHT - 100 #-100, -150, move up the bottom

def draw_heart(surface, x, y, size=24):
    color = (255, 40, 60)
    pygame.draw.circle(surface, color, (x - size // 4, y - size // 4), size // 4)
    pygame.draw.circle(surface, color, (x + size // 4, y - size // 4), size // 4)
    points = [(x - size // 2, y - size // 6), (x + size // 2, y - size // 6), (x, y + size // 2)]
    pygame.draw.polygon(surface, color, points)

def draw_health_bar(surface, x, y, current_health, max_health, width=50, height=6):
    """Draw a health bar above an enemy"""
    BLACK = (0, 0, 0)
    RED = (180, 50, 50)
    GREEN = (40, 180, 80)
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

def start_level_2(bard, sfx_enabled=True, checkpoint=None, timer=None, player_name="", game_sounds_enabled=True):
    # Pause timer during cutscene
    if timer and timer.is_running:
        timer.pause()
    
    # Play Level 2 cutscene before starting the level
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Achilles and Patroclus - Level 2")
    
    cutscene_result = cutscene.play_cutscene(screen, "level2")
    # Continue regardless of whether player skips or watches
    
    # Resume timer after cutscene
    if timer and timer.is_running:
        timer.resume()
    
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("Achilles and Patroclus - Level 2")
    clock = pygame.time.Clock()

    FONT_SCORE = pygame.font.SysFont("Arial", 30, bold=True)
    FONT_WIN = pygame.font.SysFont("Arial", 80, bold=True)
    FONT_BUTTON = pygame.font.SysFont("Arial", 40, bold=True)

    MIN_DISTANCE = 300
    ARROW_SPEED = 5
    ARROW_SCALE = 0.8
    PLAYER_SCALE = 1.2   
    PLAYER_SPEED = 5
    SWORD_SCALE = 0.5 * PLAYER_SCALE
    
    SWORD_ATTACK_RANGE = 95 
    PLAYER_BODY_RADIUS = 25   

    # EASIER MODIFICATION CRITERIA
    WIN_TARGET = 1  # Only need to defeat 1 archer
    START_HEARTS = 3  # Increased back to 3
    ARCHER_HEALTH = 5  # Archer health (increased from 3 to 5 hits)
    SWORD_ATTACK_COOLDOWN = 0.5  # 0.5 second cooldown for sword attacks

    arrow_sound = pygame.mixer.Sound("audio/arrow.mp3") if os.path.exists("audio/arrow.mp3") else None
    sword_sound = pygame.mixer.Sound("audio/sword.mp3") if os.path.exists("audio/sword.mp3") else None
    win_sound   = pygame.mixer.Sound("audio/win.mp3") if os.path.exists("audio/win.mp3") else None
    fail_sound  = pygame.mixer.Sound("audio/fail.mp3") if os.path.exists("audio/fail.mp3") else None
    buy_sound   = pygame.mixer.Sound("audio/buy.mp3") if os.path.exists("audio/buy.mp3") else None
    click_sound = pygame.mixer.Sound("audio/mouse.mp3") if os.path.exists("audio/mouse.mp3") else None

    try:
        background = pygame.image.load("backgrounds/sea.jpg").convert()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    except pygame.error:
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill((0, 105, 148))

    try:
        projectile_base_img = pygame.image.load("sprites/arrow.png").convert_alpha()
        arrow_w = int(projectile_base_img.get_width() * ARROW_SCALE)
        arrow_h = int(projectile_base_img.get_height() * ARROW_SCALE)
        projectile_base_img = pygame.transform.scale(projectile_base_img, (arrow_w, arrow_h))
    except pygame.error:
        projectile_base_img = pygame.Surface((15, 5))
        projectile_base_img.fill((200, 200, 200))

    try:
        player_raw_img = pygame.image.load("sprites/player.png").convert_alpha()
        player_w = int(player_raw_img.get_width() * PLAYER_SCALE)
        player_h = int(player_raw_img.get_height() * PLAYER_SCALE)
        player_img = pygame.transform.scale(player_raw_img, (player_w, player_h))
    except pygame.error:
        player_img = pygame.Surface((30, 30))
        player_img.fill((0, 255, 0))

    sword_frames = []
    for i in range(1, 4):
        try:
            frame = pygame.image.load(f"sprites/sword{i}.png").convert_alpha()
            new_size = (int(frame.get_width() * SWORD_SCALE), int(frame.get_height() * SWORD_SCALE))
            sword_frames.append(pygame.transform.scale(frame, new_size))
        except pygame.error:
            fallback = pygame.Surface((15, 8))
            fallback.fill((255, 255, 255))
            sword_frames.append(fallback)

    enemy_frames = []
    for i in range(1, 11):
        try:
            frame = pygame.image.load(f"sprites/ac{i}.png").convert_alpha()
            new_size = (int(frame.get_width() * 0.55), int(frame.get_height() * 0.55)) 
            enemy_frames.append(pygame.transform.scale(frame, new_size))
        except pygame.error:
            fallback = pygame.Surface((45, 45))
            fallback.fill((255, 0, 0))
            enemy_frames.append(fallback)

    enemy2_attack_frames = []
    for i in range(2, 8):
        try:
            frame = pygame.image.load(f"sprites/e{i}.png").convert_alpha()
            new_size = (int(frame.get_width() * 0.55), int(frame.get_height() * 0.55)) 
            enemy2_attack_frames.append(pygame.transform.scale(frame, new_size))
        except pygame.error:
            fallback = pygame.Surface((45, 45))
            fallback.fill((200, 50, 50))
            enemy2_attack_frames.append(fallback)

    # STATE INITIALIZATION / RESTORATION PIPELINE
    if checkpoint:
        player_x, player_y = checkpoint.get("p_x", 900), checkpoint.get("p_y", 500)
        kill_count = checkpoint.get("kills", 0)
        heart_value = checkpoint.get("hearts", START_HEARTS)
        player_coins = checkpoint.get("coins", 100)
    else:
        player_x, player_y = 900, 500
        kill_count = 0
        heart_value = START_HEARTS
        player_coins = 100  # Starting economy currency

    # Initialize animated player and companion same as level 1
    animated_player = AnimatedPlayer(player_x, player_y, scale=PLAYER_SCALE)
    animated_patroclus = AnimatedPatroclus(player_x - 20, player_y + 20, scale=1.0)

    enemy_x, enemy_y = 200, 500
    enemy_frame_idx = 0
    enemy_frame_counter = 0
    enemy_frame_delay = 2
    enemy_shoot_timer = 0
    enemy_shoot_cooldown = 75
    enemy_max_health = ARCHER_HEALTH  # Track max archer health
    enemy_health = ARCHER_HEALTH  # Track current archer health

    mole_hole_x = random.randint(200, WIDTH - 200)
    mole_hole_y = random.randint(MIN_Y + 30, MAX_Y - 30)
    enemy2_x, enemy2_y = mole_hole_x, mole_hole_y
    mole_y_offset = 50   
    mole_state = "emerging" 
    enemy2_frame_idx = 0
    enemy2_frame_counter = 0
    enemy2_frame_delay = 4
    enemy2_speed = 3.0  # Increased from 1.5 to 3.0 (twice as fast)

    is_swinging = False
    sword_frame_idx = 0
    sword_counter = 0
    has_hit_enemy = False
    sword_cooldown = 0  # Cooldown timer for sword attacks
    projectiles = []
    
    game_won = False
    game_lost = False
    flash_timer = 0
    victory_acknowledged = False  # Track if player has pressed space to acknowledge victory
    
    # Add victory screen timer to prevent instant skipping
    victory_screen_timer = 0.0
    victory_screen_delay = 0.1  # 0.1 second minimum before "Next Level" can be clicked

    sword_on_right = False
    global_esc_timer = 0

    # REMOVED PHANTOM TELEPORT ABILITY
    # phantom_active = False
    # phantom_timer = 0
    # phantom_cooldown = 0
    # phantom_cooldown_max = 5 * 60 
    enemy_target_lock_x = player_x
    enemy_target_lock_y = player_y

    audio_win_played = False
    audio_fail_played = False
    player_inventory = []
    
    # Shield bubble mechanic - now requires purchase
    shield_active = False
    shield_purchased = False
    shield_notification_timer = 0  # Timer for shield unlock notification
    
    # Blood spray effects
    blood_sprays = []

    # INITIALIZE DEALER: Top-right boundary position assignment
    level2_dealer = Dealer(MAX_X - 150, MIN_Y + 90, scale=0.5)

    running = True
    while running:
        clock.tick(60)
        current_time_ms = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        left_click_pressed = False
        e_pressed = False
        enter_pressed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_time_ms - global_esc_timer < 400:
                        return "menu", None
                    global_esc_timer = current_time_ms
                    
                    state_pkg = {"p_x": player_x, "p_y": player_y, "kills": kill_count, "hearts": heart_value, "coins": player_coins}
                    return "escaped", state_pkg
                
                # Single Press Trigger Catchers for UI Navigation
                elif event.key == pygame.K_e:
                    e_pressed = True
                elif event.key == pygame.K_RETURN:
                    enter_pressed = True
                # Space key to acknowledge victory and unpause game
                elif event.key == pygame.K_SPACE:
                    if game_won and not victory_acknowledged:
                        victory_acknowledged = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    left_click_pressed = True
                    # Block combat swings if interacting with Shop Menu OR if on cooldown OR if shield is active
                    if not is_swinging and not game_won and not game_lost and not level2_dealer.shop_open and sword_cooldown <= 0 and not shield_active:
                        is_swinging = True
                        if game_sounds_enabled and sword_sound: sword_sound.play()
                        sword_frame_idx = 0
                        sword_counter = 0
                        has_hit_enemy = False
                        sword_cooldown = SWORD_ATTACK_COOLDOWN  # Start cooldown
                
                # RIGHT CLICK FOR SHIELD (only if purchased)
                if event.button == 3: 
                    if not game_won and not game_lost and not level2_dealer.shop_open and shield_purchased:
                        shield_active = True

            # RIGHT CLICK RELEASE DEACTIVATES SHIELD
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3: 
                    shield_active = False

        keys = pygame.key.get_pressed()
        if not game_won and not game_lost and not level2_dealer.shop_open:
            if keys[pygame.K_d]:
                sword_on_right = True
            elif keys[pygame.K_a]:
                sword_on_right = False
        
        # Update shield notification timer
        if shield_notification_timer > 0:
            shield_notification_timer -= 1.0 / 60.0  # Decrease by time per frame
            # Allow SPACE to dismiss notification
            if keys[pygame.K_SPACE]:
                shield_notification_timer = 0

        # REMOVED PHANTOM TELEPORT PROCESSOR
        # if phantom_active and not game_won and not game_lost:
        #     phantom_timer += 1
        #     if phantom_timer <= 60:
        #         player_x, player_y = mouse_pos[0], mouse_pos[1]
        #         player_x = max(MIN_X, min(MAX_X, player_x))
        #         player_y = max(MIN_Y, min(MAX_Y, player_y))
        #     else:
        #         phantom_active = False
        #         phantom_cooldown = phantom_cooldown_max
        #         player_x, player_y = enemy_x - 70, enemy_y
        #         player_x = max(MIN_X, min(MAX_X, player_x))
        #         player_y = max(MIN_Y, min(MAX_Y, player_y))
        
        # if not phantom_active and phantom_cooldown > 0:
        #     phantom_cooldown -= 1
        
        # Update sword cooldown
        if sword_cooldown > 0:
            sword_cooldown -= 1.0 / 60.0  # Decrease by time per frame (assuming 60 FPS)

        # --- DEALER PROCESSING (Always active when game is paused or after acknowledging victory) ---
        if not game_lost and (victory_acknowledged or not game_won):
            shop_action = level2_dealer.update(player_x, player_y, e_pressed, keys, enter_pressed)
            if shop_action != -1:
                chosen_item = level2_dealer.items[shop_action]
                if player_coins >= chosen_item["cost"]:
                    # Play buy sound when successfully purchasing
                    if game_sounds_enabled and buy_sound:
                        buy_sound.play()
                    player_coins, purchased_item = level2_dealer.buy_item(shop_action, player_coins)
                    if purchased_item != "INSUFFICIENT_FUNDS":
                        player_inventory.append(purchased_item)
                        
                        # Handle special item purchases
                        if purchased_item == "Shield":
                            shield_purchased = True
                            shield_notification_timer = 5.0  # Show notification for 5 seconds
                        elif purchased_item == "Extra Heart":
                            heart_value = min(heart_value + 1, START_HEARTS + 1)  # Add 1 heart, max START_HEARTS + 1
                        
                        # If player just bought the ticket after winning, close shop to show victory screen
                        if game_won and purchased_item == "Colosseum Ticket":
                            level2_dealer.shop_open = False  # Close shop

        # --- PLAYER MOVEMENT AND ANIMATION UPDATE (Allow after victory acknowledgment but not during unacknowledged victory) ---
        if (not game_won or victory_acknowledged) and not game_lost:
            # Freeze entity processing loop mechanics while shopping menu context is live
            if not level2_dealer.shop_open:
                # REMOVED phantom_active check since phantom is removed
                player_moving = False
                if keys[pygame.K_w]: player_y -= PLAYER_SPEED; player_moving = True
                if keys[pygame.K_s]: player_y += PLAYER_SPEED; player_moving = True
                if keys[pygame.K_a]: player_x -= PLAYER_SPEED; player_moving = True
                if keys[pygame.K_d]: player_x += PLAYER_SPEED; player_moving = True

                player_x = max(MIN_X, min(MAX_X, player_x))
                player_y = max(MIN_Y, min(MAX_Y, player_y))
                
                # Update animated player movement
                animated_player.x = player_x
                animated_player.y = player_y
                animated_player.update_movement(keys)
                animated_player.update()
                
                # Update companion to follow player
                animated_patroclus.follow_player(player_x - 40, player_y + 40)
                healing_result = animated_patroclus.update()
                
                # Check if healing completed and heal the player
                if healing_result == "healing_complete":
                    old_hearts = heart_value
                    # Increase player heart value in level 2
                    heart_value = min(heart_value + 1, START_HEARTS)  # Increase hearts, max START_HEARTS
                    print(f"✓ LEVEL2 HEALED: Player hearts {old_hearts} → {heart_value}")

                # Calculate actual player center for targeting
                player_rect = animated_player.get_rect()
                player_center_x = player_rect.centerx
                player_center_y = player_rect.centery
                
                # REMOVED phantom target lock - archer now always targets actual player
                current_target_x = player_center_x
                current_target_y = player_center_y

                # --- ENEMY AI AND COMBAT (Only run when game is NOT won) ---
                if not game_won:
                    enemy_frame_counter += 1
                    if enemy_frame_counter >= enemy_frame_delay:
                        enemy_frame_counter = 0
                        enemy_frame_idx = (enemy_frame_idx + 1) % len(enemy_frames)

                    # ARCHER AI: Run away from player when player moves
                    dx = player_x - enemy_x
                    dy = player_y - enemy_y
                    dist = math.hypot(dx, dy)

                    if player_moving:
                        # Run AWAY from player - calculate new position first
                        if dist > 0:
                            new_enemy_x = enemy_x - (dx / dist) * 3  # Move away at speed 3
                            new_enemy_y = enemy_y - (dy / dist) * 3
                            
                            # Check if new position would be against a wall
                            margin = 50  # Keep away from edges
                            if new_enemy_x < MIN_X + margin or new_enemy_x > MAX_X - margin:
                                # Move perpendicular to avoid wall (circle around)
                                new_enemy_x = enemy_x + (dy / dist) * 3  # Move perpendicular
                            if new_enemy_y < MIN_Y + margin or new_enemy_y > MAX_Y - margin:
                                # Move perpendicular to avoid wall (circle around)
                                new_enemy_y = enemy_y - (dx / dist) * 3  # Move perpendicular
                            
                            enemy_x = new_enemy_x
                            enemy_y = new_enemy_y
                    else:
                        # When player is stationary, move closer only if far away
                        if dist > MIN_DISTANCE:
                            if dist > 0:
                                enemy_x += (dx / dist) * 2
                                enemy_y += (dy / dist) * 2
                                
                    # Clamp to valid area but allow movement along edges
                    enemy_x = max(MIN_X + 10, min(MAX_X - 10, enemy_x))
                    enemy_y = max(MIN_Y + 10, min(MAX_Y - 10, enemy_y))

                    enemy_shoot_timer += 1
                    if enemy_shoot_timer >= enemy_shoot_cooldown:
                        enemy_shoot_timer = 0
                        spawn_x = enemy_x + (60 * 0.55)
                        spawn_y = enemy_y + (20 * 0.55)
                        proj_dx = current_target_x - spawn_x
                        proj_dy = current_target_y - spawn_y
                        proj_dist = math.hypot(proj_dx, proj_dy)
                        if proj_dist == 0: proj_dist = 1
                        
                        if game_sounds_enabled and arrow_sound: arrow_sound.play()
                        projectiles.append({
                            "x": spawn_x,
                            "y": spawn_y,
                            "vx": (proj_dx / proj_dist) * ARROW_SPEED,
                            "vy": (proj_dy / proj_dist) * ARROW_SPEED,
                            "angle": -math.degrees(math.atan2(proj_dy, proj_dx))
                        })

                    if mole_state == "emerging":
                        mole_y_offset -= 2  
                        if mole_y_offset <= 0:
                            mole_y_offset = 0
                            mole_state = "active"
                    
                    elif mole_state == "active":
                        # Calculate actual player center for movement targeting and collision
                        player_rect = animated_player.get_rect()
                        player_center_x = player_rect.centerx
                        player_center_y = player_rect.centery
                        
                        m_dx = player_center_x - enemy2_x
                        m_dy = player_center_y - enemy2_y
                        m_dist = math.hypot(m_dx, m_dy)
                        if m_dist > 0:
                            enemy2_x += (m_dx / m_dist) * enemy2_speed
                            enemy2_y += (m_dy / m_dist) * enemy2_speed
                        
                        if math.hypot(player_center_x - enemy2_x, player_center_y - enemy2_y) <= PLAYER_BODY_RADIUS:
                            heart_value -= 1
                            flash_timer = 5
                            if heart_value <= 0: game_lost = True
                            
                            # Spawn near player (within 150-300 pixels)
                            spawn_distance = random.randint(150, 300)
                            spawn_angle = random.uniform(0, 2 * math.pi)
                            mole_hole_x = player_x + math.cos(spawn_angle) * spawn_distance
                            mole_hole_y = player_y + math.sin(spawn_angle) * spawn_distance
                            # Clamp to valid area
                            mole_hole_x = max(MIN_X + 100, min(MAX_X - 100, mole_hole_x))
                            mole_hole_y = max(MIN_Y + 30, min(MAX_Y - 30, mole_hole_y))
                            enemy2_x, enemy2_y = mole_hole_x, mole_hole_y
                            mole_y_offset = 50
                            mole_state = "emerging"

                    enemy2_frame_counter += 1
                    if enemy2_frame_counter >= enemy2_frame_delay:
                        enemy2_frame_counter = 0
                        enemy2_frame_idx = (enemy2_frame_idx + 1) % len(enemy2_attack_frames)

                    if is_swinging:
                        sword_counter += 1
                        if sword_counter >= 4:  
                            sword_counter = 0
                            sword_frame_idx += 1
                            if sword_frame_idx >= len(sword_frames):
                                is_swinging = False
                                sword_frame_idx = 0

                    if is_swinging and not has_hit_enemy:
                        player_rect = animated_player.get_rect()
                        player_center_x = player_rect.centerx
                        player_center_y = player_rect.centery
                        
                        if math.hypot(player_center_x - enemy_x, player_center_y - enemy_y) <= SWORD_ATTACK_RANGE:
                            enemy_health -= 1  # Reduce archer health
                            has_hit_enemy = True
                            # Create blood spray effect
                            blood_sprays.append(BloodSpray(enemy_x, enemy_y))
                            if enemy_health <= 0:
                                kill_count += 1
                                player_coins += 25  # Reward bounty currency upon targets eliminated
                                enemy_x, enemy_y = 200, 500
                                enemy_health = ARCHER_HEALTH  # Reset health for next archer
                        
                        elif mole_state == "active" and math.hypot(player_center_x - enemy2_x, player_center_y - enemy2_y) <= SWORD_ATTACK_RANGE:
                            has_hit_enemy = True
                            player_coins += 15
                            # Create blood spray effect
                            blood_sprays.append(BloodSpray(enemy2_x, enemy2_y))
                            # Spawn near player (within 150-300 pixels)
                            spawn_distance = random.randint(150, 300)
                            spawn_angle = random.uniform(0, 2 * math.pi)
                            mole_hole_x = player_x + math.cos(spawn_angle) * spawn_distance
                            mole_hole_y = player_y + math.sin(spawn_angle) * spawn_distance
                            # Clamp to valid area
                            mole_hole_x = max(MIN_X + 100, min(MAX_X - 100, mole_hole_x))
                            mole_hole_y = max(MIN_Y + 30, min(MAX_Y - 30, mole_hole_y))
                            enemy2_x, enemy2_y = mole_hole_x, mole_hole_y
                            mole_y_offset = 50
                            mole_state = "emerging"

                        if kill_count >= WIN_TARGET: 
                            game_won = True

                    projectiles_to_keep = []
                    for projectile in projectiles:
                        projectile["x"] += projectile["vx"]
                        projectile["y"] += projectile["vy"]
                        
                        player_rect = animated_player.get_rect()
                        player_center_x = player_rect.centerx
                        player_center_y = player_rect.centery
                        
                        blocked_by_sword = False
                        if is_swinging and math.hypot(player_center_x - projectile["x"], player_center_y - projectile["y"]) <= SWORD_ATTACK_RANGE:
                            blocked_by_sword = True
                        
                        # Check if blocked by shield
                        blocked_by_shield = False
                        if shield_active and math.hypot(player_center_x - projectile["x"], player_center_y - projectile["y"]) <= 60:
                            blocked_by_shield = True
                        
                        if blocked_by_sword or blocked_by_shield: 
                            continue  
                        
                        if math.hypot(player_center_x - projectile["x"], player_center_y - projectile["y"]) <= PLAYER_BODY_RADIUS:
                            heart_value -= 1
                            flash_timer = 5 
                            if heart_value <= 0: game_lost = True
                            continue 
                            
                        if (-50 < projectile["x"] < WIDTH + 50 and -50 < projectile["y"] < HEIGHT + 50):
                            projectiles_to_keep.append(projectile)
                            
                    projectiles = projectiles_to_keep

        # --- RENDERING ENGINE ---
        screen.blit(background, (0, 0))

        pygame.draw.ellipse(screen, (15, 15, 20), (mole_hole_x - 40, mole_hole_y + 10, 80, 20))
        pygame.draw.ellipse(screen, (50, 40, 35), (mole_hole_x - 40, mole_hole_y + 10, 80, 20), 2)

        e2_surf = enemy2_attack_frames[enemy2_frame_idx]
        
        # Calculate player center for consistent sprite flipping
        player_rect = animated_player.get_rect()
        player_center_x = player_rect.centerx
        
        if player_center_x < enemy2_x:
            e2_surf = pygame.transform.flip(e2_surf, True, False) 
            
        if mole_state == "emerging":
            e2_rect = e2_surf.get_rect(center=(enemy2_x, enemy2_y + mole_y_offset))
            clip_rect = pygame.Rect(0, 0, e2_rect.width, max(0, (mole_hole_y + 20) - e2_rect.top))
            screen.blit(e2_surf, e2_rect, area=clip_rect)
        else:
            e2_rect = e2_surf.get_rect(center=(int(enemy2_x), int(enemy2_y)))
            screen.blit(e2_surf, e2_rect)

        # Render Dealer Environment Elements
        level2_dealer.draw(screen, player_x, player_y, player_coins)

        # Only draw game entities when shop is closed
        if not level2_dealer.shop_open:
            # Draw animated player and companion
            animated_player.draw(screen)
            animated_patroclus.draw(screen)
            
            if is_swinging:
                raw_sword = sword_frames[sword_frame_idx]
                current_sword_img = pygame.transform.flip(raw_sword, True, False) if sword_on_right else raw_sword
                offset_x = 10 * PLAYER_SCALE if sword_on_right else -10 * PLAYER_SCALE
                
                # Calculate player center position
                player_rect = animated_player.get_rect()
                player_center_x = player_rect.centerx
                player_center_y = player_rect.centery
                
                sword_draw_rect = current_sword_img.get_rect(center=(int(player_center_x + offset_x), int(player_center_y)))
                screen.blit(current_sword_img, sword_draw_rect)
            else:
                raw_idle = sword_frames[0]
                idle_sword_img = pygame.transform.flip(raw_idle, True, False) if sword_on_right else raw_idle
                offset_x = 20 * PLAYER_SCALE if sword_on_right else -20 * PLAYER_SCALE
                
                # Calculate player center position
                player_rect = animated_player.get_rect()
                player_center_x = player_rect.centerx
                player_center_y = player_rect.centery
                
                sword_draw_rect = idle_sword_img.get_rect(center=(int(player_center_x + offset_x), int(player_center_y - 1 * PLAYER_SCALE)))
                screen.blit(idle_sword_img, sword_draw_rect)

            enemy_rect = enemy_frames[enemy_frame_idx].get_rect(center=(int(enemy_x), int(enemy_y)))
            screen.blit(enemy_frames[enemy_frame_idx], enemy_rect)
            
            # Draw archer health bar if damaged
            if enemy_health < enemy_max_health:
                draw_health_bar(screen, int(enemy_x), int(enemy_y) - 40, enemy_health, enemy_max_health, width=60, height=7)

            for projectile in projectiles:
                rotated_arrow = pygame.transform.rotate(projectile_base_img, projectile["angle"])
                screen.blit(rotated_arrow, rotated_arrow.get_rect(center=(int(projectile["x"]), int(projectile["y"]))))

            # Draw blood spray effects
            dt = clock.get_time() / 1000.0
            for spray in blood_sprays[:]:
                if not spray.update(dt):
                    blood_sprays.remove(spray)
                spray.draw(screen)

            bard.update()
            bard.draw(screen)
            
            # Draw shield bubble if active
            if shield_active:
                player_rect = animated_player.get_rect()
                player_center_x = player_rect.centerx
                player_center_y = player_rect.centery
                
                shield_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(shield_surf, (100, 150, 255, 80), (60, 60), 60)  # Light transparent blue
                pygame.draw.circle(shield_surf, (150, 200, 255, 120), (60, 60), 60, 3)  # Brighter blue border
                screen.blit(shield_surf, (player_center_x - 60, player_center_y - 60))

        if flash_timer > 0:
            flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((255, 0, 0, 75)) 
            screen.blit(flash_surf, (0, 0))
            flash_timer -= 1
        
        # Shield unlock notification
        if shield_notification_timer > 0:
            notif_bg = pygame.Surface((500, 120), pygame.SRCALPHA)
            pygame.draw.rect(notif_bg, (0, 0, 0, 200), (0, 0, 500, 120), border_radius=10)
            pygame.draw.rect(notif_bg, (100, 150, 255), (0, 0, 500, 120), 3, border_radius=10)
            screen.blit(notif_bg, (WIDTH // 2 - 250, 200))
            
            notif_title = FONT_SCORE.render("SHIELD UNLOCKED!", True, (100, 255, 100))
            screen.blit(notif_title, (WIDTH // 2 - notif_title.get_width() // 2, 220))
            
            notif_text = pygame.font.SysFont("Arial", 24, bold=True).render("Press RIGHT CLICK to activate shield", True, (255, 255, 255))
            screen.blit(notif_text, (WIDTH // 2 - notif_text.get_width() // 2, 260))
            
            dismiss_text = pygame.font.SysFont("Arial", 20).render("Press SPACE to dismiss", True, (200, 200, 200))
            screen.blit(dismiss_text, (WIDTH // 2 - dismiss_text.get_width() // 2, 290))

        score_surface = FONT_SCORE.render(f"Kills: {kill_count} / {WIN_TARGET}", True, (255, 255, 255))
        screen.blit(score_surface, (20, 20))
        
        # Add timer and player name display
        if timer and timer.is_running and player_name:
            timer_surface = FONT_SCORE.render(f"Time: {timer.format_time()}", True, (255, 255, 255))
            screen.blit(timer_surface, (20, 55))
            
            player_surface = FONT_SCORE.render(f"Player: {player_name}", True, (255, 255, 255))
            screen.blit(player_surface, (20, 90))
        
        # Display Coin HUD Counter Balance
        coins_surface = FONT_SCORE.render(f"Coins: {player_coins}", True, (255, 215, 0))
        screen.blit(coins_surface, (220, 20))
        
        for h in range(max(0, heart_value)):
            heart_y = 155 if (timer and timer.is_running and player_name) else 105
            draw_heart(screen, x=35 + (h * 35), y=heart_y, size=24)

        if game_won:
            victory_screen_timer += clock.get_time() / 1000.0  # Add elapsed time in seconds
            
            if not audio_win_played:
                if game_sounds_enabled and win_sound: win_sound.play()
                audio_win_played = True
            
            # Check if player has bought the Colosseum Ticket
            has_ticket = "Colosseum Ticket" in player_inventory
            
            # Only show overlay and victory text if not acknowledged OR if acknowledged but no ticket yet
            if not victory_acknowledged or (victory_acknowledged and not has_ticket):
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))
                
                win_surface = FONT_WIN.render("YOU WIN!", True, (0, 255, 100))
                screen.blit(win_surface, win_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
            
            # Show different UI based on whether victory is acknowledged
            if not victory_acknowledged:
                # Initial victory screen - show press space message
                if not has_ticket:
                    message1 = FONT_SCORE.render("You need a Colosseum Ticket to proceed!", True, (255, 200, 50))
                    screen.blit(message1, message1.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
                else:
                    message1 = FONT_SCORE.render("You have the Colosseum Ticket!", True, (100, 255, 100))
                    screen.blit(message1, message1.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
                
                # Press space instruction
                space_msg = FONT_SCORE.render("Press SPACE to continue", True, (255, 255, 255))
                screen.blit(space_msg, space_msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70)))
                
            elif victory_acknowledged:
                # After pressing space - show appropriate message/button
                if has_ticket:
                    # Show "Next Level" button with overlay
                    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 150))
                    screen.blit(overlay, (0, 0))
                    
                    win_surface = FONT_WIN.render("YOU WIN!", True, (0, 255, 100))
                    screen.blit(win_surface, win_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
                    
                    next_btn_rect = pygame.Rect((WIDTH // 2 - 120, HEIGHT // 2 + 50), (240, 65))
                    
                    # Only allow clicking after the delay period
                    if victory_screen_timer >= victory_screen_delay:
                        if next_btn_rect.collidepoint(mouse_pos):
                            pygame.draw.rect(screen, (80, 80, 80), next_btn_rect, border_radius=10)
                            if left_click_pressed:
                                if game_sounds_enabled and click_sound: click_sound.play()
                                return "completed", None
                        else:
                            pygame.draw.rect(screen, (45, 45, 45), next_btn_rect, border_radius=10)
                    else:
                        # Button disabled during delay - no visual indication
                        pygame.draw.rect(screen, (45, 45, 45), next_btn_rect, border_radius=10)

                    # Show "Next Level" text
                    btn_text = FONT_BUTTON.render("Next Level", True, (255, 255, 255))
                    pygame.draw.rect(screen, (200, 200, 200), next_btn_rect, 3, border_radius=10)
                    screen.blit(btn_text, btn_text.get_rect(center=next_btn_rect.center))
                else:
                    # No ticket - display message to buy ticket from dealer (with overlay)
                    message1 = FONT_SCORE.render("Visit the Dealer to buy a ticket!", True, (255, 200, 50))
                    message2 = FONT_SCORE.render("Colosseum Ticket costs 15 coins", True, (255, 200, 50))
                    screen.blit(message1, message1.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
                    screen.blit(message2, message2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))

        if game_lost:
            if not audio_fail_played:
                if game_sounds_enabled and fail_sound: fail_sound.play()
                audio_fail_played = True
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((20, 20, 20, 200))
            screen.blit(overlay, (0, 0))
            lost_surface = FONT_WIN.render("You lost", True, (255, 50, 50))
            screen.blit(lost_surface, lost_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))

            btn_rect = pygame.Rect((WIDTH // 2 - 120, HEIGHT // 2 + 50), (240, 65))
            if btn_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (80, 80, 80), btn_rect, border_radius=10) 
                if left_click_pressed:
                    if game_sounds_enabled and click_sound: click_sound.play()
                    player_x, player_y = 900, 500  
                    enemy_x, enemy_y = 200, 500
                    enemy_health = ARCHER_HEALTH  # Reset archer health
                    kill_count = 0
                    heart_value = START_HEARTS
                    player_coins = 100
                    projectiles.clear()
                    audio_fail_played = False
                    game_lost = False
                    
                    mole_hole_x = random.randint(200, WIDTH - 200)
                    mole_hole_y = random.randint(MIN_Y + 30, MAX_Y - 30)
                    enemy2_x, enemy2_y = mole_hole_x, mole_hole_y
                    mole_y_offset = 50
                    mole_state = "emerging"
            else:
                pygame.draw.rect(screen, (45, 45, 45), btn_rect, border_radius=10) 
                
            pygame.draw.rect(screen, (200, 200, 200), btn_rect, 3, border_radius=10) 
            btn_text = FONT_BUTTON.render("Try Again", True, (255, 255, 255))
            screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))

        pygame.display.flip()