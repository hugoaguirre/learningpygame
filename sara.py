import pygame
from os.path import join as path_join

from vector import Vector
from entity import Entity
from spritesheet import Spritesheet
from weapon import Weapon
from constants import NEED_RELOAD_EVENT, RELOAD_EVENT


class Sara(Entity):

    SPEED = 200
    ANIMATION_TICKS = 12
    IMAGE_FILENAME = path_join('images', 'sara.png')

    def __init__(self, world):
        ss = Spritesheet(Sara.IMAGE_FILENAME, 44)
        super(Sara, self).__init__(
            world, 'sara',
            spritesheet=ss,
            passable=False,
            can_leave_screen=True,
            speed=Sara.SPEED
        )

        self.animation = 0
        self.animation_time = 0
        self.moving = False

        # Weapon init
        self.weapon = Weapon(self, world)

        self.life = 3
        self.auto = False

    def process(self, time_passed):
        self.open_doors()
        self.activate_triggers()
        super(Sara, self).process(time_passed)

    def open_doors(self):
        for door in self.world.get_close_entities('doors', self.get_location()):
            door.open()

    def activate_triggers(self):
        for trigger in self.world.get_close_entities('triggers', self.get_location(), 50):
            if trigger.props['action'] == 'move_camera':
                trigger.props['action'] = None
                self.world.viewport.lock()
                self.world.viewport.move_to(
                    Vector(int(trigger.props['move_camera_x']),
                           int(trigger.props['move_camera_y'])),
                    on_arrival=lambda: (trigger.set_passable(False), self.set_auto(False))
                )
                self.auto_move(self.get_location() - Vector(128, 0))

    def set_auto(self, auto):
        self.auto = auto

    def process_events(self, events):
        if self.auto:
            return

        pressed_keys = pygame.key.get_pressed()
        direction = Vector(0, 0)
        if pressed_keys[pygame.K_LEFT]:
            direction.x = -1
            self.flip()
        elif pressed_keys[pygame.K_RIGHT]:
            direction.x = +1
            self.reverse_flip()

        if pressed_keys[pygame.K_UP]:
            direction.y = -1
        elif pressed_keys[pygame.K_DOWN]:
            direction.y = +1

        if pressed_keys[pygame.K_r]:
            self.weapon.reload()
            event = pygame.event.Event(RELOAD_EVENT)
            pygame.event.post(event)

        direction.normalize()

        self.set_destination(self.get_location() + Vector(
            direction.x * self.get_speed(),
            direction.y * self.get_speed()))

        for event in events:
            if (event.type == pygame.KEYDOWN and
                event.key == pygame.K_SPACE):
                self.fire()

    def fire(self):
        if not self.weapon.fire():
            event = pygame.event.Event(NEED_RELOAD_EVENT)
            pygame.event.post(event)

    def auto_move(self, destination):
        self.auto = True
        self.set_destination(destination)

    def receive_hit(self):
        '''Perform actions when player receive hit, return boolean
        indicating if entity should die'''

        self.life -= 1
        self.flash()
        return self.life == 0

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
                self.animation_time = self.ANIMATION_TICKS
            else:
                self.animation_time -= 1
        else:
            if self.animation in (1, 2, 3):  # was just moving
                self.animation_time = self.ANIMATION_TICKS / 2  # shorter stop animation
                self.animation = 4
            elif self.animation == 4 and self.animation_time != 0:
                self.animation_time -= 1
            else:
                self.animation = 0
        self.set_image(self.spritesheet.get_image(self.animation))
