import pygame
from os.path import join as path_join

from constants import ENEMY_DESTROYED_EVENT, SCREEN_SIZE
from maprender import MapRender
from settings import settings
from vector import Vector


class World:
    LEVEL_ONE_FILENAME = path_join('levels', 'one.tmx')

    def __init__(self):
        self.entities = {'all': pygame.sprite.Group()}

        mapRender = MapRender(World.LEVEL_ONE_FILENAME)
        self.map_surface = mapRender.get_surface()
        self.add_entity(mapRender.get_blocker_entities(), ('blocker'))

        self.viewport = pygame.Rect((0, 0), SCREEN_SIZE)
        self.level_surface = pygame.Surface(mapRender.get_size())

    def add_entity(self, entity, kinds=None):
        self.entities['all'].add(entity)
        if not kinds:
            kinds = tuple()
        for kind in kinds:
            if not self.entities.get(kind):
                # First entity of its kind
                self.entities[kind] = pygame.sprite.Group()
            self.entities[kind].add(entity)

    def process(self, time_passed):
        for entity in self.entities['all']:
            entity.process(time_passed)

        return self.detect_collisions()

    def detect_collisions(self):
        if (self.entities.get('enemies') and self.entities.get('ally_shots')):
            for enemy in self.entities['enemies']:
                collisions = pygame.sprite.spritecollide(enemy, self.entities['ally_shots'], True, pygame.sprite.collide_mask)
                if collisions:
                    event = pygame.event.Event(ENEMY_DESTROYED_EVENT, enemy_class=enemy.__class__)
                    pygame.event.post(event)
                    enemy.kill()

        if self.entities.get('enemy_shots') and not settings['debug']:
            for player in self.entities['player']:
                collisions = pygame.sprite.spritecollide(player, self.entities['enemy_shots'], True, pygame.sprite.collide_mask)
                if collisions:
                    if player.receive_hit():
                        player.kill()
                        return True  # should quit?
        return False


    def render(self, surface):
        player = self.get_player()
        if player:
            self.viewport.center = player.rect.center
            self.viewport.clamp_ip(self.level_surface.get_rect())

        self.level_surface.blit(self.map_surface, self.viewport, self.viewport)

        for entity in self.entities['all']:
            entity.render(self.level_surface)

        surface.blit(self.level_surface, (0, 0), self.viewport)

    def get_close_entity(self, name, location, close=100):
        location = Vector(*location)

        for entity in self.entities['all']:
            if entity.name == name:
                distance = location.get_distance_to(entity.get_location())
                if distance < close:
                    return entity
        return None

    def process_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()

        for entity in self.entities['events']:
            entity.process_events(events)

    def get_player(self):
        try:
            return self.entities['player'].sprites()[0]
        except IndexError:
            return None

    def get_impassable_entities(self, but_me=None):
        return [entity for entity in self.entities['all'] if not entity.is_passable() and entity is not but_me]
