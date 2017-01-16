import pygame
import menu
from random import randint
from sara import Sara
from robot import Robot
from world import World
from os import remove as os_remove
from PIL import Image, ImageFilter


# TODO move this to a unique source
SCREEN_SIZE = (800, 600)


class Game:
    SONG_END = pygame.USEREVENT + 1

    def __init__(self, screen):
        self.screen = screen

#        pygame.mixer.pre_init(44100, -16, 2, 1024*4)
        pygame.mixer.music.load("music/intro.wav")
        pygame.mixer.music.set_endevent(Game.SONG_END)
        pygame.mixer.music.play(1)


        self.clock = pygame.time.Clock()

        self.world = World()

        sara = Sara(self.world)
        sara.set_location(100, SCREEN_SIZE[1] / 2)
        self.world.add_entity(sara, ('events', 'player'))

        self.create_robot()
        self.create_robot()
        self.create_robot()

        self.main()

    def main(self):
        should_quit = False
        while not should_quit:
            if randint(1, 500) == 1:
                self.create_robot()

            events = pygame.event.get()
            for event in events:
                if event.type == Game.SONG_END:
                    pygame.mixer.music.load('music/main.wav')
                    pygame.mixer.music.play(-1)
            self.world.process_events(events)
            seconds_passed = self.clock.tick(60) / 1000.0
            should_quit = self.world.process(seconds_passed)
            self.world.render(self.screen)
            pygame.display.update()

        # Quit game
        self.show_game_over()

        menu.MainMenu(self.screen)

    def show_game_over(self):
        filename = 'gameover.jpg'
        pygame.image.save(self.screen, filename)
        im = Image.open(filename)
        im = im.filter(ImageFilter.BLUR)
        im.save(filename)
        self.screen.blit(pygame.image.load(filename), (0, 0))
        os_remove(filename)
        pygame.display.update()
        pygame.time.delay(500)

    def create_robot(self):
        robot = Robot(self.world)
        robot.set_location(randint(0, SCREEN_SIZE[0]), randint(0, SCREEN_SIZE[1]))
        self.world.add_entity(robot, ('enemies', ))
