import pygame
from os.path import join as path_join

from entity import Entity


class Door(Entity):
    CLOSED_IMAGE_FILENAME = path_join('images', 'closed_door.png')
    OPEN_IMAGE_FILENAME = path_join('images', 'open_door.png')

    def __init__(self, *args, **kwargs):
        sprite = pygame.image.load(Door.CLOSED_IMAGE_FILENAME).convert_alpha()
        super(Door, self).__init__(self, args[1], sprite, **kwargs)
        self.open_door = pygame.image.load(Door.OPEN_IMAGE_FILENAME).convert_alpha()
        self.keep_open = False

    def render(self, surface):
        old_image = self.get_image()
        if self.keep_open:
            self.set_image(self.open_door)
        super(Door, self).render(surface)

        self.keep_open = False
        self.set_image(old_image)
        self.set_passable(False)

    def open(self):
        self.keep_open = True
        self.set_passable(True)
