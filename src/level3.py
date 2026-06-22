import pygame
import sys
import os
from os.path import join
import math
import random

# IMPORT THE CUTSCENE FILE
from . import cutscene
from .animation_system import AnimatedPlayer  # Import animation system for player

def start_level_3(bard, timer=None, player_name="", game_sounds_enabled=True):
    # Pause timer during cutscenes
    if timer and timer.is_running:
        timer.pause()
    
    # Play intermission cutscene (between level 2 and 3)
    display_surface = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Pixel Game - Level 3: Dual Hand Slashes")
    
    intermission_result = cutscene.play_cutscene(display_surface, "intermission")
    # Continue regardless of skip
    
    # Play Level 3 cutscene
    level3_cutscene_result = cutscene.play_cutscene(display_surface, "level3")
    # Continue regardless of skip
    
    # Resume timer after cutscenes
    if timer and timer.is_running:
        timer.resume()
    
    pygame.init()
    pygame.font.init()

    # Load axes sound effect
    axes_sound = None
    if os.path.exists("audio/axes.mp3"):
        try:
            axes_sound = pygame.mixer.Sound("audio/axes.mp3")
        except pygame.error:
            axes_sound = None

    # Load fail sound effect
    fail_sound = None
    if os.path.exists("audio/fail.mp3"):
        try:
            fail_sound = pygame.mixer.Sound("audio/fail.mp3")
        except pygame.error:
            fail_sound = None

    # Load win sound effect
    win_sound = None
    if os.path.exists("audio/win.mp3"):
        try:
            win_sound = pygame.mixer.Sound("audio/win.mp3")
        except pygame.error:
            win_sound = None

    # Load hector sound effect
    hector_sound = None
    if os.path.exists("audio/hector.mp3"):
        try:
            hector_sound = pygame.mixer.Sound("audio/hector.mp3")
        except pygame.error:
            hector_sound = None

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
    SCALE_TARGET_3        = 17.0  

    DAMAGE_TIER_1         = 10
    DAMAGE_TIER_2         = 15
    DAMAGE_TIER_3         = 40

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
        axe_orig_img = pygame.image.load("sprites/axes.png").convert_alpha()
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
    for name in ["sprites/ske1.png", "sprites/ske2.png"]:
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
            
            # Determine if wave should be flipped based on Hector's position relative to player
            should_flip = target_pos[0] < pos[0]  # Flip if target (player) is to the left of source (Hector)
            
            if should_flip:
                raw_wave = font.render("(((", True, (0, 191, 255))  # Use ((( when flipped (facing left)
            else:
                raw_wave = font.render(")))", True, (0, 191, 255))  # Use ))) when normal (facing right)
            
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
                self.raw_img = pygame.image.load(join("sprites", "player.png")).convert_alpha()
                self.image = self.raw_img.copy()
            except FileNotFoundError:
                self.image = pygame.Surface((50, 50))
                self.image.fill((0, 0, 255))
                self.raw_img = self.image.copy()
                
            self.rect = self.image.get_rect(center=(WINDOW_WIDTH / 4, WINDOW_HEIGHT / 2))
            self.direction = pygame.Vector2()
            self.speed = PLAYER_SPEED
            
            # Initialize animated player
            self.animated_player = AnimatedPlayer(self.rect.x, self.rect.y, scale=1.0)
            
            self.health = 500
            self.max_health = 500
            
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
            
            # Update animated player
            self.animated_player.x = self.rect.x
            self.animated_player.y = self.rect.y
            self.animated_player.update()
     
        def movement(self, dt):
            keys = pygame.key.get_pressed()
            
            # Update animated player movement
            dx, dy = self.animated_player.update_movement(keys)
            
            # Update combat side based on A/D keys - THIS IS THE KEY CHANGE
            if keys[pygame.K_d]:
                self.combat_side = 1  # Right side
                try: 
                    self.image = self.raw_img
                    self.animated_player.facing = "right"
                except: pass
            elif keys[pygame.K_a]:
                self.combat_side = -1  # Left side
                try: 
                    self.image = pygame.transform.flip(self.raw_img, True, False)
                    self.animated_player.facing = "left"
                except: pass
            
            # Use animation system's movement calculation
            self.direction.x = dx / self.animated_player.speed if self.animated_player.speed > 0 else 0
            self.direction.y = dy / self.animated_player.speed if self.animated_player.speed > 0 else 0
            
            # Scale by speed and time
            if dx != 0 or dy != 0:
                # Calculate new position
                movement_vector = pygame.Vector2(dx, dy) * (self.speed / self.animated_player.speed) * dt
                new_x = self.rect.centerx + movement_vector.x
                new_y = self.rect.centery + movement_vector.y
                
                # Check if new position would be within ellipse boundary
                if is_within_ellipse(new_x, new_y, ellipse_center_x, ellipse_center_y, ellipse_radius_x, ellipse_radius_y):
                    # Movement is allowed
                    self.rect.center += movement_vector
                # If outside boundary, don't move (player just stops at the edge)

        def handle_axe_states(self, dt):
            mouse_buttons = pygame.mouse.get_pressed()
            
            # CHANGED: Use left mouse button (index 0) instead of right mouse button (index 2)
            if mouse_buttons[0] and start and not win and not game_over:  
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
                    # Play axes sound when releasing the attack
                    if game_sounds_enabled and axes_sound:
                        axes_sound.play()
                    
                    self.is_charging = False
                    self.is_throwing = True
                    self.throw_timer = 0.0
                    
                    damage = 0
                    if self.current_scale >= SCALE_TARGET_3 - 1.0:   damage = DAMAGE_TIER_3
                    elif self.current_scale >= SCALE_TARGET_2 - 1.0: damage = DAMAGE_TIER_2
                    elif self.current_scale >= SCALE_TARGET_1 - 1.0: damage = DAMAGE_TIER_1
                    
                    # Rotation direction depends on which side we're facing
                    if self.combat_side == 1:  # Facing right
                        self.rotation_angle = -70.0  # Swing downward from right
                    else:  # Facing left  
                        self.rotation_angle = 70.0   # Swing downward from left
                        
                    if damage > 0:
                        self.execute_strike(damage)

            if self.is_throwing:
                self.throw_timer += dt
                progress = self.throw_timer / self.throw_duration
                retract_factor = 1.0 - progress
                
                # Retract the axe back to neutral position
                if self.combat_side == 1:  # Right side
                    self.rotation_angle = retract_factor * -70.0
                else:  # Left side
                    self.rotation_angle = retract_factor * 70.0

                if self.throw_timer >= self.throw_duration:
                    self.is_throwing = False
                    self.rotation_angle = 0.0
                    self.target_scale = 1.0
            
            if not self.is_charging and not self.is_throwing and self.current_scale > 1.0:
                self.current_scale += (1.0 - self.current_scale) * AXE_GROWTH_SPEED * dt

        def execute_strike(self, damage):
            current_w = int(AXE_BASE_WIDTH * self.current_scale)
            current_h = int(AXE_BASE_HEIGHT * self.current_scale)
            
            # Create strike area that adjusts based on facing direction
            strike_rect = pygame.Rect(0, 0, current_w * 1.5, current_h * 1.5)
            if self.combat_side == 1:  # Facing right
                strike_rect.midleft = (self.rect.centerx, self.rect.centery)
            else:  # Facing left
                strike_rect.midright = (self.rect.centerx, self.rect.centery)

            # Check for enemy hits
            if strike_rect.colliderect(enemy.rect) and enemy.alive():
                enemy.health -= damage
                enemy.trigger_damage_animation()  # Trigger damage animation
                rand_offset_x = random.randint(-25, 25)
                rand_offset_y = random.randint(-35, 5)
                popup_pos = (enemy.rect.centerx + rand_offset_x, enemy.rect.top + rand_offset_y)
                DamagePopUp(damage, popup_pos, [all_sprites, vfx_sprites])

            # Check for skeleton hits
            for skel in skeleton_sprites:
                if strike_rect.colliderect(skel.rect):
                    skel.kill()

            # Check for projectile deflection
            for proj in projectile_sprites:
                if isinstance(proj, BlueWave) and strike_rect.colliderect(proj.rect):
                    proj.kill()

        def draw_animated_player(self, surface):
            """Draw the animated version of the player"""
            self.animated_player.draw(surface)

        def draw_weapon(self, surface):
            if start and not win and not game_over:
                w = int(AXE_BASE_WIDTH * self.current_scale)
                h = int(AXE_BASE_HEIGHT * self.current_scale)
                if w < 5: w = 5
                if h < 5: h = 5
                
                # Create the scaled axe
                transformed_axe = pygame.transform.scale(axe_orig_img, (w, h))
                
                # FLIP THE AXE based on combat side (left/right)
                if self.combat_side == -1:  # Left side - flip the axe horizontally
                    transformed_axe = pygame.transform.flip(transformed_axe, True, False)
                
                # Apply rotation if throwing
                if self.rotation_angle != 0:
                    transformed_axe = pygame.transform.rotate(transformed_axe, self.rotation_angle)
                
                # Position the axe relative to the player
                r_rect = transformed_axe.get_rect()
                target_x_offset = 25 * self.combat_side  # Positive for right, negative for left
                target_y_offset = -5  # Slightly above center
                r_rect.center = (self.rect.centerx + target_x_offset, self.rect.centery + target_y_offset)
                
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
            
            # Load all animation frames
            self.animations = {}
            
            # Load idle animation
            try:
                self.animations['idle'] = pygame.image.load(join("images","hector","hectoridle.png")).convert_alpha()
            except FileNotFoundError:
                self.animations['idle'] = pygame.Surface((50, 50))
                self.animations['idle'].fill((255, 0, 0))
            
            # Load attack animations
            self.animations['attack'] = []
            for i in range(1, 3):  # hectorattack1.png to hectorattack2.png
                try:
                    attack_frame = pygame.image.load(join("images","hector",f"hectorattack{i}.png")).convert_alpha()
                    self.animations['attack'].append(attack_frame)
                except FileNotFoundError:
                    # Fallback attack frame
                    attack_frame = pygame.Surface((50, 50))
                    attack_frame.fill((255, 100, 100))  # Slightly different red
                    self.animations['attack'].append(attack_frame)
            
            # Load damaged animation
            try:
                self.animations['damaged'] = pygame.image.load(join("images","hector","hectordamaged.png")).convert_alpha()
            except FileNotFoundError:
                self.animations['damaged'] = pygame.Surface((50, 50))
                self.animations['damaged'].fill((200, 0, 0))  # Darker red
            
            # Load defeated animation
            try:
                self.animations['defeated'] = pygame.image.load(join("images","hector","hectordefeated.png")).convert_alpha()
            except FileNotFoundError:
                self.animations['defeated'] = pygame.Surface((50, 50))
                self.animations['defeated'].fill((100, 0, 0))  # Dark red
            
            # Animation state
            self.animation_state = 'idle'
            self.animation_timer = 0.0
            self.attack_frame_index = 0
            
            # Set initial image and scale
            self.image = pygame.transform.scale_by(self.animations['idle'], scale_val)
            self.scale_val = scale_val
            self.rect = self.image.get_rect(center=((WINDOW_WIDTH * 0.8), (WINDOW_HEIGHT / 2)))
            
            self.speed = speed
            self.health = 150  
            self.max_health = 150
            self.wave_timer = 0.0
            self.wave_cooldown = 0.5
            
            # Skeleton summoning ability
            self.summon_timer = 0.0
            self.summon_cooldown = 3.0  # Summon skeletons every 2.0 seconds
            self.summon_animation_duration = 2.3
            
            # Attack cooldown to prevent spamming
            self.attack_timer = 0.0
            self.attack_cooldown = 0.7  # Can only attack once per second

        def set_animation_state(self, state):
            """Change animation state and reset timer"""
            if self.animation_state != state:
                self.animation_state = state
                self.animation_timer = 0.0
                self.attack_frame_index = 0

        def update_animation(self, dt):
            """Update animation based on current state"""
            self.animation_timer += dt
            
            # Determine if Hector should be flipped based on player position
            should_flip = False
            if player.alive():
                # Flip if player is on Hector's left side
                should_flip = player.rect.centerx < self.rect.centerx
            
            if self.animation_state == 'attack':
                # Attack animation: 0.5 seconds total (0.1s per frame)
                if self.animation_timer >= 0.1:
                    self.animation_timer = 0.0
                    self.attack_frame_index += 1
                    if self.attack_frame_index >= len(self.animations['attack']):
                        # Attack animation finished, return to idle
                        self.set_animation_state('idle')
                        return
                
                # Update image to current attack frame
                current_frame = self.animations['attack'][self.attack_frame_index]
                scaled_frame = pygame.transform.scale_by(current_frame, self.scale_val)
                # Flip attack animation if player is on left side
                self.image = pygame.transform.flip(scaled_frame, should_flip, False)
                
            elif self.animation_state == 'damaged':
                # Damaged animation: 0.1 seconds
                if self.animation_timer >= 0.1:
                    self.set_animation_state('idle')
                else:
                    scaled_frame = pygame.transform.scale_by(self.animations['damaged'], self.scale_val)
                    # Flip damaged animation if player is on left side
                    self.image = pygame.transform.flip(scaled_frame, should_flip, False)
                    
            elif self.animation_state == 'defeated':
                # Defeated/summoning animation: 0.3 seconds - then return to idle
                if self.animation_timer >= 0.3:
                    self.set_animation_state('idle')
                else:
                    scaled_frame = pygame.transform.scale_by(self.animations['defeated'], self.scale_val)
                    # Flip defeated animation if player is on left side
                    self.image = pygame.transform.flip(scaled_frame, should_flip, False)
                    
            else:  # idle
                scaled_frame = pygame.transform.scale_by(self.animations['idle'], self.scale_val)
                # Flip idle animation if player is on left side
                self.image = pygame.transform.flip(scaled_frame, should_flip, False)

        def trigger_attack_animation(self):
            """Trigger attack animation when touching player"""
            self.set_animation_state('attack')
            # Play hector attack sound
            if game_sounds_enabled and hector_sound:
                hector_sound.play()

        def trigger_damage_animation(self):
            """Trigger damage animation when hit by player"""
            self.set_animation_state('damaged')

        def trigger_defeated_animation(self):
            """Trigger defeated animation when health reaches 0"""
            self.set_animation_state('defeated')
            
        def trigger_summon_animation(self):
            """Trigger summoning animation to awaken skeletons"""
            self.set_animation_state('defeated')  # Use defeated animation for summoning

        def update(self, dt):
            # Update animation first
            self.update_animation(dt)
            
            # Update attack cooldown timer
            if self.attack_timer > 0:
                self.attack_timer -= dt
            
            if player.alive():
                enemy_vector = pygame.math.Vector2(player.rect.x - self.rect.x, player.rect.y - self.rect.y)
                if enemy_vector.length() > 0:
                    enemy_vector = enemy_vector.normalize()
                self.rect.center += enemy_vector * self.speed * dt
                
                # Check if touching player and trigger attack animation
                if self.rect.colliderect(player.rect):
                    # Only attack if cooldown has expired and not already attacking
                    if self.animation_state != 'attack' and self.attack_timer <= 0:
                        self.trigger_attack_animation()
                        self.attack_timer = self.attack_cooldown  # Reset cooldown

            if start and not win and not game_over:
                # Regular wave attacks
                self.wave_timer += dt
                if self.wave_timer >= self.wave_cooldown:
                    self.wave_timer = 0.0
                    BlueWave(self.rect.center, player.rect.center, [all_sprites, projectile_sprites])
                
                # Skeleton summoning ability
                self.summon_timer += dt
                if self.summon_timer >= self.summon_cooldown and self.animation_state != 'defeated':
                    self.summon_timer = 0.0
                    self.trigger_summon_animation()
                    # Return True to signal that skeletons should be spawned
                    return "summon_skeletons"
            
            return None

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
            
            # Fade-in effect
            self.fade_timer = 0.0
            self.fade_duration = 0.5  # 0.5 seconds to fade in
            self.alpha = 0  # Start invisible
            
        def update(self, dt):
            # Handle fade-in effect
            if self.fade_timer < self.fade_duration:
                self.fade_timer += dt
                # Calculate alpha from 0 to 255 over fade_duration
                progress = min(1.0, self.fade_timer / self.fade_duration)
                self.alpha = int(255 * progress)
            else:
                self.alpha = 255  # Fully visible
            
            # Animation update
            self.anim_timer += dt
            if self.anim_timer >= 0.3:
                self.anim_timer = 0.0
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = pygame.transform.scale(self.frames[self.frame_index], (55, 75))
                
            # Apply alpha to image
            self.image.set_alpha(self.alpha)

            # Attack logic (only when fully visible)
            if player.alive() and not player.is_frozen and self.alpha >= 255:
                self.attack_timer += dt
                if self.attack_timer >= self.attack_cooldown:
                    self.attack_timer = 0.0
                    PinkHeart(self.rect.center, player.rect.center, [all_sprites, projectile_sprites])

    player = Player(all_sprites)
    enemy = Hector((all_sprites, enemy_sprites), 0, ENEMY_SCALE)

    start = False
    # Elliptical boundary instead of rectangular
    ellipse_center_x = WINDOW_WIDTH // 2
    ellipse_center_y = (150 + (WINDOW_HEIGHT - 150)) // 2  # Center of the available area
    ellipse_width = WINDOW_WIDTH  # Horizontal diameter
    ellipse_height = WINDOW_HEIGHT - 150  # Vertical diameter
    ellipse_radius_x = ellipse_width // 2
    ellipse_radius_y = ellipse_height // 2
    
    def is_within_ellipse(x, y, center_x, center_y, radius_x, radius_y):
        """Check if a point is within the elliptical boundary"""
        dx = x - center_x
        dy = y - center_y
        return (dx * dx) / (radius_x * radius_x) + (dy * dy) / (radius_y * radius_y) <= 1
    
    def keep_in_ellipse(sprite, center_x, center_y, radius_x, radius_y):
        """Keep a sprite within an elliptical boundary by preventing movement outside"""
        # Check if current position is outside ellipse
        if not is_within_ellipse(sprite.rect.centerx, sprite.rect.centery, center_x, center_y, radius_x, radius_y):
            # Find the closest point on the ellipse edge
            dx = sprite.rect.centerx - center_x
            dy = sprite.rect.centery - center_y
            
            if dx == 0 and dy == 0:
                return  # Sprite is at center, no need to move
            
            angle = math.atan2(dy, dx)
            # Calculate ellipse edge position at this angle
            edge_x = center_x + math.cos(angle) * radius_x
            edge_y = center_y + math.sin(angle) * radius_y
            sprite.rect.centerx = int(edge_x)
            sprite.rect.centery = int(edge_y)
    
    # Keep border rect for skeleton spawning compatibility
    border = pygame.Rect(0, 150, WINDOW_WIDTH, WINDOW_HEIGHT - 150) 
    win = False
    game_over = False
    
    # Audio flags
    audio_fail_played = False
    audio_win_played = False
    
    hector_dead_delay = False
    win_timer_accum = 0.0
    skeleton_spawn_timer = 0.0
    summon_delay_timer = 0.0  # Timer to wait for summon animation to finish

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
                
                # Update all sprites and check for special actions
                for sprite in all_sprites:
                    if sprite == enemy:
                        summon_result = sprite.update(dt)
                        if summon_result == "summon_skeletons":
                            summon_delay_timer = 0.3  # Wait for animation to finish
                    else:
                        sprite.update(dt)
                
                # Handle skeleton summoning after animation delay
                if summon_delay_timer > 0:
                    summon_delay_timer -= dt
                    if summon_delay_timer <= 0:
                        # Spawn 2-3 skeletons when Hector summons
                        num_skeletons = random.randint(2, 3)
                        for _ in range(num_skeletons):
                            rand_x = random.randint(border.left + 50, border.right - 50)
                            rand_y = random.randint(border.top + 50, border.bottom - 50)
                            Skeleton((rand_x, rand_y), [all_sprites, skeleton_sprites])

                if player.alive(): 
                    # Player now handles its own boundary checking in movement()
                    pass
                    
                    for proj in projectile_sprites:
                        if player.rect.colliderect(proj.rect):
                            if isinstance(proj, PinkHeart):
                                player.health -= 5
                                player.is_frozen = True
                                player.frozen_timer = 1.0
                                proj.kill()
                            elif isinstance(proj, BlueWave):
                                player.health -= 7  
                                proj.kill()

                    if player.health <= 0:
                        player.health = 0
                        game_over = True

                if enemy.alive():  
                    keep_in_ellipse(enemy, ellipse_center_x, ellipse_center_y, ellipse_radius_x, ellipse_radius_y)

                # Check if Hector is actually defeated (health reaches 0)
                if enemy.health <= 0 and enemy.alive() and not hector_dead_delay:
                    enemy.trigger_defeated_animation()  # Final defeated animation
                    hector_dead_delay = True

            if hector_dead_delay:
                win_timer_accum += dt
                if win_timer_accum >= 0.5:
                    win = True
                    enemy.kill()
                    for skel in skeleton_sprites: 
                        skel.kill()

            display_surface.blit(background, (0, 0))
            
            # Draw sprites - use animated player
            for sprite in all_sprites:
                if sprite == player:
                    player.draw_animated_player(display_surface)
                else:
                    display_surface.blit(sprite.image, sprite.rect)
            
            player.draw_weapon(display_surface)
            player.draw_health_bar(display_surface)
            enemy.draw_health_bar(display_surface)

            # Add timer and player name display
            if timer and timer.is_running and player_name:
                timer_text = UI_FONT.render(f"Time: {timer.format_time()}", True, (255, 255, 255))
                display_surface.blit(timer_text, (WINDOW_WIDTH - timer_text.get_width() - 30, 30))
                
                player_text = UI_FONT.render(f"Player: {player_name}", True, (255, 255, 255))
                display_surface.blit(player_text, (WINDOW_WIDTH - player_text.get_width() - 30, 65))

            if not start:
                lbl = UI_FONT.render("Press '1' to Start Final Showdown", True, (255, 255, 255))
                display_surface.blit(lbl, lbl.get_rect(center=(WINDOW_WIDTH // 2, 50)))
                control_lbl = UI_FONT.render("Hold LEFT MOUSE to charge and release to attack", True, (200, 200, 255))
                display_surface.blit(control_lbl, control_lbl.get_rect(center=(WINDOW_WIDTH // 2, 80)))
                control_lbl2 = UI_FONT.render("Press A/D to turn left/right and flip your axe", True, (180, 180, 255))
                display_surface.blit(control_lbl2, control_lbl2.get_rect(center=(WINDOW_WIDTH // 2, 110)))
                
                # Pause timer while waiting for '1' to start
                if timer and timer.is_running and not timer.is_paused:
                    timer.pause()
                    
            elif player.is_charging:
                # Resume timer when gameplay actually starts
                if timer and timer.is_running and timer.is_paused:
                    timer.resume()
                    
                lbl = UI_FONT.render(f"CHARGING AXE: x{player.current_scale:.1f}", True, (0, 255, 255))
                display_surface.blit(lbl, lbl.get_rect(center=(player.rect.centerx, player.rect.top - 50)))
                
                # Show which direction player is facing
                direction_text = "RIGHT" if player.combat_side == 1 else "LEFT"
                dir_lbl = UI_FONT.render(f"Facing: {direction_text}", True, (255, 255, 0))
                display_surface.blit(dir_lbl, dir_lbl.get_rect(center=(player.rect.centerx, player.rect.top - 25)))
            else:
                # Resume timer when gameplay actually starts  
                if timer and timer.is_running and timer.is_paused:
                    timer.resume()

            bard.update()
            bard.draw(display_surface)
            pygame.display.update()

        # --- GAME OVER SCREEN ---
        elif game_over:
            # Play fail sound once
            if not audio_fail_played:
                if game_sounds_enabled and fail_sound:
                    fail_sound.play()
                audio_fail_played = True
                
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
            
            # Play win sound once before cutscene
            if not audio_win_played:
                if game_sounds_enabled and win_sound:
                    win_sound.play()
                audio_win_played = True
            
            # Pause timer during victory cutscene
            if timer and timer.is_running:
                timer.pause()
                
            # Automatically play victory cutscene
            cutscene.play_cutscene(display_surface, "victory")
            
            # Resume timer after cutscene
            if timer and timer.is_running:
                timer.resume()
                
            return "completed"