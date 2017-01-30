import pygame
from os.path import join as path_join

from vector import Vector
from entity import Entity
from constants import  COLOR_BLACK


class Bullet(Entity):
    """ Make the bullets independant"""

    SPEED = 300
    IMAGE_FILENAME = path_join("images", "laser.png")

    def __init__(self, world, flip=False, location=None):
        sprite = pygame.image.load(Bullet.IMAGE_FILENAME).convert()
        sprite.set_colorkey(COLOR_BLACK)

        super(Bullet, self).__init__(
            world, 'Bullet', sprite,
            flip=flip,
            speed=Bullet.SPEED,
            location=location
        )

    def process(self, time_passed):
        if not self.get_destination():
            x = 0 - self.get_width() if self.is_flip() else self.world.get_world_limits()[0] + self.get_width()
            self.set_destination(Vector(x, self.get_location().y))
        super(Bullet, self).process(time_passed)
