import pygame
from os.path import join
pygame.init()

### Constants ###
WINDOW_WIDTH   = 1500
WINDOW_HEIGHT  = 1000

### Weapon Damage ###
INITIAL_DAMAGE = 3
SWORD_DAMAGE = 100
SPEAR_DAMAGE = 100
######

### Groups ###
all_sprites = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()
######

### Animation Frames ###

# Player

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
    # Player Attack Animations
player_attack_frames = []
for i in range(21):
#    player_death_frames.append(pygame.image.load(join(f"explosion\{i}.png")).convert_alpha())
    pass
    ###

# Enemy
### Animation Variables ###
    # Player Death Animation #
enemy_death_frames = []
for i in range(21):
#    player_death_frames.append(pygame.image.load(join(f"explosion\{i}.png")).convert_alpha())
    pass
    ###

    # Player Idle Animation #
enemy_idle_frames = []
for i in range(21):
#    player_idle_frames.append(pygame.image.load(join(f"explosion\{i}.png")).convert_alpha())
    pass
    ###

    # Player Moving Animation #
enemy_move_frames = []
for i in range(21):
#    player_move_frames.append(pygame.image.load(join(f"explosion\{i}.png")).convert_alpha())
    pass
    ###
    # Player Attack Animations
enemy_attack_frames = []
for i in range(21):
#    player_death_frames.append(pygame.image.load(join(f"explosion\{i}.png")).convert_alpha())
    pass
    ###


### Chrion Animations
# Player Death Animation #
enemy_death_frames = []
for i in range(21):
#    player_death_frames.append(pygame.image.load(join(f"explosion\{i}.png")).convert_alpha())
    pass
    ###

    # Player Idle Animation #
enemy_idle_frames = []
for i in range(21):
#    player_idle_frames.append(pygame.image.load(join(f"explosion\{i}.png")).convert_alpha())
    pass
    ###

    # Player Moving Animation #
chiron_walk_frames = []
for i in range(6):
    chiron_walk_frames.append(pygame.image.load(join("animations","Chiron","Walking",f"Chiron_Walk_{i}.png")))
    # Player Attack Animations
enemy_attack_frames = []
for i in range(21):
#    player_death_frames.append(pygame.image.load(join(f"explosion\{i}.png")).convert_alpha())
    pass
    ###