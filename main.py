import pygame
import menu


SCREEN_SIZE = (800, 600)

def init_screen():
    pygame.init()
    pygame.mouse.set_visible(0)
    pygame.display.set_caption('Sara\'s shooter')
    return pygame.display.set_mode(SCREEN_SIZE)

def main():
    screen = init_screen()
    menu.MainMenu(screen)

if __name__ == '__main__':
    main()
