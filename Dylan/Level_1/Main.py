import pygame

### Import Modules Created By Us
from Player import * ### Contains Player class And All Player Animations
from Chiron import *
from Constants import *
######

### Initialisation ###
pygame.init()
######

### Variables ###
running = True
clock = pygame.time.Clock()
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
background = pygame.image.load("TeamProject\images\lv1background.png")
background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
enemy = []
start = True
border = pygame.Rect(325, 169, 880, 723)
######

### Functions ###
def collisions(dt):
    collision_sprites = pygame.sprite.spritecollide(player, enemy_sprites, False, pygame.sprite.collide_mask)
    if collision_sprites:
        player.flash()


    # collided_sprites_enemy = pygame.sprite.spritecollide(enemy, player, True, pygame.sprite.collide_mask)
    # if collided_sprites_enemy and enemy.health == 0:
    #     # Enemy_Animation(enemy_death_frames, enemy.rect, all_sprites)
    #     enemy.kill()

### Chiron ###
enemy = Enemy((all_sprites, enemy_sprites))

### Running Loop ###
while running:
    recent_keys = pygame.key.get_just_pressed()
    if recent_keys[pygame.K_SPACE ] :
        start = True
    if start:
        # Delta-Time
        dt = clock.tick() / 1000
        ###

        # Event Loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            recent_keys = pygame. key.get_just_pressed()
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

pygame.quit()

