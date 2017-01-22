import pygame
from entity import Entity
from random import randint
from statemachine import StateMachine, State
from vector import Vector


SPRITE_IMAGE_FILENAME = "images/spider.png"


class Spider(Entity):

    SPEED = 100
    SCORE = 500

    def __init__(self, world):
        sprite = pygame.image.load(SPRITE_IMAGE_FILENAME).convert_alpha()
        super(Spider, self).__init__(
            world, 'Spider', sprite,
            brain=self._build_brain(),
            speed=Spider.SPEED,
        )

        self.set_destination(self.get_location())

    def _build_brain(self):
        brain = StateMachine()

        brain.add_state(SpiderStateShoting(self))
        brain.add_state(SpiderStateWaiting(self))
        brain.add_state(SpiderStateDodging(self))

        brain.set_state('waiting')
        return brain

    def shoot(self):
        thunder = Thunder(self.world)
        thunder.set_location(self.get_location() + Vector(31, 34))
        self.world.add_entity(thunder, ('enemy_shots', ))

    def __del__(self):
        print 'bye'


class SpiderStateDodging(State):
    def __init__(self, spider):
        super(SpiderStateDodging, self).__init__('dodging')
        self.spider = spider

    def random_destination(self):
        x = int(self.spider.get_location().x)
        self.spider.set_destination(Vector(randint(x-200, x+200), 1))  # Always on top
        self.spider.keep_inside_screen()

    def do_actions(self):
        # just move once and then do nothing
        pass

    def check_conditions(self, time_passed):
        spider_location = self.spider.get_location()
        spider_destination = self.spider.get_destination()
        if (spider_location.x == float(spider_destination.x) and
            spider_location.y == float(spider_destination.y)):
            return 'shoting'
        return None

    def entry_actions(self):
        self.random_destination()


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
    IMAGE_FILENAME = 'images/thunder.png'

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
