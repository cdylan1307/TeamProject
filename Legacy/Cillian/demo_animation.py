import pygame
import sys
import os
import math

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Player & Patroclus Animation System")

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

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
                print(f"✓ Loaded: {img_path}")
            except Exception as e:
                print(f"✗ ERROR loading {img_path}: {e}")
        
        if not self.frames:
            # Create placeholder if no frames loaded
            print(f"WARNING: No frames loaded for {folder_path}, using placeholder")
            self.frames.append(pygame.Surface((64, 64)))
            self.frames[0].fill((255, 0, 255))
        else:
            print(f"Successfully loaded {len(self.frames)} frames from {folder_path}")
    
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


class Player:
    """Player character with WASD movement and attack"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.facing = "front"  # front, back, left, right
        self.state = "idle"  # idle, walking, attacking
        
        # Get base path for animations - use absolute path from script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.join(script_dir, "..", "animations", "Player")
        base_path = os.path.abspath(base_path)
        print(f"\nPlayer animations base path: {base_path}")
        print(f"Path exists: {os.path.exists(base_path)}\n")
        
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
    
    def handle_input(self, keys, mouse_buttons):
        """Handle WASD movement and mouse attack"""
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
        
        # Move player
        self.x += dx
        self.y += dy
        
        # Keep player on screen
        self.x = max(0, min(SCREEN_WIDTH - 64, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - 64, self.y))
        
        # Handle attack (left mouse button)
        if mouse_buttons[0] and self.attack_cooldown <= 0:
            self.state = "attacking"
            self.attack_cooldown = 30  # Cooldown frames
    
    def update(self):
        """Update player animation"""
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
        """Draw player on screen"""
        frame = self.current_animation.get_current_frame()
        if self.flip_x:
            frame = pygame.transform.flip(frame, True, False)
        surface.blit(frame, (self.x, self.y))
        
        # Draw health bar
        pygame.draw.rect(surface, BLACK, (self.x - 2, self.y - 12, 68, 8))
        pygame.draw.rect(surface, GREEN, (self.x, self.y - 10, 64, 4))


class Patroclus:
    """Patroclus NPC companion that follows player and heals periodically"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 3  # Slower than player
        self.facing = "front"  # front, left, right
        self.state = "idle"  # idle, walking, healing
        
        # Get base path for animations - use absolute path from script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.join(script_dir, "..", "animations", "Player")
        base_path = os.path.abspath(base_path)
        print(f"\nPatroclus animations base path: {base_path}")
        print(f"Path exists: {os.path.exists(base_path)}\n")
        
        # Load Patroclus animations
        self.animations = {
            "front_idle": Animation(os.path.join(base_path, "PatrocusFrontIdle Frames"), 8),
            "side_walk": Animation(os.path.join(base_path, "PatrocusSideWalk Frames"), 9),
            "healing": Animation(os.path.join(base_path, "PatrocusHealing Frames"), 20, loop=False)
        }
        
        self.current_animation = self.animations["front_idle"]
        self.flip_x = False
        
        # Healing timer (15 seconds = 900 frames at 60 FPS)
        self.heal_timer = 900
        self.healing_cooldown = 900  # 15 seconds
    
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
                self.heal_timer = self.healing_cooldown
        
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
        
        # Update current animation
        self.current_animation.update()
    
    def draw(self, surface):
        """Draw Patroclus on screen"""
        frame = self.current_animation.get_current_frame()
        if self.flip_x:
            frame = pygame.transform.flip(frame, True, False)
        surface.blit(frame, (self.x, self.y))
        
        # Draw healing timer indicator
        timer_width = 64 * (self.heal_timer / self.healing_cooldown)
        pygame.draw.rect(surface, BLACK, (self.x - 2, self.y - 12, 68, 8))
        pygame.draw.rect(surface, (100, 200, 255), (self.x, self.y - 10, timer_width, 4))
        
        # Draw "HEALING" text when healing
        if self.state == "healing":
            font = pygame.font.Font(None, 24)
            text = font.render("HEALING!", True, (0, 255, 0))
            text_rect = text.get_rect(center=(self.x + 32, self.y - 25))
            surface.blit(text, text_rect)


def main():
    """Main game loop"""
    # Create player and Patroclus
    player = Player(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
    patroclus = Patroclus(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2)
    
    # Instructions font
    font = pygame.font.Font(None, 28)
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Get input
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        
        # Update player
        player.handle_input(keys, mouse_buttons)
        player.update()
        
        # Update Patroclus (follow player)
        patroclus.follow_player(player.x, player.y)
        patroclus.update()
        
        # Draw everything
        screen.fill(GREY)
        
        # Draw instructions
        instructions = [
            "WASD - Move Player",
            "Left Click - Attack",
            "ESC - Exit"
        ]
        y_offset = 10
        for instruction in instructions:
            text = font.render(instruction, True, BLACK)
            screen.blit(text, (10, y_offset))
            y_offset += 30
        
        # Draw status
        status_text = f"Player State: {player.state.upper()} | Patroclus: {patroclus.state.upper()}"
        status = font.render(status_text, True, BLACK)
        screen.blit(status, (10, SCREEN_HEIGHT - 40))
        
        # Draw characters (draw Patroclus first so player appears on top)
        patroclus.draw(screen)
        player.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
