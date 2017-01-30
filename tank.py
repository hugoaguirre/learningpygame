import pyganim
import pygame

from entity import Entity
from vector import Vector
from statemachine import StateMachine, State
from random import randint
from constants import SCREEN_SIZE


class Tank(Entity):
    SCORE = 1000
    SPEED = 300

    def __init__(self,*args, **kwargs):
        images = pyganim.getImagesFromSpriteSheet('images/tank.png', rows=1, cols=4, rects=[])
        frames = list(zip(images[:3], [200, 200, 200]))
        self.animObj = pyganim.PygAnimation(frames)
        self.animObj.play()

        kwargs['image'] = frames[0][0]
        kwargs['life'] = 20
        kwargs['speed'] = Tank.SPEED
        super(Tank, self).__init__(*args, **kwargs)

    def build_brain(self):
        brain = StateMachine()
        shooting_state = TankStateShooting(self)
        waiting_state = TankStateWaiting(self)
        dodging_state = TankStateDodging(self)

        brain.add_state(shooting_state)
        brain.add_state(waiting_state)
        brain.add_state(dodging_state)

        brain.set_state('waiting')
        self._brain = brain

    def render(self, surface):
        location = self.get_location()

        self.animObj.blit(surface, (location.x, location.y))

    def flip(self):
        if not self._is_flip:
            self._is_flip = True
            self.animObj.flip(True, False)

    def reverse_flip(self):
        if self._is_flip:
            self._is_flip = False
            self.animObj.flip(True, False)

    def shoot_spark(self):
        self.spark = Spark(self.world)
        location = self.get_location()
        self.spark.set_location(location + Vector(63, 106))
        self.world.add_entity(self.spark, ('enemy_shots',))


class TankStateDodging(State):
    def __init__(self, tank):
        super(TankStateDodging, self).__init__('dodging')
        self.tank = tank
        self._last_time_collided = None

    def set_destination(self):
        sara_rect = self.tank.world.get_player().get_rect()
        tank_rect = self.tank.get_rect()
        tank_rect.centery = sara_rect.centery

        self.tank.set_destination(Vector(*tank_rect.topleft))

    def do_actions(self):
        # just move once and then do nothing
        pass

    def check_conditions(self, time_passed):
        if self.tank.get_location() == self.tank.get_destination():
            return 'shooting'
        return None

    def entry_actions(self):
        self.set_destination()


class TankStateShooting(State):
    def __init__(self, tank):
        super(TankStateShooting, self).__init__('shooting')
        self.tank = tank
        self.has_shot = False

    def entry_actions(self):
        self.tank.shoot_spark()

    def check_conditions(self, time_passed):
        if self.tank.spark.shoot:
            return 'waiting'
        return None


class TankStateWaiting(State):
    WAIT = 1  # second

    def __init__(self, tank):
        super(TankStateWaiting, self).__init__('waiting')
        self.tank = tank
        self.time_passed = 0

    def check_conditions(self, time_passed):
        self.time_passed += time_passed
        if self.time_passed > self.WAIT:
            self.time_passed = 0
            return 'dodging'

SPARK_IMAGE_FILENAME = 'images/redspark.png'


class Spark(Entity):

    LOADING_TIME = 0.5

    def __init__(self, world):

        images = pyganim.getImagesFromSpriteSheet(SPARK_IMAGE_FILENAME, rows=1, cols=2, rects=[])
        frames = list(zip(images, [100, 100]))
        self.animObj = pyganim.PygAnimation(frames)
        self.animObj.play()

        sprite = pygame.image.load(SPARK_IMAGE_FILENAME).convert_alpha()
        super(Spark, self).__init__(world, 'spark', sprite)
        self.loading = 0
        self.shoot = False

    def render(self, surface):
        location = self.get_location()

        self.animObj.blit(surface, (location.x, location.y))

    def flip(self):
        if not self._is_flip:
            self._is_flip = True
            self.animObj.flip(True, False)

    def reverse_flip(self):
        if self._is_flip:
            self._is_flip = False
            self.animObj.flip(True, False)

    def process(self, time_passed):
        self.loading += time_passed
        if self.loading > Spark.LOADING_TIME and not self.get_destination():
            self.shoot = True
            self.set_speed(1200)
            x = 0 - self.get_width() if self.is_flip() else SCREEN_SIZE[0] + self.get_width()
            self.set_destination(Vector(
                x,
                self.get_location().y
            ))
        super(Spark, self).process(time_passed)
