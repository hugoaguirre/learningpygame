import pygame

from vector import Vector
from constants import SCREEN_SIZE


class Entity(pygame.sprite.Sprite):

    def __init__(self, world, name,
                 image=None,
                 rect=None,
                 spritesheet=None,
                 flip=False,
                 passable=True,
                 can_leave_screen=True,
                 brain=None,
                 location=None,
                 destination=None,
                 speed=0):
        super(Entity, self).__init__()
        self.world = world
        self.name = name
        if not image and spritesheet:
            self.spritesheet = spritesheet
            image = spritesheet.get_image(0)

        if not location:
            location = Vector(0, 0)
        self._location = location
        self._destination = destination
        self._passable = passable
        self._can_leave_screen = can_leave_screen
        self._brain = brain

        self._speed = speed

        # Needed by pygame
        if image:
            self.rect = image.get_rect()
        else:
            self.rect = rect

        self._image = None
        self._is_flip = flip
        self._flash = None
        if image:
            self.set_image(image)

        self.id = 0

        # Internal state
        self._has_collide = None

    def is_passable(self):
        return self._passable

    def set_passable(self, passable):
        self._passable = passable

    def can_leave_screen(self):
        return self._can_leave_screen

    def set_can_leave_screen(self, can_leave_screen):
        self._can_leave_screen = can_leave_screen

    def is_flip(self):
        return self._is_flip

    def get_width(self):
        return self._image.get_width()

    def get_height(self):
        return self._image.get_height()

    def set_image(self, image):
        self._image = image
        if self._is_flip:
            self._is_flip = False  # Force flip
            self.flip()
        self.mask = pygame.mask.from_surface(self._image)

    def get_image(self):
        return self._image

    def flip(self):
        if not self._is_flip:
            self._is_flip = True
            self._image = pygame.transform.flip(self._image, True, False)
            self.mask = pygame.mask.from_surface(self._image)

    def reverse_flip(self):
        if self._is_flip:
            self._is_flip = False
            self._image = pygame.transform.flip(self._image, True, False)
            self.mask = pygame.mask.from_surface(self._image)

    def set_location(self, vector):
        self._location = vector
        self.rect.x = vector.x
        self.rect.y = vector.y

    def get_location(self):
        return self._location

    def set_destination(self, vector):
        self._destination = vector
        self.rect.x = vector.x
        self.rect.y = vector.y

    def get_destination(self):
        return self._destination

    def set_speed(self, speed):
        self._speed = speed

    def get_speed(self):
        return self._speed

    def flash(self):
        o = self.mask.outline()
        s = pygame.Surface((self.get_width(), self.get_height()))
        s.set_colorkey((0, 0, 0))
        pygame.draw.polygon(s, (200, 150, 150), o, 0)
        self._flash = s
        self._flash_duration = 5

    def render(self, surface):
        if not self._image:
            return
        x = self._location.x
        y = self._location.y

        if not self._flash:
            surface.blit(self._image, (x, y))
        else:
            surface.blit(self._flash, (x, y))
            self._flash_duration -= 1
            if self._flash_duration == 0:
                self._flash = None
                o = self.mask.outline()

        # o = self.mask.outline()
        # s = pygame.Surface((self.get_width(), self.get_height()))
        # s.set_colorkey((0,0,0))
        # pygame.draw.lines(s,(200,150,150),1,o)
        # surface.blit(s, (x, y))

    def process(self, time_passed):
        if self._brain:
            self._brain.think(time_passed)
        self.move(time_passed)

    def move(self, time_passed):
        self._has_collide = None
        if self.get_speed() > 0 and self._location != self._destination:
            if not self.can_leave_screen():
                self.keep_inside_screen()
            if not self.is_passable():
                old_location = self._location

            vec_to_destination = self._destination - self._location
            distance_to_destination = vec_to_destination.get_magnitude()
            vec_to_destination.normalize()
            travel_distance = min(distance_to_destination, time_passed * self.get_speed())
            vec_to_destination.x *= travel_distance
            vec_to_destination.y *= travel_distance
            self.set_location(self._location + vec_to_destination)

            # cancel movement
            if not self.is_passable() and self.is_colliding_with_impassable_entities():
                self._has_collide = self._destination
                # because movement is interrupted can be defined as a float, which may lead to troubles
                self.set_location(old_location)
                self.set_destination(self.get_location())
            return True
        # Known issue: if there is a collition between impassable entities when they are not moving
        # e.g. during first render, they won't be able to cancel any movement and they will stay blocked

        return False

    def keep_inside_screen(self):
        if self._destination.x < 0:
            self._destination.x = 0
        elif self._destination.x > SCREEN_SIZE[0] - self._image.get_width():
            self._destination.x = SCREEN_SIZE[0] - self._image.get_width()

        if self._destination.y < 0:
            self._destination.y = 0
        elif self._destination.y > SCREEN_SIZE[1] - self._image.get_height():
            self._destination.y = SCREEN_SIZE[1] - self._image.get_height()

    def is_colliding_with_impassable_entities(self):
        entities = self.world.get_impassable_entities(but_me=self)
        entities_with_image = [entity for entity in entities if entity._image]
        entities_rect = [entity for entity in entities if entity._image is None]
        col_mask = pygame.sprite.spritecollideany(self, entities_with_image, pygame.sprite.collide_mask)
        col_rect = pygame.sprite.spritecollideany(self, entities_rect, pygame.sprite.collide_rect)
        return col_mask or col_rect

    def get_middle(self):
        x = self._location.x + self.get_width() / 2
        y = self._location.y + self.get_height() / 2
        return (x, y)
