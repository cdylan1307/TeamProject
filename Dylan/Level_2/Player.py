import pygame
from os.path import join
from Constants import *


###    Classes   ###
### Player Class ###
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)

        self.group      = groups
        self.image      = pygame.image.load(join("TeamProject","images", "player.png"))
        self.rect       = self.image.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.mask       = pygame.mask.from_surface(self.image)
        self.direction  = pygame.Vector2()
        self.speed      = 300
        self.health     = 3
        self.damage     = INITIAL_DAMAGE
    
    def update(self, dt):
        self.movement(dt)
 
    def movement(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = (int(keys[pygame.K_RIGHT]) or int(keys[pygame.K_d])) - (int(keys[pygame.K_LEFT] or int(keys[pygame.K_a])))
        self.direction.y = (int(keys[pygame.K_DOWN]) or int(keys[pygame.K_s])) - (int(keys[pygame.K_UP] or int(keys[pygame.K_w])))
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt
    
    def attack(self, dt):
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE]:
            Player_Animation(player_attack_frames)
            pass
    
    def damage(self):
        self.health -= 1
        if (self.health <= 0):
            Player_Animation(player_death_frames, self.rect.midtop, self.group)
            self.kill()
        
    def flash(self):
        pass

### Animation Class ###
class Player_Animation(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH/ 2, WINDOW_HEIGHT/ 2))

    def update(self, dt):
        self.frame_index += 20 * dt
        if ( self.frame_index < len(self.frames) ):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

player = Player(all_sprites)