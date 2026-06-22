import math
import sys
import os
import pygame
import random
from level3 import start_level_3

WIDTH, HEIGHT = 1280, 720
MIN_X, MAX_X = 0, WIDTH
MIN_Y, MAX_Y = 530, HEIGHT - 43

def draw_heart(surface, x, y, size=24):
    color = (255, 40, 60)
    pygame.draw.circle(surface, color, (x - size // 4, y - size // 4), size // 4)
    pygame.draw.circle(surface, color, (x + size // 4, y - size // 4), size // 4)
    points = [(x - size // 2, y - size // 6), (x + size // 2, y - size // 6), (x, y + size // 2)]
    pygame.draw.polygon(surface, color, points)

def start_level_2(bard, sfx_enabled=True, checkpoint=None):
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Level 2: The Archer Showdown")
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
    WIN_TARGET = 2 
    START_HEARTS = 5

    arrow_sound = pygame.mixer.Sound("arrow.mp3") if os.path.exists("arrow.mp3") else None
    sword_sound = pygame.mixer.Sound("sword.mp3") if os.path.exists("sword.mp3") else None
    win_sound   = pygame.mixer.Sound("win.mp3") if os.path.exists("win.mp3") else None
    fail_sound  = pygame.mixer.Sound("fail.mp3") if os.path.exists("fail.mp3") else None
    click_sound = pygame.mixer.Sound("mouse.mp3") if os.path.exists("mouse.mp3") else None

    try:
        background = pygame.image.load("sea.jpg").convert()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    except pygame.error:
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill((0, 105, 148))

    try:
        projectile_base_img = pygame.image.load("arrow.png").convert_alpha()
        arrow_w = int(projectile_base_img.get_width() * ARROW_SCALE)
        arrow_h = int(projectile_base_img.get_height() * ARROW_SCALE)
        projectile_base_img = pygame.transform.scale(projectile_base_img, (arrow_w, arrow_h))
    except pygame.error:
        projectile_base_img = pygame.Surface((15, 5))
        projectile_base_img.fill((200, 200, 200))

    try:
        player_raw_img = pygame.image.load("player.png").convert_alpha()
        player_w = int(player_raw_img.get_width() * PLAYER_SCALE)
        player_h = int(player_raw_img.get_height() * PLAYER_SCALE)
        player_img = pygame.transform.scale(player_raw_img, (player_w, player_h))
    except pygame.error:
        player_img = pygame.Surface((30, 30))
        player_img.fill((0, 255, 0))

    sword_frames = []
    for i in range(1, 4):
        try:
            frame = pygame.image.load(f"sword{i}.png").convert_alpha()
            new_size = (int(frame.get_width() * SWORD_SCALE), int(frame.get_height() * SWORD_SCALE))
            sword_frames.append(pygame.transform.scale(frame, new_size))
        except pygame.error:
            fallback = pygame.Surface((15, 8))
            fallback.fill((255, 255, 255))
            sword_frames.append(fallback)

    enemy_frames = []
    for i in range(1, 11):
        try:
            frame = pygame.image.load(f"ac{i}.png").convert_alpha()
            new_size = (int(frame.get_width() * 0.55), int(frame.get_height() * 0.55)) 
            enemy_frames.append(pygame.transform.scale(frame, new_size))
        except pygame.error:
            fallback = pygame.Surface((45, 45))
            fallback.fill((255, 0, 0))
            enemy_frames.append(fallback)

    enemy2_attack_frames = []
    for i in range(2, 8):
        try:
            frame = pygame.image.load(f"e{i}.png").convert_alpha()
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
    else:
        player_x, player_y = 900, 500
        kill_count = 0
        heart_value = START_HEARTS

    enemy_x, enemy_y = 200, 500
    enemy_frame_idx = 0
    enemy_frame_counter = 0
    enemy_frame_delay = 2
    enemy_shoot_timer = 0
    
    # SLOWED DOWN: Shooting rate relaxed from 30 frames to 75 frames spacing
    enemy_shoot_cooldown = 75

    mole_hole_x = random.randint(200, WIDTH - 200)
    mole_hole_y = random.randint(MIN_Y + 30, MAX_Y - 30)
    enemy2_x, enemy2_y = mole_hole_x, mole_hole_y
    mole_y_offset = 50   
    mole_state = "emerging" 
    enemy2_frame_idx = 0
    enemy2_frame_counter = 0
    enemy2_frame_delay = 4
    enemy2_speed = 1.5

    is_swinging = False
    sword_frame_idx = 0
    sword_counter = 0
    has_hit_enemy = False
    projectiles = []
    
    game_won = False
    game_lost = False
    flash_timer = 0

    sword_on_right = False
    global_esc_timer = 0

    phantom_active = False
    phantom_timer = 0
    phantom_cooldown = 0
    phantom_cooldown_max = 5 * 60 
    enemy_target_lock_x = player_x
    enemy_target_lock_y = player_y

    audio_win_played = False
    audio_fail_played = False

    running = True
    while running:
        clock.tick(60)
        current_time_ms = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        left_click_pressed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Double escape instantly resets game straight back to Scrolling intro scene
                    if current_time_ms - global_esc_timer < 400:
                        # Return all the way to start
                        return "menu", None
                    global_esc_timer = current_time_ms
                    
                    # Single Escape Action: Save context and drop back to layout choice screen
                    state_pkg = {"p_x": player_x, "p_y": player_y, "kills": kill_count, "hearts": heart_value}
                    return "escaped", state_pkg

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left Click Attack Input
                    left_click_pressed = True
                    if not is_swinging and not game_won and not game_lost:
                        is_swinging = True
                        if sfx_enabled and sword_sound: sword_sound.play()
                        sword_frame_idx = 0
                        sword_counter = 0
                        has_hit_enemy = False
                
                if event.button == 3: # Right Click Skill Active Lock
                    if phantom_cooldown == 0 and not phantom_active:
                        phantom_active = True
                        phantom_timer = 0
                        enemy_target_lock_x = player_x
                        enemy_target_lock_y = player_y

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3: 
                    if phantom_active:
                        phantom_active = False
                        phantom_cooldown = phantom_cooldown_max
                        player_x, player_y = enemy_x - 70, enemy_y
                        player_x = max(MIN_X, min(MAX_X, player_x))
                        player_y = max(MIN_Y, min(MAX_Y, player_y))

        # Horizontal direction tracking linked seamlessly to explicit buttons
        keys = pygame.key.get_pressed()
        if not game_won and not game_lost and not phantom_active:
            if keys[pygame.K_d]:
                sword_on_right = True
            elif keys[pygame.K_a]:
                sword_on_right = False

        # --- UNTARGETABLE PHANTOM PROCESSOR ---
        if phantom_active and not game_won and not game_lost:
            phantom_timer += 1
            if phantom_timer <= 60:
                player_x, player_y = mouse_pos[0], mouse_pos[1]
                player_x = max(MIN_X, min(MAX_X, player_x))
                player_y = max(MIN_Y, min(MAX_Y, player_y))
            else:
                phantom_active = False
                phantom_cooldown = phantom_cooldown_max
                player_x, player_y = enemy_x - 70, enemy_y
                player_x = max(MIN_X, min(MAX_X, player_x))
                player_y = max(MIN_Y, min(MAX_Y, player_y))
        
        if not phantom_active and phantom_cooldown > 0:
            phantom_cooldown -= 1

        # --- GAME STATE UPDATE ---
        if not game_won and not game_lost:
            if not phantom_active:
                player_moving = False
                if keys[pygame.K_w]: player_y -= PLAYER_SPEED; player_moving = True
                if keys[pygame.K_s]: player_y += PLAYER_SPEED; player_moving = True
                if keys[pygame.K_a]: player_x -= PLAYER_SPEED; player_moving = True
                if keys[pygame.K_d]: player_x += PLAYER_SPEED; player_moving = True

                player_x = max(MIN_X, min(MAX_X, player_x))
                player_y = max(MIN_Y, min(MAX_Y, player_y))
            else:
                player_moving = False

            current_target_x = enemy_target_lock_x if phantom_active else player_x
            current_target_y = enemy_target_lock_y if phantom_active else player_y

            enemy_frame_counter += 1
            if enemy_frame_counter >= enemy_frame_delay:
                enemy_frame_counter = 0
                enemy_frame_idx = (enemy_frame_idx + 1) % len(enemy_frames)

            dx = player_x - enemy_x
            dy = player_y - enemy_y
            dist = math.hypot(dx, dy)

            if player_moving and dist > MIN_DISTANCE:
                if dist == 0: dist = 1
                enemy_x += (dx / dist) * 2
                enemy_y += (dy / dist) * 2
            enemy_x = max(MIN_X, min(MAX_X, enemy_x))
            enemy_y = max(MIN_Y, min(MAX_Y, enemy_y))

            enemy_shoot_timer += 1
            if enemy_shoot_timer >= enemy_shoot_cooldown:
                enemy_shoot_timer = 0
                spawn_x = enemy_x + (60 * 0.55)
                spawn_y = enemy_y + (20 * 0.55)
                proj_dx = current_target_x - spawn_x
                proj_dy = current_target_y - spawn_y
                proj_dist = math.hypot(proj_dx, proj_dy)
                if proj_dist == 0: proj_dist = 1
                
                if sfx_enabled and arrow_sound: arrow_sound.play()
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
                m_dx = player_x - enemy2_x
                m_dy = player_y - enemy2_y
                m_dist = math.hypot(m_dx, m_dy)
                if m_dist > 0:
                    enemy2_x += (m_dx / m_dist) * enemy2_speed
                    enemy2_y += (m_dy / m_dist) * enemy2_speed
                
                if math.hypot(player_x - enemy2_x, player_y - enemy2_y) <= PLAYER_BODY_RADIUS:
                    heart_value -= 1
                    flash_timer = 5
                    if heart_value <= 0: game_lost = True
                    
                    mole_hole_x = random.randint(200, WIDTH - 200)
                    mole_hole_y = random.randint(MIN_Y + 30, MAX_Y - 30)
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
                if math.hypot(player_x - enemy_x, player_y - enemy_y) <= SWORD_ATTACK_RANGE:
                    kill_count += 1
                    has_hit_enemy = True 
                    enemy_x, enemy_y = 200, 500
                
                elif mole_state == "active" and math.hypot(player_x - enemy2_x, player_y - enemy2_y) <= SWORD_ATTACK_RANGE:
                    has_hit_enemy = True
                    mole_hole_x = random.randint(200, WIDTH - 200)
                    mole_hole_y = random.randint(MIN_Y + 30, MAX_Y - 30)
                    enemy2_x, enemy2_y = mole_hole_x, mole_hole_y
                    mole_y_offset = 50
                    mole_state = "emerging"

                if kill_count >= WIN_TARGET: 
                    game_won = True

            projectiles_to_keep = []
            for projectile in projectiles:
                projectile["x"] += projectile["vx"]
                projectile["y"] += projectile["vy"]
                
                blocked_by_sword = False
                if is_swinging and math.hypot(player_x - projectile["x"], player_y - projectile["y"]) <= SWORD_ATTACK_RANGE:
                    blocked_by_sword = True
                
                if blocked_by_sword: 
                    continue  
                
                if math.hypot(player_x - projectile["x"], player_y - projectile["y"]) <= PLAYER_BODY_RADIUS:
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
        if player_x < enemy2_x:
            e2_surf = pygame.transform.flip(e2_surf, True, False) 
            
        if mole_state == "emerging":
            e2_rect = e2_surf.get_rect(center=(enemy2_x, enemy2_y + mole_y_offset))
            clip_rect = pygame.Rect(0, 0, e2_rect.width, max(0, (mole_hole_y + 20) - e2_rect.top))
            screen.blit(e2_surf, e2_rect, area=clip_rect)
        else:
            e2_rect = e2_surf.get_rect(center=(int(enemy2_x), int(enemy2_y)))
            screen.blit(e2_surf, e2_rect)

        # Draw Player with horizontal flip state tracked by standard configuration flags
        p_surf = player_img if sword_on_right else pygame.transform.flip(player_img, True, False)
        ent_draw_rect = p_surf.get_rect(center=(int(player_x), int(player_y)))
        
        if phantom_active: p_surf.set_alpha(100)
        else: p_surf.set_alpha(255)
        screen.blit(p_surf, ent_draw_rect)
        
        if is_swinging:
            raw_sword = sword_frames[sword_frame_idx]
            current_sword_img = pygame.transform.flip(raw_sword, True, False) if sword_on_right else raw_sword
            offset_x = 30 * PLAYER_SCALE if sword_on_right else -30 * PLAYER_SCALE
            sword_draw_rect = current_sword_img.get_rect(center=(int(player_x + offset_x), int(player_y)))
            screen.blit(current_sword_img, sword_draw_rect)
        else:
            raw_idle = sword_frames[0]
            idle_sword_img = pygame.transform.flip(raw_idle, True, False) if sword_on_right else raw_idle
            offset_x = 15 * PLAYER_SCALE if sword_on_right else -15 * PLAYER_SCALE
            sword_draw_rect = idle_sword_img.get_rect(center=(int(player_x + offset_x), int(player_y - 5 * PLAYER_SCALE)))
            screen.blit(idle_sword_img, sword_draw_rect)

        enemy_rect = enemy_frames[enemy_frame_idx].get_rect(center=(int(enemy_x), int(enemy_y)))
        screen.blit(enemy_frames[enemy_frame_idx], enemy_rect)

        for projectile in projectiles:
            rotated_arrow = pygame.transform.rotate(projectile_base_img, projectile["angle"])
            screen.blit(rotated_arrow, rotated_arrow.get_rect(center=(int(projectile["x"]), int(projectile["y"]))))

        bard.update()
        bard.draw(screen)

        if flash_timer > 0:
            flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((255, 0, 0, 75)) 
            screen.blit(flash_surf, (0, 0))
            flash_timer -= 1

        score_surface = FONT_SCORE.render(f"Kills: {kill_count} / {WIN_TARGET}", True, (255, 255, 255))
        screen.blit(score_surface, (20, 20))
        
        if phantom_active:
            skill_text = f"PHANTOM ACTIVE: {max(0.0, (60 - phantom_timer) / 60.0):.1f}s"
            skill_color = (0, 255, 255)
        elif phantom_cooldown > 0:
            skill_text = f"PHANTOM COOLDOWN: {max(0.0, phantom_cooldown / 60.0):.1f}s"
            skill_color = (255, 50, 50)
        else:
            skill_text = "PHANTOM CHASE [R-CLICK]: READY"
            skill_color = (255, 255, 255)
            
        skill_surf = FONT_SCORE.render(skill_text, True, skill_color)
        screen.blit(skill_surf, (20, HEIGHT - 50))
        
        for h in range(max(0, heart_value)):
            draw_heart(screen, x=35 + (h * 35), y=75, size=24)

        if game_won:
            if not audio_win_played:
                if sfx_enabled and win_sound: win_sound.play()
                audio_win_played = True
            
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            win_surface = FONT_WIN.render("YOU WIN!", True, (0, 255, 100))
            screen.blit(win_surface, win_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))

            next_btn_rect = pygame.Rect((WIDTH // 2 - 120, HEIGHT // 2 + 50), (240, 65))
            if next_btn_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (80, 80, 80), next_btn_rect, border_radius=10)
                if left_click_pressed:
                    if sfx_enabled and click_sound: click_sound.play()
                    start_level_3(bard)
                    return "completed", None
            else:
                pygame.draw.rect(screen, (45, 45, 45), next_btn_rect, border_radius=10)

            pygame.draw.rect(screen, (200, 200, 200), next_btn_rect, 3, border_radius=10)
            btn_text = FONT_BUTTON.render("Next Level", True, (255, 255, 255))
            screen.blit(btn_text, btn_text.get_rect(center=next_btn_rect.center))

        if game_lost:
            if not audio_fail_played:
                if sfx_enabled and fail_sound: fail_sound.play()
                audio_fail_played = True
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((20, 20, 20, 200))
            screen.blit(overlay, (0, 0))
            lost_surface = FONT_WIN.render("Lost try again", True, (255, 50, 50))
            screen.blit(lost_surface, lost_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))

            btn_rect = pygame.Rect((WIDTH // 2 - 120, HEIGHT // 2 + 50), (240, 65))
            if btn_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (80, 80, 80), btn_rect, border_radius=10) 
                if left_click_pressed:
                    if sfx_enabled and click_sound: click_sound.play()
                    player_x, player_y = 900, 500  
                    enemy_x, enemy_y = 200, 500
                    kill_count = 0
                    heart_value = START_HEARTS
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