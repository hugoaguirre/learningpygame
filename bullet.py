import pygame

from vector import Vector
from entity import Entity

# TODO: Create game_settings.py file
BLACK = (0, 0, 0)
LASER_IMG_FILENAME = "images/laser.png"
SCREEN_SIZE = (800, 600)

class Bullet(Entity):
    """ Make the bullets independant 
        Make the bullets great again """

    def __init__(self, world, flip=False):

        sprite = pygame.image.load(LASER_IMG_FILENAME).convert()
        sprite.set_colorkey(BLACK)
        super(Bullet, self).__init__(world, 'bulllet', sprite, flip=flip)

        # Bullet settings
        self.speed = 300

    def process(self, time_passed):
        if not self.destination:
            x = 0 - self.get_width() if self.is_flip() else SCREEN_SIZE[0] + self.get_width()
            self.destination = Vector(x, self.location.y)
        super(Bullet, self).process(time_passed)
