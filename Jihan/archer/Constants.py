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