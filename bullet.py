import pygame
from os.path import join as path_join

from vector import Vector
from entity import Entity
from constants import  COLOR_BLACK


class Bullet(Entity):
    """ Make the bullets independant"""

    SPEED = 500
    IMAGE_FILENAME = path_join('assets', "images", "laser.png")

    def __init__(self, world, flip=False, location=None, direction=None):
        sprite = pygame.image.load(Bullet.IMAGE_FILENAME).convert()
        sprite.set_colorkey(COLOR_BLACK)
        super(Bullet, self).__init__(
            world, 'Bullet', sprite,
            flip=flip,
            speed=Bullet.SPEED,
            location=location
        )
        self.direction = direction

    def process(self, time_passed):
        if not self.get_destination():
            x, y = self.get_location().x, self.get_location().y
            if self.direction == 'up':
                y = 0 - self.get_height()
            elif self.direction == 'down':
                y = self.world.get_world_limits()[1] + self.get_height()
            elif self.direction == 'left':
                x = 0 - self.get_width()
            elif self.direction == 'right':
                x = self.world.get_world_limits()[0] + self.get_width()
            self.set_destination(Vector(x, y))
        super(Bullet, self).process(time_passed)
