import pygame
from pygame import *
from pygame.locals import *
import random


game_width = 900
game_height = 500

images = {}
def load_image(name, filename, flip_x = False):
    images[name] = pygame.image.load(filename).convert_alpha()

    # flip image on the x-axis
    if flip_x:
        images[name] = pygame.transform.flip(images[name], True, False)

load_image('shadow', 'images/shadow_enemy.png')

#################SOUNDS#####################













##############ENEMY#CLASS###################
class enemy(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.x += random.randint(0, 85) * 10
        self.y += random.randint(0, 20) * 10

        # keep track of whether this enemy has been hit or not
        self.is_hit = False

    def draw(self):
        # draw the enemy if it hasn't been hit yet
        if self.is_hit == False:
            game_window.blit(self.image, (self.x, self.y))

################ENEMIES#######################
class Shadow(enemy):

    def __init__(self, x):
        super().__init__(x, game_height - 450)
        self.points = random.choice([1, 2])
        self.special_points = 1
        self.image = images['shadow']

    def update(self):
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y