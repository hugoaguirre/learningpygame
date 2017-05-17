import pygame
from os.path import join as path_join

from vector import Vector
from entity import Entity
from spritesheet import Spritesheet
from weapon import Weapon
from constants import BOSS_BATTLE_EVENT

RELOAD_BUTTON_IMAGE_FILENAME = path_join('images', 'button_r.png')

class Sara(Entity):

    SPEED = 250
    ANIMATION_TICKS = 5
    IMAGE_FILENAME = path_join('images', 'newsara.png')
    DOWN_IMAGE_FILENAME = path_join('images', 'saradown.png')
    UP_IMAGE_FILENAME = path_join('images', 'saraup.png')

    def __init__(self, world):
        ss = Spritesheet(Sara.IMAGE_FILENAME, 44)
        self.ss = {
            'left': ss,
            'right': ss,
            'up': Spritesheet(Sara.UP_IMAGE_FILENAME, 44),
            'down': Spritesheet(Sara.DOWN_IMAGE_FILENAME, 44)
        }
        super(Sara, self).__init__(
            world, 'sara',
            spritesheet=self.ss['right'],
            passable=False,
            can_leave_screen=True,
            speed=Sara.SPEED
        )

        self.animation = 0
        self.animation_time = 0
        self.moving = False

        # Weapon init
        self.weapon = Weapon(self, world)

        self.life = 3
        self.auto = False
        self.image_reload = pygame.image.load(RELOAD_BUTTON_IMAGE_FILENAME).convert_alpha()
        self.show_reload = False
        self._keys = []
        self.face_to = 'right'
        self.flip()

    def process(self, time_passed):
        self.open_doors()
        self.activate_triggers()
        super(Sara, self).process(time_passed)

    def open_doors(self):
        for door in self.world.get_close_entities('doors', self.get_location()):
            door.open(self._keys)

    def activate_triggers(self):
        for trigger in self.world.get_close_entities('triggers', self.get_location(), 50):
            if trigger.props['action'] == 'boss_battle':
                e = pygame.event.Event(
                    BOSS_BATTLE_EVENT,
                    {
                        'on_end_callback':lambda: (trigger.set_passable(False), self.set_auto(False)),
                        'trigger': trigger
                    }
                )
                pygame.event.post(e)
                self.auto_move(self.get_location() - Vector(128, 0))

    def set_auto(self, auto):
        self.auto = auto

    def process_events(self, events):
        if self.auto:
            return

        pressed_keys = pygame.key.get_pressed()
        direction = Vector(0, 0)
        if pressed_keys[pygame.K_LEFT]:
            direction.x = -1
            self.reverse_flip()
        elif pressed_keys[pygame.K_RIGHT]:
            direction.x = +1
            self.flip()

        if pressed_keys[pygame.K_UP]:
            direction.y = -1
        elif pressed_keys[pygame.K_DOWN]:
            direction.y = +1

        if pressed_keys[pygame.K_r]:
            self.weapon.reload()
            self.show_reload = False

        direction.normalize()

        old_face_to = self.face_to
        facing = list()
        if direction.x > 0:
            facing.append('right')
        elif direction.x < 0:
            facing.append('left')

        if direction.y > 0:
            facing.append('down')
        elif direction.y < 0:
            facing.append('up')

        if facing and self.face_to not in facing:
            self.face_to = facing[0]
            self.set_spritesheet(self.ss[self.face_to])

        self.set_destination(self.get_location() + Vector(
            direction.x * self.get_speed(),
            direction.y * self.get_speed()))

        for event in events:
            if (event.type == pygame.KEYDOWN and
                event.key == pygame.K_SPACE):
                self.fire()

    def fire(self):
        if not self.weapon.fire(self.face_to):
            self.show_reload = True

    def auto_move(self, destination):
        self.auto = True
        self.set_destination(destination)

    def receive_hit(self):
        '''Perform actions when player receive hit, return boolean
        indicating if entity should die'''

        self.life -= 1
        self.flash()
        return self.life == 0

    def render(self, surface):
        # This is HUD, but not rendered at game.py we render here
        # because it is not fixed on screen but it follows sara
        # needs to be render to level_surface (see World.render)
        if self.show_reload:
            x, y = self.rect.midtop
            y -= self.image_reload.get_height() + 4
            x -= 14 if self.is_flip() else 26
            surface.blit(self.image_reload, (x, y))

        super(Sara, self).render(surface)

    def move(self, time_passed):
        is_moving = super(Sara, self).move(time_passed)
        if is_moving:
            # here it was a case where no moving loop finish with
            # self.animation_time equals to zero, and not valid
            # sprites were being requested
            if self.animation in (0, 4):
                self.animation = 1
            if self.animation_time == 0:
                self.animation += -2 if self.animation == 3 else 1
                self.animation_time = self.ANIMATION_TICKS
            else:
                self.animation_time -= 1
        else:
            self.set_auto(False)
            if self.animation in (1, 2, 3):  # was just moving
                self.animation_time = self.ANIMATION_TICKS / 2  # shorter stop animation
                self.animation = 4
            elif self.animation == 4 and self.animation_time != 0:
                self.animation_time -= 1
            else:
                self.animation = 0
        self.set_image(self.get_spritesheet().get_image(self.animation))
