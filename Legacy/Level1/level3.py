import pygame
import sys
from os.path import join
import math
import random

def start_level_3(bard):
    pygame.init()
    pygame.font.init()

    WINDOW_WIDTH   = 1280
    WINDOW_HEIGHT  = 720
    PLAYER_SPEED   = 400     
    ENEMY_SPEED    = 150     
    ENEMY_SCALE    = 1.25  

    AXE_BASE_WIDTH        = 50    
    AXE_BASE_HEIGHT       = 50    
    AXE_GROWTH_SPEED      = 12.0  
    
    TIME_THRESHOLD_1      = 0.5   
    SCALE_TARGET_1        = 9.0   
    TIME_THRESHOLD_2      = 0.75  
    SCALE_TARGET_2        = 13.0  
    TIME_THRESHOLD_3      = 1.0   
    SCALE_TARGET_3        = 16.0  

    DAMAGE_TIER_1         = 10
    DAMAGE_TIER_2         = 15
    DAMAGE_TIER_3         = 30

    # VARIABLE ADDED: Scale factor for Hector's blue wave projectile
    WAVE_SCALE            = 2.0  

    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pixel Game - Level 3: Dual Hand Slashes")
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    enemy_sprites = pygame.sprite.Group()
    skeleton_sprites = pygame.sprite.Group()
    projectile_sprites = pygame.sprite.Group()  
    vfx_sprites = pygame.sprite.Group()

    try:
        UI_FONT = pygame.font.Font(join("text", "Oxanium-Bold.ttf"), 24)
        DAMAGE_FONT = pygame.font.Font(join("text", "Oxanium-Bold.ttf"), 28)
        WIN_FONT = pygame.font.Font(join("text", "Oxanium-Bold.ttf"), 64)
    except OSError:
        UI_FONT = pygame.font.SysFont("Arial", 24, bold=True)
        DAMAGE_FONT = pygame.font.SysFont("Arial", 28, bold=True)
        WIN_FONT = pygame.font.SysFont("Arial", 64, bold=True)

    try:
        axe_orig_img = pygame.image.load("axes.png").convert_alpha()
        axe_orig_img = pygame.transform.scale(axe_orig_img, (AXE_BASE_WIDTH, AXE_BASE_HEIGHT))
    except FileNotFoundError:
        axe_orig_img = pygame.Surface((AXE_BASE_WIDTH, AXE_BASE_HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(axe_orig_img, (192, 192, 192), [
            (AXE_BASE_WIDTH//2, 0), (AXE_BASE_WIDTH, AXE_BASE_HEIGHT//2), 
            (AXE_BASE_WIDTH//2, AXE_BASE_HEIGHT), (0, AXE_BASE_HEIGHT//2)
        ])

    try:
        background = pygame.image.load(join("images", "lv3background.png")).convert()
    except FileNotFoundError:
        background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        background.fill((30, 20, 30))
    background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))

    ske_imgs = []
    for name in ["ske1.png", "ske2.png"]:
        try:
            ske_imgs.append(pygame.image.load(name).convert_alpha())
        except FileNotFoundError:
            surf = pygame.Surface((40, 60), pygame.SRCALPHA)
            surf.fill((200, 200, 200) if "1" in name else (170, 170, 170))
            ske_imgs.append(surf)

    # --- PROJECTILE CLASSES ---
    class PinkHeart(pygame.sprite.Sprite):
        def __init__(self, pos, target_pos, groups):
            super().__init__(groups)
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 105, 180), (6, 6), 6)
            pygame.draw.circle(self.image, (255, 105, 180), (14, 6), 6)
            pygame.draw.polygon(self.image, (255, 105, 180), [(0, 9), (20, 9), (10, 20)])
            
            self.rect = self.image.get_rect(center=pos)
            direction = pygame.Vector2(target_pos) - pygame.Vector2(pos)
            if direction.length() > 0:
                self.direction = direction.normalize()
            else:
                self.direction = pygame.Vector2(-1, 0)
            self.speed = 250

        def update(self, dt):
            self.rect.center += self.direction * self.speed * dt
            if not display_surface.get_rect().collidepoint(self.rect.center):
                self.kill()

    class BlueWave(pygame.sprite.Sprite):
        def __init__(self, pos, target_pos, groups):
            super().__init__(groups)
            font = pygame.font.SysFont("Arial", 32, bold=True)
            raw_wave = font.render(")))", True, (0, 191, 255))
            
            # Scaled up wave image cleanly using WAVE_SCALE
            w = int(raw_wave.get_width() * WAVE_SCALE)
            h = int(raw_wave.get_height() * WAVE_SCALE)
            self.image = pygame.transform.scale(raw_wave, (w, h))
            
            self.rect = self.image.get_rect(center=pos)
            direction = pygame.Vector2(target_pos) - pygame.Vector2(pos)
            if direction.length() > 0:
                self.direction = direction.normalize()
            else:
                self.direction = pygame.Vector2(-1, 0)
            self.speed = 300

        def update(self, dt):
            self.rect.center += self.direction * self.speed * dt
            if not display_surface.get_rect().collidepoint(self.rect.center):
                self.kill()

    class DamagePopUp(pygame.sprite.Sprite):
        def __init__(self, amount, pos, groups):
            super().__init__(groups)
            self.image = DAMAGE_FONT.render(str(amount), True, (255, 60, 60))
            self.rect = self.image.get_rect(center=pos)
            self.timer = 0.3  
            self.vy = -80     

        def update(self, dt):
            self.timer -= dt
            self.rect.centery += self.vy * dt
            if self.timer <= 0:
                self.kill()

    class Player(pygame.sprite.Sprite):
        def __init__(self, groups):
            super().__init__(groups)
            try:
                self.raw_img = pygame.image.load(join("images", "player.png")).convert_alpha()
                self.image = self.raw_img.copy()
            except FileNotFoundError:
                self.image = pygame.Surface((50, 50))
                self.image.fill((0, 0, 255))
                self.raw_img = self.image.copy()
                
            self.rect = self.image.get_rect(center=(WINDOW_WIDTH / 4, WINDOW_HEIGHT / 2))
            self.direction = pygame.Vector2()
            self.speed = PLAYER_SPEED
            
            self.health = 100
            self.max_health = 100
            
            self.is_charging = False
            self.charge_time = 0.0
            self.is_throwing = False
            self.throw_timer = 0.0
            self.throw_duration = 0.12  
            
            self.current_scale = 1.0
            self.target_scale = 1.0
            self.rotation_angle = 0.0
            self.combat_side = 1 

            self.frozen_timer = 0.0
            self.is_frozen = False

        def update(self, dt):
            if self.is_frozen:
                self.frozen_timer -= dt
                if self.frozen_timer <= 0:
                    self.is_frozen = False
                self.is_charging = False
                return 

            self.movement(dt)
            self.handle_axe_states(dt)
     
        def movement(self, dt):
            keys = pygame.key.get_pressed()
            self.direction.x = (int(keys[pygame.K_RIGHT]) or int(keys[pygame.K_d])) - (int(keys[pygame.K_LEFT]) or int(keys[pygame.K_a]))
            self.direction.y = (int(keys[pygame.K_DOWN]) or int(keys[pygame.K_s])) - (int(keys[pygame.K_UP]) or int(keys[pygame.K_w]))
            
            if keys[pygame.K_d]:
                self.combat_side = 1
                try: self.image = self.raw_img
                except: pass
            elif keys[pygame.K_a]:
                self.combat_side = -1
                try: self.image = pygame.transform.flip(self.raw_img, True, False)
                except: pass

            if self.direction.length() > 0:
                self.direction = self.direction.normalize()
            self.rect.center += self.direction * self.speed * dt

        def handle_axe_states(self, dt):
            mouse_buttons = pygame.mouse.get_pressed()
            
            if mouse_buttons[2] and start and not win and not game_over:  
                if not self.is_charging and not self.is_throwing:
                    self.is_charging = True
                    self.charge_time = 0.0
                    self.rotation_angle = 0.0 
                
                if self.is_charging:
                    self.charge_time += dt
                    if self.charge_time >= TIME_THRESHOLD_3:   self.target_scale = SCALE_TARGET_3
                    elif self.charge_time >= TIME_THRESHOLD_2: self.target_scale = SCALE_TARGET_2
                    elif self.charge_time >= TIME_THRESHOLD_1: self.target_scale = SCALE_TARGET_1
                    else:                                      self.target_scale = 1.0
                    
                    self.current_scale += (self.target_scale - self.current_scale) * AXE_GROWTH_SPEED * dt
            else:
                if self.is_charging:  
                    self.is_charging = False
                    self.is_throwing = True
                    self.throw_timer = 0.0
                    
                    damage = 0
                    if self.current_scale >= SCALE_TARGET_3 - 1.0:   damage = DAMAGE_TIER_3
                    elif self.current_scale >= SCALE_TARGET_2 - 1.0: damage = DAMAGE_TIER_2
                    elif self.current_scale >= SCALE_TARGET_1 - 1.0: damage = DAMAGE_TIER_1
                    
                    self.rotation_angle = -70.0 * self.combat_side  
                    if damage > 0:
                        self.execute_strike(damage)

            if self.is_throwing:
                self.throw_timer += dt
                progress = self.throw_timer / self.throw_duration
                retract_factor = 1.0 - progress
                self.rotation_angle = retract_factor * (-70.0 * self.combat_side)

                if self.throw_timer >= self.throw_duration:
                    self.is_throwing = False
                    self.rotation_angle = 0.0
                    self.target_scale = 1.0
            
            if not self.is_charging and not self.is_throwing and self.current_scale > 1.0:
                self.current_scale += (1.0 - self.current_scale) * AXE_GROWTH_SPEED * dt

        def execute_strike(self, damage):
            current_w = int(AXE_BASE_WIDTH * self.current_scale)
            current_h = int(AXE_BASE_HEIGHT * self.current_scale)
            
            strike_rect = pygame.Rect(0, 0, current_w * 1.5, current_h * 1.5)
            if self.combat_side == 1:
                strike_rect.midleft = (self.rect.centerx, self.rect.centery)
            else:
                strike_rect.midright = (self.rect.centerx, self.rect.centery)

            if strike_rect.colliderect(enemy.rect) and enemy.alive():
                enemy.health -= damage
                rand_offset_x = random.randint(-25, 25)
                rand_offset_y = random.randint(-35, 5)
                popup_pos = (enemy.rect.centerx + rand_offset_x, enemy.rect.top + rand_offset_y)
                DamagePopUp(damage, popup_pos, [all_sprites, vfx_sprites])

            for skel in skeleton_sprites:
                if strike_rect.colliderect(skel.rect):
                    skel.kill()

            for proj in projectile_sprites:
                if isinstance(proj, BlueWave) and strike_rect.colliderect(proj.rect):
                    proj.kill()

        def draw_weapon(self, surface):
            if start and not win and not game_over:
                w = int(AXE_BASE_WIDTH * self.current_scale)
                h = int(AXE_BASE_HEIGHT * self.current_scale)
                if w < 5: w = 5
                if h < 5: h = 5
                
                transformed_axe = pygame.transform.scale(axe_orig_img, (w, h))
                if self.combat_side == -1:
                    transformed_axe = pygame.transform.flip(transformed_axe, True, False)
                    
                if self.rotation_angle != 0:
                    transformed_axe = pygame.transform.rotate(transformed_axe, self.rotation_angle)
                
                r_rect = transformed_axe.get_rect()
                target_x_offset = 20 * self.combat_side
                r_rect.center = (self.rect.centerx + target_x_offset, self.rect.centery)
                surface.blit(transformed_axe, r_rect.topleft)

        def draw_health_bar(self, surface):
            if self.alive() and start and not win:
                bar_width = 150
                bar_height = 14
                bar_x = 30
                bar_y = 30
                ratio = max(0.0, min(1.0, self.health / self.max_health))
                pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(surface, (0, 230, 50), (bar_x, bar_y, int(bar_width * ratio), bar_height))
                pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
                
                lbl = UI_FONT.render("PLAYER HP", True, (255, 255, 255))
                surface.blit(lbl, (bar_x, bar_y + 18))

                if self.is_frozen:
                    lbl_f = UI_FONT.render(f"FROZEN! ({self.frozen_timer:.1f}s)", True, (0, 191, 255))
                    surface.blit(lbl_f, (self.rect.centerx - 50, self.rect.top - 30))

    class Hector(pygame.sprite.Sprite):
        def __init__(self, groups, speed, scale_val):
            super().__init__(groups)
            try:
                self.image = pygame.image.load(join("images","hector","hectoridle.png")).convert_alpha()
            except FileNotFoundError:
                self.image = pygame.Surface((50, 50))
                self.image.fill((255, 0, 0))
                
            self.image = pygame.transform.scale_by(self.image, scale_val)
            self.rect = self.image.get_rect(center=((WINDOW_WIDTH * 0.8), (WINDOW_HEIGHT / 2)))
            self.speed = speed
            self.health = 100  
            self.max_health = 100
            self.wave_timer = 0.0
            self.wave_cooldown = 1.8

        def update(self, dt):
            # Hector can still move/re-position even if the player is frozen
            if player.alive():
                enemy_vector = pygame.math.Vector2(player.rect.x - self.rect.x, player.rect.y - self.rect.y)
                if enemy_vector.length() > 0:
                    enemy_vector = enemy_vector.normalize()
                self.rect.center += enemy_vector * self.speed * dt

            # Hector ALWAYS keeps firing waves, even when the player is frozen
            if start and not win and not game_over:
                self.wave_timer += dt
                if self.wave_timer >= self.wave_cooldown:
                    self.wave_timer = 0.0
                    BlueWave(self.rect.center, player.rect.center, [all_sprites, projectile_sprites])

        def draw_health_bar(self, surface):
            if self.alive() and start and not win:
                bar_width = 120
                bar_height = 12
                bar_x = self.rect.centerx - (bar_width // 2)
                bar_y = self.rect.top - 25
                ratio = max(0.0, min(1.0, self.health / self.max_health))
                pygame.draw.rect(surface, (50, 10, 10), (bar_x, bar_y, bar_width, bar_height))  
                pygame.draw.rect(surface, (230, 30, 30), (bar_x, bar_y, int(bar_width * ratio), bar_height))  
                pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)  

    class Skeleton(pygame.sprite.Sprite):
        def __init__(self, pos, groups):
            super().__init__(groups)
            self.frames = ske_imgs
            self.frame_index = 0
            self.image = pygame.transform.scale(self.frames[self.frame_index], (55, 75))
            self.rect = self.image.get_rect(center=pos)
            
            self.anim_timer = 0.0
            self.attack_timer = 0.0
            self.attack_cooldown = 2.5

        def update(self, dt):
            self.anim_timer += dt
            if self.anim_timer >= 0.3:
                self.anim_timer = 0.0
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = pygame.transform.scale(self.frames[self.frame_index], (55, 75))

            # CHANGED: Skeletons do not track attack cooldowns or throw attacks while the player is frozen
            if player.alive() and not player.is_frozen:
                self.attack_timer += dt
                if self.attack_timer >= self.attack_cooldown:
                    self.attack_timer = 0.0
                    PinkHeart(self.rect.center, player.rect.center, [all_sprites, projectile_sprites])

    player = Player(all_sprites)
    enemy = Hector((all_sprites, enemy_sprites), 0, ENEMY_SCALE)

    start = False
    border = pygame.Rect(0, 150, WINDOW_WIDTH, WINDOW_HEIGHT - 150) 
    win = False
    game_over = False
    
    hector_dead_delay = False
    win_timer_accum = 0.0
    skeleton_spawn_timer = 0.0

    is_paused = False

    while True:
        dt = clock.tick(60) / 1000.0
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        left_click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                left_click = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not win and not game_over:
                        is_paused = not is_paused

                if event.key == pygame.K_1 and not is_paused and not game_over:
                    start = True

        # --- PAUSE GAME OVERLAY LOOP ---
        if is_paused:
            pause_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            pause_overlay.fill((10, 10, 15, 8))
            display_surface.blit(pause_overlay, (0,0))
            
            lbl_paused = WIN_FONT.render("PAUSED", True, (240, 240, 255))
            display_surface.blit(lbl_paused, lbl_paused.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100)))

            btn_continue = pygame.Rect(WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT // 2, 280, 55)
            h_c = btn_continue.collidepoint(mouse_pos)
            pygame.draw.rect(display_surface, (70, 70, 85) if h_c else (45, 45, 55), btn_continue, border_radius=6)
            txt_c = UI_FONT.render("Continue", True, (255, 255, 255))
            display_surface.blit(txt_c, txt_c.get_rect(center=btn_continue.center))
            if h_c and left_click:
                is_paused = False

            btn_restart = pygame.Rect(WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT // 2 + 80, 280, 55)
            h_r = btn_restart.collidepoint(mouse_pos)
            pygame.draw.rect(display_surface, (160, 50, 50) if h_r else (110, 35, 35), btn_restart, border_radius=6)
            txt_r = UI_FONT.render("Restart", True, (255, 255, 255))
            display_surface.blit(txt_r, txt_r.get_rect(center=btn_restart.center))
            if h_r and left_click:
                return "escaped"

            pygame.display.update()
            continue

        # --- REGULAR ACTIVE SIMULATION UPDATE ---
        if not win and not game_over:
            if start:
                enemy.speed = ENEMY_SPEED  
                all_sprites.update(dt)

                if player.alive(): 
                    player.rect.clamp_ip(border)
                    
                    for proj in projectile_sprites:
                        if player.rect.colliderect(proj.rect):
                            if isinstance(proj, PinkHeart):
                                player.health -= 10
                                player.is_frozen = True
                                player.frozen_timer = 3.0
                                proj.kill()
                            elif isinstance(proj, BlueWave):
                                player.health -= 15  
                                proj.kill()

                    if player.health <= 0:
                        player.health = 0
                        game_over = True

                if enemy.alive():  
                    enemy.rect.clamp_ip(border)
                
                skeleton_spawn_timer += dt
                if skeleton_spawn_timer >= 5.0:
                    skeleton_spawn_timer = 0.0
                    rand_x = random.randint(border.left + 50, border.right - 50)
                    rand_y = random.randint(border.top + 50, border.bottom - 50)
                    Skeleton((rand_x, rand_y), [all_sprites, skeleton_sprites])

                if enemy.health <= 0 and enemy.alive() and not hector_dead_delay:
                    hector_dead_delay = True

            if hector_dead_delay:
                win_timer_accum += dt
                if win_timer_accum >= 2.0:
                    win = True
                    enemy.kill()
                    for skel in skeleton_sprites: 
                        skel.kill()

            display_surface.blit(background, (0, 0))
            all_sprites.draw(display_surface)
            player.draw_weapon(display_surface)
            player.draw_health_bar(display_surface)
            enemy.draw_health_bar(display_surface)

            if not start:
                lbl = UI_FONT.render("Press '1' to Start Final Showdown", True, (255, 255, 255))
                display_surface.blit(lbl, lbl.get_rect(center=(WINDOW_WIDTH // 2, 50)))
            elif player.is_charging:
                lbl = UI_FONT.render(f"CHARGING AXE: x{player.current_scale:.1f}", True, (0, 255, 255))
                display_surface.blit(lbl, lbl.get_rect(center=(player.rect.centerx, player.rect.top - 50)))

            bard.update()
            bard.draw(display_surface)
            pygame.display.update()

        # --- GAME OVER SCREEN ---
        elif game_over:
            display_surface.fill((20, 10, 10))
            go_surf = WIN_FONT.render('GAME OVER', True, (255, 50, 50))
            display_surface.blit(go_surf, go_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60)))
            
            btn_retry = pygame.Rect(WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT // 2 + 40, 280, 60)
            h_g = btn_retry.collidepoint(mouse_pos)
            pygame.draw.rect(display_surface, (140, 45, 45) if h_g else (100, 30, 30), btn_retry, border_radius=8)
            txt_g = UI_FONT.render("Try Again", True, (255, 255, 255))
            display_surface.blit(txt_g, txt_g.get_rect(center=btn_retry.center))
            pygame.display.update()

            if h_g and left_click:
                return "escaped"

        # --- DELAYED WIN COMPLETION SCREEN ---
        else:
            if player.alive(): 
                player.kill()
                
            display_surface.fill((10, 15, 10))
            text_surf = WIN_FONT.render('YOU WIN!', True, (0, 255, 100))
            display_surface.blit(text_surf, text_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 80)))
            
            btn_menu_rect = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT // 2 + 40, 320, 60)
            h_m = btn_menu_rect.collidepoint(mouse_pos)
            pygame.draw.rect(display_surface, (50, 120, 70) if h_m else (35, 85, 50), btn_menu_rect, border_radius=8)
            
            txt_m = UI_FONT.render("Return & Restart", True, (255, 255, 255))
            display_surface.blit(txt_m, txt_m.get_rect(center=btn_menu_rect.center))
            pygame.display.update()

            if h_m and left_click:
                return "completed"