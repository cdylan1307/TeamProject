import pygame

### Import Modules Created By Us
from Player import * ### Contains Player class And All Player Animations
from Enemy import *
from Constants import *
######

### Initialisation ###
pygame.init()
######

### Variables ###
running = True
clock = pygame.time.Clock()
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
enemy = []
######

### Functions ###
def collisions(dt):
    collision_sprites = pygame.sprite.spritecollide(player, enemy, True, pygame.sprite.collide_mask)
    if collision_sprites:
        player.flash()

    for enemy in enemy_sprites:
        collided_sprites_enemy = pygame.sprite.spritecollide(enemy, player, True, pygame.sprite.collide_mask)
        if collided_sprites_enemy and enemy.health == 0:
            # Enemy_Animation(enemy_death_frames, enemy.rect, all_sprites)
            enemy.kill()



### Running Loop ###
while running:
    # Delta-Time
    dt = clock.tick() / 1000
    ###

    # Event Loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        recent_keys = pygame. key.get_just_pressed()
        if recent_keys[pygame.K_p ]:
            for enemies in enemy:
                enemies.kill()
                enemy.remove(enemies)
    ###

    while (len(enemy) < 2):
        enemy.append(Enemy((enemy_sprites, all_sprites)))
    ###
    # Update
    all_sprites.update(dt)

    # Draw
    display_surface.fill('darkgray')
    all_sprites.draw(display_surface)
    pygame.display.update()
    ###

pygame.quit()

