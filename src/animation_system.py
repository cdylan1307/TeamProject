import pygame
import os
import math

# Animation settings
ANIMATION_SPEED = 0.15  # Higher = faster animation

class Animation:
    """Handles loading and playing sprite animations"""
    def __init__(self, folder_path, frame_count, loop=True):
        self.frames = []
        self.frame_index = 0
        self.loop = loop
        self.finished = False
        
        # Load animation frames
        for i in range(frame_count):
            try:
                img_path = os.path.join(folder_path, f"pixil-frame-{i}.png")
                img = pygame.image.load(img_path).convert_alpha()
                self.frames.append(img)
            except Exception as e:
                pass  # Silently skip missing frames
        
        if not self.frames:
            # Use fallback - try to load default player.png
            try:
                fallback_img = pygame.image.load("sprites/player.png").convert_alpha()
                self.frames.append(fallback_img)
            except:
                # Create colored placeholder
                self.frames.append(pygame.Surface((64, 64)))
                self.frames[0].fill((255, 0, 255))
    
    def update(self, speed=ANIMATION_SPEED):
        """Update animation frame"""
        if not self.finished:
            self.frame_index += speed
            if self.frame_index >= len(self.frames):
                if self.loop:
                    self.frame_index = 0
                else:
                    self.frame_index = len(self.frames) - 1
                    self.finished = True
    
    def reset(self):
        """Reset animation to beginning"""
        self.frame_index = 0
        self.finished = False
    
    def get_current_frame(self):
        """Get current frame image"""
        return self.frames[int(self.frame_index)]


class AnimatedPlayer:
    """Player character with WASD movement and attack animations"""
    def __init__(self, x, y, scale=1.0):
        self.x = x
        self.y = y
        self.speed = 5
        self.facing = "front"  # front, back, left, right
        self.state = "idle"  # idle, walking, attacking
        self.scale = scale
        
        # Get base path for animations (go up one level from src to root, then to animations)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)  # Go up one level from src to root
        base_path = os.path.join(root_dir, "animations", "Player")
        base_path = os.path.abspath(base_path)
        
        # Load all animations
        self.animations = {
            "front_idle": Animation(os.path.join(base_path, "FrontIdle Frames"), 5),
            "front_walk": Animation(os.path.join(base_path, "FrontWalk Frames"), 10),
            "back_idle": Animation(os.path.join(base_path, "BackIdle Frames"), 8),
            "back_walk": Animation(os.path.join(base_path, "BackWalk Frames"), 8),
            "side_idle": Animation(os.path.join(base_path, "SideIdle Frames"), 6),
            "side_walk": Animation(os.path.join(base_path, "SideWalk Frames"), 10),
            "side_attack": Animation(os.path.join(base_path, "SideAttack Frames"), 7, loop=False)
        }
        
        self.current_animation = self.animations["front_idle"]
        self.flip_x = False  # For flipping sprite when facing left
        
        # Attack cooldown
        self.attack_cooldown = 0
    
    def update_movement(self, keys):
        """Handle WASD movement"""
        if self.state == "attacking" and not self.current_animation.finished:
            return  # Don't move while attacking
        
        # Reset state
        self.state = "idle"
        dx, dy = 0, 0
        
        # WASD movement
        if keys[pygame.K_w]:
            dy = -self.speed
            self.facing = "back"
            self.state = "walking"
        if keys[pygame.K_s]:
            dy = self.speed
            self.facing = "front"
            self.state = "walking"
        if keys[pygame.K_a]:
            dx = -self.speed
            self.facing = "left"
            self.state = "walking"
        if keys[pygame.K_d]:
            dx = self.speed
            self.facing = "right"
            self.state = "walking"
        
        # Move character
        self.x += dx
        self.y += dy
        
        return dx, dy
    
    def handle_attack(self, mouse_buttons):
        """Handle attack input (left mouse button)"""
        if mouse_buttons[0] and self.attack_cooldown <= 0:
            self.state = "attacking"
            self.attack_cooldown = 30  # Cooldown frames
            return True
        return False
    
    def update(self):
        """Update animation"""
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Determine which animation to play
        animation_key = None
        
        if self.state == "attacking":
            animation_key = "side_attack"
            self.flip_x = (self.facing == "left")
        elif self.state == "walking":
            if self.facing == "front":
                animation_key = "front_walk"
                self.flip_x = False
            elif self.facing == "back":
                animation_key = "back_walk"
                self.flip_x = False
            elif self.facing in ["left", "right"]:
                animation_key = "side_walk"
                self.flip_x = (self.facing == "left")
        else:  # idle
            if self.facing == "front":
                animation_key = "front_idle"
                self.flip_x = False
            elif self.facing == "back":
                animation_key = "back_idle"
                self.flip_x = False
            elif self.facing in ["left", "right"]:
                animation_key = "side_idle"
                self.flip_x = (self.facing == "left")
        
        # Switch animation if needed
        if animation_key and self.current_animation != self.animations[animation_key]:
            self.current_animation = self.animations[animation_key]
            self.current_animation.reset()
        
        # Check if attack finished
        if self.state == "attacking" and self.current_animation.finished:
            self.state = "idle"
        
        # Update current animation
        self.current_animation.update()
    
    def draw(self, surface):
        """Draw animated player on screen"""
        frame = self.current_animation.get_current_frame()
        if self.scale != 1.0:
            new_size = (int(frame.get_width() * self.scale), int(frame.get_height() * self.scale))
            frame = pygame.transform.scale(frame, new_size)
        if self.flip_x:
            frame = pygame.transform.flip(frame, True, False)
        surface.blit(frame, (self.x, self.y))
    
    def get_rect(self):
        """Get rectangle for collision detection"""
        frame = self.current_animation.get_current_frame()
        if self.scale != 1.0:
            new_size = (int(frame.get_width() * self.scale), int(frame.get_height() * self.scale))
            return pygame.Rect(self.x, self.y, new_size[0], new_size[1])
        return pygame.Rect(self.x, self.y, frame.get_width(), frame.get_height())


