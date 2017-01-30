import pygame
import pyganim
from os.path import join as path_join

from entity import Entity
from random import randint
from statemachine import StateMachine, State
from vector import Vector
from sfx import play_laser
from constants import SCREEN_SIZE


class Robot(Entity):
    SPEED = 100
    SCORE = 100
    IMAGE_FILENAME = path_join("images", "robot.png")

    def __init__(self, world, location=(0, 0)):
        # FIX integrate pyganim as part on entity
        images = pyganim.getImagesFromSpriteSheet(path_join('images', 'anirobot.png'), rows=1, cols=3, rects=[])
        frames = list(zip(images, [200, 200, 200]))
        self.animObj = pyganim.PygAnimation(frames)
        self.animObj.play()

        sprite = pygame.image.load(Robot.IMAGE_FILENAME).convert_alpha()

        super(Robot, self).__init__(
            world, 'Robot', sprite,
            passable=False,
            can_leave_screen=False,
            brain=self._build_brain(),
            location=location)

    def _build_brain(self):
        brain = StateMachine()
        shoting_state = RobotStateShoting(self)
        waiting_state = RobotStateWaiting(self)
        dodging_state = RobotStateDodging(self)

        brain.add_state(shoting_state)
        brain.add_state(waiting_state)
        brain.add_state(dodging_state)

        brain.set_state('waiting')
        return brain

    def render(self, surface):
        location = self.get_location()
        self.animObj.blit(surface, (location.x, location.y))

    def shoot(self):
        location = self.get_location()
        laser = Laser(self.world, flip=self.is_flip())
        laser.set_location(location)
        self.world.add_entity(laser, ('enemy_shots', ))
        play_laser()

    def flip(self):
        if not self._is_flip:
            self._is_flip = True
            self.animObj.flip(True, False)

    def reverse_flip(self):
        if self._is_flip:
            self._is_flip = False
            self.animObj.flip(True, False)


class RobotStateDodging(State):
    def __init__(self, robot):
        super(RobotStateDodging, self).__init__('dodging')
        self.robot = robot
        self._last_time_collided = None

    def random_destination(self, but=None):
        location = self.robot.get_location()
        (x, y) = int(location.x), int(location.y)
        range_x = [-200, 200]
        range_y = [-200, 200]

        if but:
            range_x[0 if but[0] < 0 else 1] = 0
            range_y[0 if but[1] < 0 else 1] = 0

        self.robot.set_destination(Vector(
            randint(x + range_x[0], x + range_x[1]),
            randint(y + range_y[0], y + range_y[1])
        ))

    def do_actions(self):
        # just move once and then do nothing
        pass

    def check_conditions(self, time_passed):
        robot_location = self.robot.get_location()
        if self.robot._has_collide:
            collision = self.robot._has_collide - robot_location
            self._last_time_collided = collision.get_direction()

        sara = self.robot.world.get_player()

        sara_location = sara.get_location()
        if sara_location.x < robot_location.x:
            self.robot.flip()
        else:
            self.robot.reverse_flip()

        robot_destination = self.robot.get_destination()
        if (robot_location.x == float(robot_destination.x) and
            robot_location.y == float(robot_destination.y)):
            return 'shoting'
        return None

    def entry_actions(self):
        self.robot.set_speed(Robot.SPEED + randint(-20, 20))
        self.random_destination(but=self._last_time_collided)
        self._last_time_collided = None


class RobotStateShoting(State):
    def __init__(self, robot):
        super(RobotStateShoting, self).__init__('shoting')
        self.robot = robot
        self.has_shot = False

    def do_actions(self):
        self.robot.shoot()
        self.has_shot = True

    def check_conditions(self, time_passed):
        if self.has_shot:
            return 'waiting'
        return None


class RobotStateWaiting(State):
    WAIT = 1  # second

    def __init__(self, robot):
        super(RobotStateWaiting, self).__init__('waiting')
        self.robot = robot
        self.time_passed = 0

    def check_conditions(self, time_passed):
        self.time_passed += time_passed
        if self.time_passed > self.WAIT:
            self.time_passed = 0
            return 'dodging'


class Laser(Entity):

    SPEED = 600
    IMAGE_FILENAME = path_join('images', 'redlaser.png')

    def __init__(self, world, flip=False):
        sprite = pygame.image.load(Laser.IMAGE_FILENAME).convert_alpha()
        super(Laser, self).__init__(
            world, 'laser', sprite,
            flip=flip,
            speed=Laser.SPEED,
            kill_on_leaving_screen=True,
        )

    def process(self, time_passed):
        if not self.get_destination():
            x = 0 - self.get_width() if self.is_flip() else SCREEN_SIZE[0] + self.get_width()
            self.set_destination(Vector(
                x,
                self.get_location().y
            ))
        super(Laser, self).process(time_passed)
