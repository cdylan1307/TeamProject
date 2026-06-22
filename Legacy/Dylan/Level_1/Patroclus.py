import pygame
from os.path import join
from Constants import *
from Player import *

class Patroclus(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)

        self.group      = groups
        self.image      = pygame.image.load(join("images", "player.png"))
        self.rect       = self.image.get_frect(center = (WINDOW_WIDTH / 2 - 20, WINDOW_HEIGHT / 2 + 20))
        self.mask       = pygame.mask.from_surface(self.image)
        self.direction  = pygame.Vector2()
        self.speed      = 3

    def update(self, dt):
        enemy_vector = pygame.math.Vector2((player.rect.x -40) - self.rect.x,
                                      (player.rect.y + 40) - self.rect.y)
        enemy_vector.normalize() if self.direction else self.direction
        # Move along this normalized vector towards the player at current speed.
        self.rect.center += enemy_vector * self.speed * dt

patroclus = Patroclus(all_sprites)