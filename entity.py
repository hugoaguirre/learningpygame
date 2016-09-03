from vector import Vector
import pygame
from statemachine import StateMachine


BLACK = (0, 0, 0)
SARA_IMG_FILENAME = 'images/sara.png'
LASER_IMG_FILENAME = "images/laser.png"
SCREEN_SIZE = (800, 600)


class Entity(pygame.sprite.Sprite):

    def __init__(self, world, name, image=None, spritesheet=None):
        super(Entity, self).__init__()
        self.world = world
        self.name = name
        if not image:
            self.spritesheet = spritesheet
            image = spritesheet.get_image(0)
        self.image = image
        self.rect = image.get_rect()
        self.location = Vector(0, 0)
        self.destination = None
        self.speed = 0.0

        self.brain = StateMachine()

        self.id = 0

    def set_location(self, x, y):
        self.location = Vector(x, y)
        self.rect.x = x
        self.rect.y = y

    def render(self, surface):
        x = self.location.x
        y = self.location.y
        surface.blit(self.image, (x, y))

    def process(self, time_passed):
        self.brain.think()
        self.move(time_passed)

    def move(self, time_passed):
        if self.speed > 0 and self.location != self.destination:
            vec_to_destination = self.destination - self.location
            distance_to_destination = vec_to_destination.get_magnitude()
            vec_to_destination.normalize()
            travel_distance = min(distance_to_destination, time_passed * self.speed)
            vec_to_destination.x *= travel_distance
            vec_to_destination.y *= travel_distance
            self.set_location(self.location.x + vec_to_destination.x,
                              self.location.y + vec_to_destination.y)
            return True
        return False


    def keep_inside_screen(self):
        if self.destination.x < 0:
            self.destination.x = 0
        elif self.destination.x > SCREEN_SIZE[0] - self.image.get_width():
            self.destination.x = SCREEN_SIZE[0] - self.image.get_width()

        if self.destination.y < 0:
            self.destination.y = 0
        elif self.destination.y > SCREEN_SIZE[1] - self.image.get_height():
            self.destination.y = SCREEN_SIZE[1] - self.image.get_height()
