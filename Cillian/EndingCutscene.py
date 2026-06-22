import pygame
import os
from os.path import join

# Initialize Pygame
pygame.init()

# Screen settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Achilles: The End of a Legend")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
RED = (200, 50, 50)
BLUE = (100, 100, 200)
SAND = (194, 178, 128)
OCEAN = (0, 105, 148)
SUNSET_ORANGE = (255, 140, 0)
PURPLE = (100, 50, 150)

# Font
title_font = pygame.font.Font(None, 72)
dialogue_font = pygame.font.Font(None, 36)
subtext_font = pygame.font.Font(None, 24)

def load_animation_frames(animation_path, scale=3.0):
    """Load animation frames from a folder"""
    frames = []
    if os.path.exists(animation_path):
        for filename in sorted(os.listdir(animation_path)):
            if filename.endswith('.png'):
                img = pygame.image.load(os.path.join(animation_path, filename)).convert_alpha()
                img = pygame.transform.scale_by(img, scale)
                frames.append(img)
    return frames

def load_all_animations():
    """Load all player animations"""
    base_path = "animations/Player"
    
    animations = {
        'side_walk': load_animation_frames(os.path.join(base_path, "SideWalk Frames")),
        'side_idle': load_animation_frames(os.path.join(base_path, "SideIdle Frames")),
        'front_walk': load_animation_frames(os.path.join(base_path, "FrontWalk Frames")),
        'front_idle': load_animation_frames(os.path.join(base_path, "FrontIdle Frames")),
        'back_walk': load_animation_frames(os.path.join(base_path, "BackWalk Frames")),
        'back_idle': load_animation_frames(os.path.join(base_path, "BackIdle Frames")),
        'archer_attack': load_animation_frames("images/archerattack", scale=4.0),
    }
    return animations

