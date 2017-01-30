from sys import exit as sys_exit
import ezmenu
import pygame
import game
from settings import settings
from constants import SCREEN_SIZE


class MainMenu:

    def __init__(self, screen):
        self.screen = screen
        self.menu = ezmenu.EzMenu(
            ['Start', lambda: game.Game(screen)],
            ['Quit', sys_exit]
        )

        self.menu.set_highlight_color((255, 0, 0))
        self.menu.set_normal_color((255, 255, 255))
        self.menu.center_at(SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2)
        self.menu.set_font(pygame.font.Font(settings['font'], 60))

        self.clock = pygame.time.Clock()

        self.main()

    def main(self):
        pygame.mixer.music.load("music/menu.wav")
        pygame.mixer.music.play(-1)

        while True:
            self.clock.tick(30)
            events = pygame.event.get()
            self.menu.update(events)
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()

            self.menu.draw(self.screen)
            pygame.display.flip()
