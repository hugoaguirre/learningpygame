import pygame

pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
pygame.init()

laser = pygame.mixer.Sound('sfx/laser.wav')
laser.set_volume(0.2)
laser2 = pygame.mixer.Sound('sfx/laser2.wav')
laser2.set_volume(0.2)

def play_laser():
    laser.play()

def play_laser2():
    laser2.play()