class AnimatedPatroclus:
    """Patroclus NPC companion that follows player and heals periodically"""
    def __init__(self, x, y, scale=1.0):
        self.x = x
        self.y = y
        self.speed = 3  # Slower than player
        self.facing = "front"  # front, left, right
        self.state = "idle"  # idle, walking, healing
        self.scale = scale
        
        # Get base path for animations (go up one level from src to root, then to animations)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)  # Go up one level from src to root
        base_path = os.path.join(root_dir, "animations", "Player")
        base_path = os.path.abspath(base_path)
        
        # Load Patroclus animations
        self.animations = {
            "front_idle": Animation(os.path.join(base_path, "PatrocusFrontIdle Frames"), 8),
            "side_walk": Animation(os.path.join(base_path, "PatrocusSideWalk Frames"), 9),
            "healing": Animation(os.path.join(base_path, "PatrocusHealing Frames"), 20, loop=False)
        }
        
        self.current_animation = self.animations["front_idle"]
        self.flip_x = False
        
        # Healing timer (3 seconds = 180 frames at 60 FPS)
        self.heal_timer = 180
        self.healing_cooldown = 180  # 3 seconds
    
    def follow_player(self, player_x, player_y):
        """Follow player at slower speed"""
        if self.state == "healing" and not self.current_animation.finished:
            return  # Don't move while healing
        
        # Calculate distance to player
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Keep some distance from player (don't overlap)
        min_distance = 80
        
        if distance > min_distance:
            # Normalize and move towards player
            dx = dx / distance * self.speed
            dy = dy / distance * self.speed
            
            self.x += dx
            self.y += dy
            
            self.state = "walking"
            
            # Determine facing direction
            if abs(dx) > abs(dy):
                if dx > 0:
                    self.facing = "right"
                else:
                    self.facing = "left"
            else:
                self.facing = "front"
        else:
            self.state = "idle"
            self.facing = "front"
    
    def update(self):
        """Update Patroclus animation and healing timer"""
        # Update healing timer
        if self.state != "healing":
            self.heal_timer -= 1
            if self.heal_timer <= 0:
                # Start healing animation
                self.state = "healing"
                print(f"✓ Patroclus starts healing animation!")
        
        # Determine which animation to play
        animation_key = None
        
        if self.state == "healing":
            animation_key = "healing"
            self.flip_x = False
        elif self.state == "walking":
            # Always use side walking animation when moving (regardless of direction)
            animation_key = "side_walk"
            self.flip_x = (self.facing == "left")
        else:  # idle
            # Use front idle when not moving
            animation_key = "front_idle"
            self.flip_x = False
        
        # Switch animation if needed
        if animation_key and self.current_animation != self.animations[animation_key]:
            self.current_animation = self.animations[animation_key]
            self.current_animation.reset()
        
        # Check if healing finished
        if self.state == "healing" and self.current_animation.finished:
            self.state = "idle"
            self.heal_timer = self.healing_cooldown  # Reset timer after healing completes
            print(f"✓ Patroclus healing animation complete! Returning heal signal.")
            # Return healing signal to indicate healing effect should trigger
            return "healing_complete"
        
        # Update current animation
        self.current_animation.update()
        
        # Return None by default
        return None
    
    def draw(self, surface):
        """Draw Patroclus on screen"""
        frame = self.current_animation.get_current_frame()
        if self.scale != 1.0:
            new_size = (int(frame.get_width() * self.scale), int(frame.get_height() * self.scale))
            frame = pygame.transform.scale(frame, new_size)
        if self.flip_x:
            frame = pygame.transform.flip(frame, True, False)
        surface.blit(frame, (self.x, self.y))
        
        # Draw "HEALING" text when healing
        if self.state == "healing":
            font = pygame.font.Font(None, 24)
            text = font.render("HEALING!", True, (0, 255, 0))
            text_rect = text.get_rect(center=(self.x + 32, self.y - 25))
            surface.blit(text, text_rect)
    
    def get_rect(self):
        """Get rectangle for collision detection"""
        frame = self.current_animation.get_current_frame()
        if self.scale != 1.0:
            new_size = (int(frame.get_width() * self.scale), int(frame.get_height() * self.scale))
            return pygame.Rect(self.x, self.y, new_size[0], new_size[1])
        return pygame.Rect(self.x, self.y, frame.get_width(), frame.get_height())