def load_background():
    """Load the background image"""
    bg_path = "images/lv2background.jpg"
    if os.path.exists(bg_path):
        bg = pygame.image.load(bg_path).convert()
        return pygame.transform.scale(bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
    return None

class DialogueBox:
    def __init__(self):
        self.font = dialogue_font
        self.texts = []
        self.current_index = 0
        self.alpha = 0
        self.showing = False
        self.timer = 0
        self.display_time = 4000  # 4 seconds per dialogue
        
    def set_dialogue(self, texts):
        self.texts = texts
        self.current_index = 0
        self.alpha = 255
        self.showing = True
        
    def update(self, dt):
        if not self.showing:
            return
            
        self.timer += dt * 1000
        if self.timer >= self.display_time:
            self.timer = 0
            self.current_index += 1
            if self.current_index >= len(self.texts):
                self.showing = False
                
    def draw(self, surface):
        if not self.showing or self.current_index >= len(self.texts):
            return
            
        # Draw dialogue box background
        box_rect = pygame.Rect(100, WINDOW_HEIGHT - 150, WINDOW_WIDTH - 200, 120)
        bg = pygame.Surface((box_rect.width, box_rect.height))
        bg.set_alpha(200)
        bg.fill(BLACK)
        surface.blit(bg, box_rect.topleft)
        
        # Draw border
        pygame.draw.rect(surface, GOLD, box_rect, 3)
        
        # Draw text
        text = self.font.render(self.texts[self.current_index], True, WHITE)
        text_rect = text.get_rect(center=box_rect.center)
        surface.blit(text, text_rect)

class EndingCutscene:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "intro"  # intro, walking, adventures, death, fade_out
        self.state_timer = 0
        
        # Load animations and background
        self.animations = load_all_animations()
        self.background = load_background()
        self.frame_index = 0
        self.animation_speed = 0.15
        
        # Player position and movement
        self.player_x = 200
        self.player_y = WINDOW_HEIGHT - 200
        self.walk_speed = 100
        
        # Adventure flash timer
        self.adventure_timer = 0
        self.adventure_locations = []
        
        # Archer animation
        self.archer_frame = 0
        self.archer_x = WINDOW_WIDTH - 200
        self.archer_y = WINDOW_HEIGHT - 300
        self.archer_anim_speed = 0.1
        
        # Death animation
        self.arrow_fired = False
        self.arrow_pos = [WINDOW_WIDTH + 50, 0]
        self.arrow_target = [0, 0]
        self.arrow_speed = 1000
        self.hit = False
        self.player_falling = False
        self.fall_rotation = 0
        
        # Fade effect
        self.fade_alpha = 0
        self.fade_direction = 1
        
        # Dialogue
        self.dialogue_box = DialogueBox()
        
    def draw_background(self, state):
        """Draw different backgrounds based on state"""
        if self.background:
            # Use the game background for all states
            screen.blit(self.background, (0, 0))
            
            # Add atmospheric overlays based on state
            if state == "intro":
                # Victory glow overlay
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                overlay.set_alpha(80)
                overlay.fill((255, 215, 0))  # Golden glow
                screen.blit(overlay, (0, 0))
                
            elif state == "death":
                # Dark dramatic overlay
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                overlay.set_alpha(100)
                overlay.fill((50, 0, 50))  # Purple/dark overlay
                screen.blit(overlay, (0, 0))
        else:
            # Fallback if background doesn't load
            screen.fill((135, 206, 235))
            
    def draw_player(self, frame, falling=False):
        """Draw the player sprite"""
        if self.animations['side_walk']:
            frames = self.animations['side_walk']
            if frame < len(frames):
                img = frames[frame]
                
                # Apply rotation if falling
                if falling:
                    img = pygame.transform.rotate(img, self.fall_rotation)
                
                rect = img.get_rect(midbottom=(self.player_x, self.player_y))
                screen.blit(img, rect)
                
    def draw_archer(self):
        """Draw the archer using attack animation frames"""
        if self.animations['archer_attack'] and self.state == "death":
            frames = self.animations['archer_attack']
            if int(self.archer_frame) < len(frames):
                img = frames[int(self.archer_frame)]
                # Flip to face left toward Achilles
                img = pygame.transform.flip(img, True, False)
                rect = img.get_rect(midbottom=(self.archer_x, self.archer_y))
                screen.blit(img, rect)
                
    def draw_arrow(self):
        """Draw the fatal arrow with trail effect"""
        if self.arrow_fired and not self.hit:
            # Arrow trail for dramatic effect
            trail_length = 5
            for i in range(trail_length):
                alpha = 255 - (i * 50)
                trail_surface = pygame.Surface((20, 5))
                trail_surface.set_alpha(max(alpha, 0))
                trail_surface.fill(WHITE)
                offset_x = -i * 15
                screen.blit(trail_surface, (self.arrow_pos[0] + offset_x, self.arrow_pos[1]))
            
            # Main arrow
            start = self.arrow_pos
            end = [self.arrow_pos[0] - 25, self.arrow_pos[1]]
            pygame.draw.line(screen, (200, 200, 200), start, end, 3)
            
            # Arrowhead
            pygame.draw.polygon(screen, RED, [
                (end[0], end[1]),
                (end[0] + 15, end[1] - 6),
                (end[0] + 15, end[1] + 6)
            ])
                
    def draw_achilles_heel_marker(self):
        """Mark the vulnerable heel with visual effects"""
        if self.state == "death" and not self.hit:
            heel_x = self.player_x - 15
            heel_y = self.player_y - 30
            
            # Pulsing glow effect
            pulse = abs((pygame.time.get_ticks() % 800) - 400) / 400
            radius = int(12 + pulse * 8)
            
            # Outer glow
            glow_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 50, 50, 80), (radius * 2, radius * 2), radius + 10)
            screen.blit(glow_surface, (heel_x - radius * 2, heel_y - radius * 2))
            
            # Inner circle
            pygame.draw.circle(screen, (255, 100, 100), (heel_x, heel_y), radius, 2)
            
        # Show impact effect when hit
        if self.hit and self.state_timer < 1:
            heel_x = self.player_x - 15
            heel_y = self.player_y - 30
            
            # Expanding circle effect
            impact_radius = int(self.state_timer * 100)
            if impact_radius < 50:
                alpha = int(255 - (self.state_timer * 255))
                impact_surface = pygame.Surface((impact_radius * 4, impact_radius * 4), pygame.SRCALPHA)
                pygame.draw.circle(impact_surface, (255, 0, 0, alpha), 
                                 (impact_radius * 2, impact_radius * 2), impact_radius, 3)
                screen.blit(impact_surface, (heel_x - impact_radius * 2, heel_y - impact_radius * 2))
            
    def draw_fade(self):
        """Draw fade overlay"""
        if self.fade_alpha > 0:
            fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            fade_surface.set_alpha(self.fade_alpha)
            fade_surface.fill(BLACK)
            screen.blit(fade_surface, (0, 0))
            
    def update(self, dt):
        """Update cutscene state"""
        
        # State transitions
        if self.state == "intro":
            self.state_timer += dt
            if self.state_timer > 3:
                self.state = "walking"
                self.state_timer = 0
                self.dialogue_box.set_dialogue([
                    "Achilles: Another victory... yet I feel no satisfaction.",
                    "Achilles: The prophecy lingers in my mind like a shadow.",
                    "Achilles: Shall I live a long, forgotten life... or die young in glory?",
                    "Achilles: I have chosen glory. Let my name echo through eternity!"
                ])
                
        elif self.state == "walking":
            # Move player across screen
            self.player_x += self.walk_speed * dt
            self.state_timer += dt
            
            if self.player_x > WINDOW_WIDTH + 100:
                self.state = "adventures"
                self.state_timer = 0
                self.player_x = 400  # Reset position for adventure scene
                self.dialogue_box.set_dialogue([
                    "NARRATOR: Years pass on the beaches of Troy...",
                    "NARRATOR: Achilles becomes legend - undefeated, unstoppable.",
                    "NARRATOR: But even the mightiest warriors have a weakness...",
                    "NARRATOR: And the gods remember every slight, every act of pride."
                ])
                
        elif self.state == "adventures":
            self.state_timer += dt
            # Show text about adventures
            if self.state_timer > 6:
                self.state = "death"
                self.state_timer = 0
                self.dialogue_box.set_dialogue([
                    "Paris: There! The mighty Achilles walks alone...",
                    "Paris: Apollo guide my arrow to his only weakness!",
                ])
                
        elif self.state == "death":
            self.state_timer += dt
            
            # Animate archer
            if not self.arrow_fired and len(self.animations['archer_attack']) > 0:
                self.archer_frame += self.archer_anim_speed
                if self.archer_frame >= len(self.animations['archer_attack']):
                    self.archer_frame = len(self.animations['archer_attack']) - 1
            
            # Fire arrow at specific time (when archer animation completes)
            if self.state_timer > 3 and not self.arrow_fired and self.archer_frame >= len(self.animations['archer_attack']) - 1:
                self.arrow_fired = True
                self.arrow_pos = [self.archer_x - 50, self.archer_y - 80]
                self.arrow_target = [self.player_x - 15, self.player_y - 30]
                
            # Move arrow toward heel with dramatic slowdown near impact
            if self.arrow_fired and not self.hit:
                dx = self.arrow_target[0] - self.arrow_pos[0]
                dy = self.arrow_target[1] - self.arrow_pos[1]
                dist = (dx**2 + dy**2) ** 0.5
                
                if dist > 5:
                    # Slow down as it approaches (dramatic effect)
                    speed_mult = min(1.0, dist / 200)
                    speed = self.arrow_speed * dt * speed_mult
                    self.arrow_pos[0] += (dx / dist) * speed
                    self.arrow_pos[1] += (dy / dist) * speed
                else:
                    self.hit = True
                    self.arrow_fired = False
                    self.player_falling = True
                    self.state_timer = 0  # Reset for hit animation
                    self.dialogue_box.set_dialogue([
                        "Achilles: Ahh... the heel... my mother's folly...",
                        "Achilles: So this is fate... I regret nothing!",
                        "NARRATOR: Thus fell the greatest warrior of Greece.",
                        "NARRATOR: His name would echo through the ages... immortal."
                    ])
                    
            # Player falling animation
            if self.player_falling and self.fall_rotation > -90:
                self.fall_rotation -= dt * 100
                self.player_y += dt * 50
                    
            # Start fade after dialogue finishes
            if self.hit and not self.dialogue_box.showing:
                self.fade_alpha += dt * 60
                if self.fade_alpha >= 255:
                    self.fade_alpha = 255
                    
        # Update animation frame
        if self.state in ["walking", "adventures"] or (self.state == "death" and not self.player_falling):
            self.frame_index += dt / self.animation_speed
            if self.frame_index >= len(self.animations['side_walk']):
                self.frame_index = 0
                
        # Update dialogue
        self.dialogue_box.update(dt)
        
    def run(self):
        """Main cutscene loop"""
        while self.running:
            dt = self.clock.tick(60) / 1000
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.key == pygame.K_SPACE:
                        # Skip to next state
                        if self.state == "walking":
                            self.state = "adventures"
                        elif self.state == "adventures":
                            self.state = "death"
                        elif self.state == "death" and self.hit:
                            self.running = False
                            
            # Update
            self.update(dt)
            
            # Draw
            self.draw_background(self.state)
            
            if self.state in ["walking", "adventures", "death"]:
                self.draw_player(int(self.frame_index), self.player_falling)
                
            if self.state == "death":
                self.draw_archer()
                self.draw_arrow()
                self.draw_achilles_heel_marker()
                
            # Draw dialogue
            self.dialogue_box.draw(screen)
            
            # Draw title for intro
            if self.state == "intro":
                title = title_font.render("VICTORY!", True, GOLD)
                title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3))
                shadow = title_font.render("VICTORY!", True, BLACK)
                screen.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
                screen.blit(title, title_rect)
                
                subtitle = subtext_font.render("The Boss Has Been Defeated", True, WHITE)
                sub_rect = subtitle.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3 + 50))
                screen.blit(subtitle, sub_rect)
                
            # Draw fade
            self.draw_fade()
            
            # Draw state indicator (for debugging)
            # state_text = subtext_font.render(f"State: {self.state}", True, WHITE)
            # screen.blit(state_text, (10, 10))
            
            pygame.display.flip()
            
        pygame.quit()

if __name__ == "__main__":
    cutscene = EndingCutscene()
    cutscene.run()