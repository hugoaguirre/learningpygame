import pygame
from vector import Vector
from entity import Entity
from spritesheet import Spritesheet


BLACK = (0, 0, 0)
SARA_IMG_FILENAME = 'images/sara.png'
LASER_IMG_FILENAME = "images/laser.png"
SCREEN_SIZE = (800, 600)


class Sara(Entity):

    ANIMATION_TICKS = 12

    def __init__(self, world):
        ss = Spritesheet(SARA_IMG_FILENAME, 44)
        super(Sara, self).__init__(world, 'sara', spritesheet=ss)
        self.speed = 200
        self.animation = 0
        self.animation_time = 0

    def process_events(self, events):
        pressed_keys = pygame.key.get_pressed()
        direction = Vector(0, 0)
        if pressed_keys[pygame.K_LEFT]:
            direction.x = -1
        elif pressed_keys[pygame.K_RIGHT]:
            direction.x = +1

        if pressed_keys[pygame.K_UP]:
            direction.y = -1
        elif pressed_keys[pygame.K_DOWN]:
            direction.y = +1
        direction.normalize()

        self.destination = self.location + Vector(
            direction.x * self.speed,
            direction.y * self.speed)

        self.keep_inside_screen()

        for event in events:
            if (event.type == pygame.KEYDOWN and
                event.key == pygame.K_SPACE):
                self.fire()

    def fire(self):
        # TODO if sara is moving and fires, laser appears in a previous location
        x = self.location.x + 40
        y = self.location.y + 36
        shot = Shot(self.world)
        shot.set_location(x, y)
        self.world.add_entity(shot, ('ally_shots', ))

    def move(self, time_passed):
        is_moving = super(Sara, self).move(time_passed)
        if is_moving:
            # here it was a case where no moving loop finish with
            # self.animation_time equals to zero, and not valid
            # sprites were being requested
            if self.animation in (0, 4):
                self.animation = 1
            if self.animation_time == 0:
                self.animation += -2 if self.animation == 3 else 1
                self.image = self.spritesheet.get_image(self.animation)
                self.animation_time = self.ANIMATION_TICKS
            else:
                self.animation_time -= 1
        else:
            if self.animation in (1, 2, 3): # was just moving
                self.animation_time = self.ANIMATION_TICKS / 2  # shorter stop animation
                self.animation = 4
            elif self.animation == 4 and self.animation_time != 0:
                self.animation_time -= 1
            else:
                self.animation = 0
        self.image = self.spritesheet.get_image(self.animation)

class Shot(Entity):
    def __init__(self, world):
        sprite = pygame.image.load(LASER_IMG_FILENAME).convert()
        sprite.set_colorkey(BLACK)
        super(Shot, self).__init__(world, 'shot', sprite)
        self.speed = 600

    def process(self, time_passed):
        if not self.destination:
            self.destination = Vector(
                SCREEN_SIZE[0] + self.image.get_width(),
                self.location.y
            )
        super(Shot, self).process(time_passed)
