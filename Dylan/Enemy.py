import pygame
from os.path import join
from random import randint
from Constants import *
pygame.init()

###   Classes   ###
### Enemy Class ###
class Enemy(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)

        self.group       = groups
        self.image       = pygame.image.load(join("TeamProject","animations","Chiron","Walking","Chiron_Walk_0.png")).convert_alpha()
        self.rect        = self.image.get_frect(center = ((WINDOW_WIDTH + 10), randint(0, WINDOW_HEIGHT)))
        self.mask        = pygame.mask.from_surface(self.image)
        self.direction   = pygame.Vector2()
        self.speed       = 300
        self.frames      = chiron_walk_frames
        self.frame_index = 0
        

    def update(self, dt):
        self.frame_index += 20 * dt
        if ( self.frame_index < len(self.frames) ):
            self.image = self.frames[int(self.frame_index)]
        self.rect= self.image.get_frect(center = ((WINDOW_WIDTH -10), randint(0, WINDOW_HEIGHT)))
    
### Animation Class ###
class Enemy_Animation(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH/ 2, WINDOW_HEIGHT/ 2))
        
            