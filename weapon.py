import pygame

from bullet import Bullet

class Weapon():

    def __init__(self, player, world):
        self.magazine_size = 10
        self.bullets_fired = 0
        self.reloading = False

        self.player = player
        self.world = world
        self.reload()

    def reload(self):
        self.reloading = True
        self.bullets_fired = 0
        self.reloading = False

    def fire(self):
        x = self.player.location.x + (0 if self.player.is_flip() else self.player.get_width())
        y = self.player.location.y + self.player.get_height() / 2

        if self.bullets_fired < self.magazine_size:
            bullet = Bullet(self.world, flip=self.player.is_flip())
            bullet.set_location(x, y)
            self.bullets_fired += 1
            self.world.add_entity(bullet, ('ally_shots', ))
        else:
            print 'no ammo'
