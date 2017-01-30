import pygame
import menu
import argparse
from settings import settings
from constants import SCREEN_SIZE


def init_screen():
    pygame.init()
    pygame.mouse.set_visible(0)
    pygame.display.set_caption('Sara\'s shooter')
    return pygame.display.set_mode(SCREEN_SIZE)


def parse_args():
    parser = argparse.ArgumentParser(description='Sara is shooting some robots')
    parser.add_argument('--debug', help='Useful for debugging purposes', default=False, action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()
    settings['debug'] = args.debug
    screen = init_screen()
    menu.MainMenu(screen)

if __name__ == '__main__':
    main()
