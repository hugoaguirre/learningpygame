import pygame
from entity import Entity
from random import randint
from statemachine import State
from vector import Vector


ROBOT_IMAGE_FILENAME = "images/robot.png"


class Robot(Entity):
    SPEED = 100
    def __init__(self, world):
        sprite = pygame.image.load(ROBOT_IMAGE_FILENAME).convert_alpha()
        super(Robot, self).__init__(world, 'Robot', sprite)

        shoting_state = RobotStateShoting(self)
        waiting_state = RobotStateWaiting(self)
        dodging_state = RobotStateDodging(self)

        self.brain.add_state(shoting_state)
        self.brain.add_state(waiting_state)
        self.brain.add_state(dodging_state)

        self.brain.set_state('shoting')

        self.last = pygame.time.get_ticks()
        self.cooldown = 300

    def shoot(self):
        x = self.location.x
        y = self.location.y
        laser = Laser(self.world)
        laser.set_location(x, y)
        self.world.add_entity(laser, ('enemy_shots', ))


class RobotStateDodging(State):
    def __init__(self, robot):
        super(RobotStateDodging, self).__init__('dodging')
        self.robot = robot

    def random_destination(self):
        x = self.robot.location.x
        y = self.robot.location.y
        self.robot.destination = Vector(randint(x-200, x+200), randint(y-200, y + 200))
        self.robot.keep_inside_screen()

    def do_actions(self):
        # just move once and then do nothing
        pass

    def check_conditions(self):
        if (self.robot.location.x == float(self.robot.destination.x) and
            self.robot.location.y == float(self.robot.destination.y)):
            return 'shoting'
        return None

    def entry_actions(self):
        self.robot.speed = Robot.SPEED + randint(-20, -20)
        self.random_destination()

class RobotStateShoting(State):
    def __init__(self, robot):
        super(RobotStateShoting, self).__init__('shoting')
        self.robot = robot
        self.has_shot = False

    def do_actions(self):
        self.robot.shoot()
        self.has_shot = True

    def check_conditions(self):
        if self.has_shot:
            return 'waiting'
        return None

class RobotStateWaiting(State):
    def __init__(self, robot):
        super(RobotStateWaiting, self).__init__('waiting')
        self.robot = robot

    def check_conditions(self):
        # do nothing 
        return 'dodging'


LASER_IMAGE_FILENAME = 'images/redlaser.png'
class Laser(Entity):

    def __init__(self, world):
        sprite = pygame.image.load(LASER_IMAGE_FILENAME).convert_alpha()
        super(Laser, self).__init__(world, 'laser', sprite)
        self.speed = 600

    def process(self, time_passed):
        if not self.destination:
            self.destination = Vector(
                -self.image.get_width(),
                self.location.y
            )
        super(Laser, self).process(time_passed)
