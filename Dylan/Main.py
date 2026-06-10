import pygame

### Import Modules Created By Us
from Player import ( ### Contains Player class And All Player Animations
    Player,
    Player_Animation
                   )

from Constants import (
    WINDOW_WIDTH, 
    WINDOW_HEIGHT
                 )
######

### Initialisation ###
pygame.init()
######

### Variables ###
running = True
clock = pygame.time.Clock()
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
######

### Groups ###
all_sprites = pygame.sprite.Group()
######


player = Player(all_sprites)

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

    # Update
    all_sprites.update(dt)

    # Draw
    display_surface.fill('darkgray')
    all_sprites.draw(display_surface)
    pygame.display.update()
    ###

pygame.quit()