import pygame
from os import remove as os_remove
from os.path import join as path_join
from PIL import Image, ImageFilter
from random import randint

import menu
from sara import Sara
from robot import Robot
from spider import Spider
from tank import Tank
from world import World
from vector import Vector
from settings import settings
from constants import ENEMY_DESTROYED_EVENT, SCREEN_SIZE, SONG_END_EVENT, BOSS_BATTLE_EVENT


LIFE_IMAGE_FILENAME = path_join('images', 'heart.png')


class Game:
    def __init__(self, screen):
        self.screen = screen

#        pygame.mixer.pre_init(44100, -16, 2, 1024*4)
        pygame.mixer.music.load("music/intro.wav")
        pygame.mixer.music.set_endevent(SONG_END_EVENT)
        pygame.mixer.music.play(1)

        self.score = 0

        self.clock = pygame.time.Clock()

        self.world = World()

        self.sara = Sara(self.world)
        self.sara.set_location(Vector(20, 74))
        self.world.add_entity(self.sara, ('events', 'player'))

        self.images = dict()
        self.images['life'] = pygame.image.load(LIFE_IMAGE_FILENAME).convert_alpha()

        if pygame.font.get_init():
            self.font = pygame.font.Font(settings['font'], 80)

        self.robots_created = 0
        for _ in xrange(settings['initial_robots']):
            self.create_robot()

        self.possible_enemies = None
        self.init_enemy_creation()
        self.main()

    def init_enemy_creation(self):
        self.possible_enemies = [None] * 101

    def main(self):
        should_quit = False
        self.possible_enemies[100] = self.create_robot

        while not should_quit:
            if randint(1, 250) == 1:
                # Create an enemy
                hard = randint(0, 99)
                for enemy_creator in self.possible_enemies[hard:]:
                    if enemy_creator:
                        enemy_creator()

            # Adding enemies
            if self.score == 500:
                self.possible_enemies[30] = self.create_spider

            self.process_events()
            seconds_passed = self.clock.tick(60) / 1000.0
            should_quit = self.world.process(seconds_passed)
            self.world.render(self.screen)

            if not should_quit:
                self.render()
            pygame.display.update()

        # Quit game
        self.show_game_over()

        menu.MainMenu(self.screen)

    def process_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == SONG_END_EVENT and not settings['debug']:
                pygame.mixer.music.load('music/main.wav')
                pygame.mixer.music.play(-1)
            if event.type == ENEMY_DESTROYED_EVENT:
                try:
                    self.score += event.enemy_class.SCORE
                except AttributeError:
                    pass  # no score
            if event.type == BOSS_BATTLE_EVENT:
                self.start_boss_battle(event.trigger, event.on_end_callback)
        self.world.process_events(events)

    def render(self):
        '''Use it to render HUD'''
        for i in xrange(0, self.sara.life):
            x = self.images['life'].get_width() * i + 5 * (i + 1)
            self.screen.blit(self.images['life'], (x, 10))

        # Render score
        self._render_surface_score()

    def _render_surface_score(self, prefix=''):
        try:
            surface = self.font.render(prefix + str(self.score), True, (255, 255, 255))
            if surface:
                # TODO height of this font is pretty weird, can manage to render it with a vertical margin of 10
                self.screen.blit(surface, (SCREEN_SIZE[0] - surface.get_width() - 10, 0))
        except AttributeError:
            return None  # not font subsystem available

    def show_game_over(self):
        filename = 'gameover.jpg'
        pygame.image.save(self.screen, filename)
        im = Image.open(filename)
        im = im.filter(ImageFilter.BLUR)
        im.save(filename)
        self.screen.blit(pygame.image.load(filename), (0, 0))

        # Render Score
        self._render_surface_score('Max score: ')

        os_remove(filename)
        pygame.display.update()
        pygame.time.delay(500)

    def create_robot(self):
        robot = Robot(self.world)
        # 150px is just in front of sara
        robot.set_location(Vector(randint(150, SCREEN_SIZE[0]), randint(0, SCREEN_SIZE[1])))
        # Really lazy way to prevent collition at init
        # see Entity.move()
        while robot.is_colliding_with_impassable_entities():
            print 'collide at init'
            robot.set_location(Vector(randint(150, SCREEN_SIZE[0]), randint(0, SCREEN_SIZE[1])))

        self.world.add_entity(robot, ('enemies', ))
        self.robots_created += 1

    def create_spider(self):
        spider = Spider(self.world)
        spider.set_location(Vector(200, 1))
        self.world.add_entity(spider, ('enemies',))

    def start_boss_battle(self, trigger, onend=None):
        trigger.props['action'] = None
        for enemy in self.world.entities['enemies']:
            enemy.kill()
        pygame.mixer.music.load('music/bossbattle.wav')
        pygame.mixer.music.play(-1)
        self.init_enemy_creation()  # No more enemy creation

        tank = Tank(
            self.world,
            'Tank',
            location=Vector(64, 1280),
            flip=False,
            passable=False,
        )
        self.world.add_entity(tank, ('enemies', ))

        self.world.viewport.lock()
        self.world.viewport.move_to(
            Vector(int(trigger.props['move_camera_x']),
                   int(trigger.props['move_camera_y'])),
            on_arrival=lambda: (onend(), tank.build_brain())
        )
