import pygame
from os.path import join
from random import randint
from Constants import *
from Player import *
pygame.init()

###
scale = 0.75

###   Classes   ###
### Enemy Class ###
class Enemy(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)

        self.group       = groups
        self.image       = pygame.image.load(join("TeamProject","animations","Chiron","Walking","Chiron_Walk_0.png")).convert_alpha()
        self.image       = pygame.transform.scale_by(self.image, scale)
        self.rect        = self.image.get_frect(center = ((WINDOW_WIDTH * 0.8), (WINDOW_HEIGHT / 2)))
        self.mask        = pygame.mask.from_surface(self.image)
        self.direction   = pygame.Vector2()
        self.speed       = 0.3
        self.frames      = chiron_walk_frames
        self.frame_index = 0
        

    def update(self, dt):

        self.frame_index += 10 * dt
        if ( self.frame_index < len(self.frames) ):
            self.image = self.frames[int(self.frame_index)]
            self.image = pygame.transform.scale_by(self.image, scale)
        else:
            self.frame_index = 0
        
        ### https://stackoverflow.com/questions/20044791/how-to-make-an-enemy-follow-the-player-in-pygame
        # Find direction vector (dx, dy) between enemy and player.
        enemy_vector = pygame.math.Vector2(player.rect.x - self.rect.x,
                                      player.rect.y - self.rect.y)
        enemy_vector.normalize() if self.direction else self.direction
        # Move along this normalized vector towards the player at current speed.
        self.rect.center += enemy_vector * self.speed * dt




        
        
        
            