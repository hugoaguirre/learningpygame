import sfx

from bullet import Bullet
from vector import Vector


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

    def fire(self, direction):
        player_location = self.player.get_location()
        x = player_location.x + (0 if self.player.is_flip() else self.player.get_width())
        y = player_location.y + self.player.get_height() / 2

        # Just at weapon's muzzle
        x -= 7
        y += 2

        if self.bullets_fired <= self.magazine_size:
            bullet = Bullet(self.world, flip=not self.player.is_flip(), location=Vector(x, y), direction=direction)
            self.bullets_fired += 1
            self.world.add_entity(bullet, ('ally_shots', 'shots'))
            sfx.play_laser2()
            return True
        else:
            return False
