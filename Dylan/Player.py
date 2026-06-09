import pygame
from os.path import join
import Main

###    Classes   ###
### Player Class ###
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)

#        self.image = pygame.image.load(join("images", "player.png")).convert_alpha()
        self.rect = self.image.get_frect(center = (Main.WINDOW_WIDTH / 2, Main.WINDOW_HEIGHT / 2))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2()
        self.speed = 300
        self.health = 3
    
    def update(self, dt):
        self.movement(dt)

    def movement(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt
    
    def attack(self, dt):
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE]:
            pass
    
    def damage(self):
        self.health -= 1
        if (self.health <= 0):
            Animation(player_death_frames, self.rect.midtop, Main.all_sprites)
            self.kill()

### Animation Class ###
class Animation(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)

    def update(self, dt):
        self.frame_index += 20 * dt
        if ( self.frame_index < len(self.frames) ):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

### Animation Variables ###
    # Player Death Animation #
player_death_frames = []
for i in range(21):
#    player_death_frames.append(pygame.image.load(join(f"explosion\{i}.png")).convert_alpha())
    pass
    ###

    # Player Idle Animation #
player_idle_frames = []
for i in range(21):
#    player_idle_frames.append(pygame.image.load(join(f"explosion\{i}.png")).convert_alpha())
    pass
    ###

    # Player Moving Animation #
player_move_frames = []
for i in range(21):
#    player_move_frames.append(pygame.image.load(join(f"explosion\{i}.png")).convert_alpha())
    pass
    ###