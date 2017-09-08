import pygame
from random import randint
from os.path import join as path_join

from entity import Entity
from statemachine import StateMachine, State
from vector import Vector


class Spider(Entity):
    SPEED = 1000
    SCORE = 500
    IMAGE_FILENAME = path_join('assets', 'images', 'spider.png')

    def __init__(self, world):
        sprite = pygame.image.load(Spider.IMAGE_FILENAME).convert_alpha()
        super(Spider, self).__init__(
            world, 'Spider', sprite,
            brain=self._build_brain(),
            speed=Spider.SPEED,
        )

    def _build_brain(self):
        brain = StateMachine()

        brain.add_state(SpiderStateShoting(self))
        brain.add_state(SpiderStateWaiting(self))
        brain.add_state(SpiderStateChasing(self))

        brain.set_state('chasing')
        return brain

    def shoot(self):
        thunder = Thunder(self.world)
        thunder.set_location(self.get_location() + Vector(31, 34))
        self.world.add_entity(thunder, ('enemy_shots', 'shots'))


class SpiderStateChasing(State):
    def __init__(self, spider):
        super(SpiderStateChasing, self).__init__('chasing')
        self.spider = spider

    def do_actions(self):
        # just move once and then do nothing
        pass

    def check_conditions(self, time_passed):
        sara = self.spider.world.get_player()
        sara_location = sara.get_location()

        spider_location = self.spider.get_location()
        spider_destination = sara_location

        self.spider.set_location(sara_location)

        if (spider_location.x == float(spider_destination.x) and
            spider_location.y == float(spider_destination.y)):
            return 'shoting'
        return None

    def entry_actions(self):
        pass


class SpiderStateShoting(State):
    def __init__(self, spider):
        super(SpiderStateShoting, self).__init__('shoting')
        self.spider = spider
        self.has_shot = False

    def do_actions(self):
        self.spider.shoot()
        self.has_shot = True
        self.spider.kill()

    def check_conditions(self, time_passed):
        if self.has_shot:
            return 'waiting'
        return None


class SpiderStateWaiting(State):
    def __init__(self, robot):
        super(SpiderStateWaiting, self).__init__('waiting')
        self.robot = robot

    def check_conditions(self, time_passed):
        # do nothing
        return 'dodging'


class Thunder(Entity):

    SPEED = 1200
    IMAGE_FILENAME = 'assets/images/thunder.png'

    def __init__(self, world):
        sprite = pygame.image.load(Thunder.IMAGE_FILENAME).convert_alpha()
        super(Thunder, self).__init__(world, 'Thunder', sprite, speed=Thunder.SPEED)

    def process(self, time_passed):
        if not self.get_destination():
            self.set_destination(Vector(
                self.get_location().x,
                self.get_height(),
            ))
        super(Thunder, self).process(time_passed)
