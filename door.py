import pygame
from os.path import join as path_join

from entity import Entity
from constants import DISPLAY_MESSAGE_EVENT


class Door(Entity):
    CLOSED_IMAGE_FILENAME = path_join('assets', 'images', 'closed_door.png')
    OPEN_IMAGE_FILENAME = path_join('assets', 'images', 'open_door.png')

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

    def open(self, keys):
        if self.props.get('key', None) is None or self.props['key'] in keys:
            self.keep_open = True
            self.set_passable(True)
            message = self.props.get('message', None)
        else:
            message = self.props.get('locked_message', None)

        if message:
            event = pygame.event.Event(
                DISPLAY_MESSAGE_EVENT, {
                    'message': message
                }
            )
            pygame.event.post(event)
