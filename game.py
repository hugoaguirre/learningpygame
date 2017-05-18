## Esto podría ser un código mejor organizado pero... meh
## Este archivo tiene una clase muy importante para el juego
## Game representa el juego en sí, el concepto abstracto del juego
## que orquesta todo lo que está pasando.
## A esta clase vamos a regresar muchas veces, pues es la que tiene
## el ciclo principal del juego, ese que da vueltas 30 veces por segundo,
## también mantiene unidas otras entidades como el mundo, mensajes, las entradas
## del usuario etc.

## un monton de imports
import pygame
from os import remove as os_remove
from os.path import join as path_join
from PIL import Image, ImageFilter
from random import randint

## ¿ya notaste que separo los imports en dos bloques?
## el primero son de la libreria estándar y paquetes de terceros
## este segundo bloque son módulos que están en este mismo paquete
## es una convención usual en los programas de python
from constants import (
    BOSS_BATTLE_EVENT,
    DISPLAY_MESSAGE_EVENT,
    END_GAME_EVENT,
    END_LEVEL_EVENT,
    ENEMY_DESTROYED_EVENT,
    SCREEN_SIZE,
    SONG_END_EVENT
)
import menu
from robot import Robot
from sara import Sara
from settings import settings
from tank import Tank
from vector import Vector
from world import World


LIFE_IMAGE_FILENAME = path_join('images', 'heart.png')


## La clase Game se va a instanciar una sola vez durante toda la ejecución del
## programa, los valores que se inicialian en el cosntructor se van a utilizar
## durante todo el juego e incluyen valores como el jugador, los enemigos, los
## mensajes etc.
class Game:
    def __init__(self, screen):
        ## De nuevo recibimos la pantalla que creamos en main.py, pasamos a
        ## menu.py y la recibimos acá. Vamos a usarla mucho por aquí
        self.screen = screen

        ## Cambiamos de música, comenzando con un intro
        pygame.mixer.music.load("music/intro.wav")
        ## Vamos a ver un poco más sobre eventos, este evento es especial
        ## y se activa cuando se termina la canción, por ahora debemos saber
        ## eso. Más adelante veremos como se manejan los eventos del juego.
        pygame.mixer.music.set_endevent(SONG_END_EVENT)
        pygame.mixer.music.play(1)

        ## El puntaje se lleva a lo largo de todo el juego, es responsabilidad
        ## de Game llevar el puntaje
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
                pygame.mixer.music.load('music/main.wav')
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

    def end_level(self):
        for shot in self.world.entities.get('ally_shots', []):
            shot.kill()
        for shot in self.world.entities.get('enemy_shots', []):
            shot.kill()
        pygame.mixer.music.load('music/end.wav')
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
