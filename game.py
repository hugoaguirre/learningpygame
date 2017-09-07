import pygame
from os import remove as os_remove
from os.path import join as path_join
from PIL import Image, ImageFilter
from random import randint

import menu
from sara import Sara
from robot import Robot
from tank import Tank
from world import World
from vector import Vector
from settings import settings
from constants import ENEMY_DESTROYED_EVENT, SCREEN_SIZE, SONG_END_EVENT, BOSS_BATTLE_EVENT, DISPLAY_MESSAGE_EVENT, END_LEVEL_EVENT, END_GAME_EVENT


LIFE_IMAGE_FILENAME = path_join('assets', 'images', 'heart.png')

MUSIC_BOSS_BATTLE = path_join('assets', 'music', 'bossbattle.wav')
MUSIC_MAIN = path_join('assets', 'music', 'main.wav')
MUSIC_INTRO = path_join('assets', 'music', 'intro.wav')
MUSIC_END = path_join('assets', 'music', 'end.wav')


class Game:
    def __init__(self, screen):
        self.screen = screen

        pygame.mixer.music.load(MUSIC_INTRO)
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

        self.messages = []
        self.possible_enemies = None
        self.init_enemy_creation()
        self.main()

    def init_enemy_creation(self):
        self.possible_enemies = [None] * 101

    def main(self):
        should_quit = False
        self.possible_enemies[100] = self.create_robot

        while not should_quit:
            should_quit = self.process_events()
            should_quit |= self.process()
            self.render(should_quit)
            pygame.display.update()

        # Quit game
        self.show_game_over()
        menu.MainMenu(self.screen)

    def process(self):
        seconds_passed = self.clock.tick(60) / 1000.0
        for message in self.messages:
            message.process(seconds_passed)
        self.create_enemies()
        should_quit = self.world.process(seconds_passed)
        return should_quit

    def create_enemies(self):
        if randint(1, 100) == 1:
            # Create an enemy
            hard = randint(0, 99)
            for enemy_creator in self.possible_enemies[hard:]:
                if enemy_creator:
                    enemy_creator()

    def process_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == SONG_END_EVENT and not settings['debug']:
                pygame.mixer.music.load(MUSIC_MAIN)
                pygame.mixer.music.play(-1)
            if event.type == ENEMY_DESTROYED_EVENT:
                try:
                    self.score += event.enemy_class.SCORE
                except AttributeError:
                    pass  # no score
            if event.type == BOSS_BATTLE_EVENT:
                self.start_boss_battle(event.trigger, event.on_end_callback)
            if event.type == DISPLAY_MESSAGE_EVENT:
                self.messages.append(Message(event.message))
            if event.type == END_LEVEL_EVENT:
                self.end_level()
            if event.type == END_GAME_EVENT:
                return True

        self.world.process_events(events)
        return False

    def render(self, should_quit):
        self.world.render(self.screen)

        if not should_quit:
            # Use it to render HUD
            for i in xrange(0, self.sara.life):
                x = self.images['life'].get_width() * i + 5 * (i + 1)
                self.screen.blit(self.images['life'], (x, 10))

            # Render score
            self._render_surface_score()

            for message in self.messages:
                message.render(self.screen)

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
        sarax = int(self.sara.get_location().x)
        saray = int(self.sara.get_location().y)
        while True:
            x = randint(max(0, sarax - 600), min(sarax + 600, self.world.level_surface.get_width()))
            y = randint(max(0, saray - 600), min(saray + 600, self.world.level_surface.get_height()))
            robot.set_location(Vector(x, y))
            # Really lazy way to prevent collition at init
            if not robot.is_colliding_with_impassable_entities():
                break

        self.world.add_entity(robot, ('enemies', ))
        self.robots_created += 1

    def start_boss_battle(self, trigger, onend=None):
        trigger.props['action'] = None
        for enemy in self.world.entities.get('enemies', []):
            enemy.kill()
        for laser in self.world.entities.get('enemy_shots', []):
            laser.kill()
        pygame.mixer.music.load(MUSIC_BOSS_BATTLE)
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

    def end_level(self):
        for shot in self.world.entities.get('ally_shots', []):
            shot.kill()
        for shot in self.world.entities.get('enemy_shots', []):
            shot.kill()
        pygame.mixer.music.load(MUSIC_END)
        pygame.mixer.music.set_endevent(END_GAME_EVENT)
        pygame.mixer.music.play(0)
        self.sara.auto_move(Vector(360, 1350))
        self.sara.set_spritesheet(self.sara.ss['down'])

class Message:
    def __init__(self, message, timeout=2, position=(400, 300)):
        self.timeout = timeout
        self.time_passed = 0
        self.surface = None
        if pygame.font.get_init():
            font = pygame.font.Font(settings['font'], 80)
            self.surface = font.render(message, True, (255, 255, 255))
            if position:
                self.rect = self.surface.get_rect()
                self.rect.center = position

    def process(self, time_passed):
        self.time_passed += time_passed
        if self.time_passed > self.timeout:
            self.surface = None
            return False
        return True

    def render(self, surface):
        if self.surface:
            surface.blit(self.surface, self.rect)
