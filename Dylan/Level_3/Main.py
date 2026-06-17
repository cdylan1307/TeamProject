import pygame

### Import Modules Created By Us
from Player import * ### Contains Player class And All Player Animations
from Hector import *
from Constants import *
######

### Initialisation ###
pygame.init()
######

### Variables ###
running = True
clock = pygame.time.Clock()
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
background = pygame.image.load("images\lv1background.png")
background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
enemy = []
start = False
border = pygame.Rect(325, 169, 880, 723)
win = False
######

### Functions ###
def collisions(dt):
    collision_sprites = pygame.sprite.spritecollide(player, enemy_sprites, False, pygame.sprite.collide_mask)
    if collision_sprites:
        player.flash()

    collided_sprites_enemy = pygame.sprite.spritecollide(player, enemy_sprites, False, pygame.sprite.collide_mask)
    if collided_sprites_enemy  and recent_keys[pygame.K_SPACE]:
        enemy.health -= 1

    if collided_sprites_enemy and enemy.health == 0:
        global win
        win = True
        enemy.kill()

### Chiron ###
enemy = Hector((all_sprites, enemy_sprites), 0)


### Running Loop ###
while running:
    # Event Loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.QUIT

    if not win:
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_1]:
            start = True
                ###

        if start:
            enemy.speed = 0.3
            # Delta-Time
            dt = clock.tick() / 1000
            ###

            
            

            # Update
            all_sprites.update(dt)
            collisions(dt)

            # Draw
            display_surface.blit(background)
            all_sprites.draw(display_surface)
            pygame.display.update()
            ###

            # Border
            player.rect.clamp_ip(border)
            enemy.rect.clamp_ip(border)
            ###

    ### win cutscene
    while win:

            player.kill()
            font = pygame.font.Font("text/Oxanium-Bold.ttf")
            display_surface.blit(font.render('You Win!', True, (0,0,0))), (WINDOW_WIDTH /2, WINDOW_HEIGHT /2)
            pygame.display.update()
        
           



pygame.quit()

