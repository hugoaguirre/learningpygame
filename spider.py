import pygame
from entity import Entity
from random import randint
from statemachine import State
from vector import Vector


SPRITE_IMAGE_FILENAME = "images/spider.png"


class Spider(Entity):

    SPEED = 100
    SCORE = 500

    def __init__(self, world):
        sprite = pygame.image.load(SPRITE_IMAGE_FILENAME).convert_alpha()
        super(Spider, self).__init__(world, 'Spider', sprite)
        self.speed = Spider.SPEED
        self.destination = self.location

        shoting_state = SpiderStateShoting(self)
        waiting_state = SpiderStateWaiting(self)
        dodging_state = SpiderStateDodging(self)

        self.brain.add_state(shoting_state)
        self.brain.add_state(waiting_state)
        self.brain.add_state(dodging_state)

        self.brain.set_state('dodging')

        self.last = pygame.time.get_ticks()
        self.cooldown = 300

    def shoot(self):
        x = self.location.x + 31
        y = self.location.y + 34
        thunder = Thunder(self.world)
        thunder.set_location(x, y)
        self.world.add_entity(thunder, ('enemy_shots', ))

    def __del__(self):
        print 'bye'


class SpiderStateDodging(State):
    def __init__(self, spider):
        super(SpiderStateDodging, self).__init__('dodging')
        self.spider = spider

    def random_destination(self):
        x = int(self.spider.location.x)
        self.spider.destination = Vector(randint(x-200, x+200), 1)  # Always on top
        self.spider.keep_inside_screen()

    def do_actions(self):
        # just move once and then do nothing
        pass

    def check_conditions(self):
        if (self.spider.location.x == float(self.spider.destination.x) and
            self.spider.location.y == float(self.spider.destination.y)):
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

    def check_conditions(self):
        if self.has_shot:
            return 'waiting'
        return None

class SpiderStateWaiting(State):
    def __init__(self, robot):
        super(SpiderStateWaiting, self).__init__('waiting')
        self.robot = robot

    def check_conditions(self):
        # do nothing 
        return 'dodging'


THUNDER_IMAGE_FILENAME = 'images/thunder.png'
class Thunder(Entity):

    def __init__(self, world):
        sprite = pygame.image.load(THUNDER_IMAGE_FILENAME).convert_alpha()
        super(Thunder, self).__init__(world, 'thunder', sprite)
        self.speed = 1200

    def process(self, time_passed):
        if not self.destination:
            self.destination = Vector(
                self.location.x,
                self.image.get_height(),
            )
        super(Thunder, self).process(time_passed)
