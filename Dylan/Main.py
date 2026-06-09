import pygame
from os.path import join

### Import Modules Created By Us
import Player ### Contains Player class And All Player Animations
######

### Initialisation ###
pygame.init()
######

# Where Constants Are Used In Other Files 
# They Must Import Main(This File) and take the form
# {file_name}.{constant_name} e.g. Main.WINDOW_HEIGHT
### Constants ###
WINDOW_WIDTH   = 1500
WINDOW_HEIGHT  = 1000
######

### Variables ###
running = True
clock = pygame.time.Clock()
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
######

### Groups ###
all_sprites = pygame.sprite.Group()
######

### Running Loop ###
while running:
    # Delta-Time
    dt = clock.tick() / 1000
    ###

    # Event Loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    ###

    # Draw
    display_surface.fill('darkgray')
    pygame.display.update()
    ###

pygame.quit()