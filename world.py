import pygame
from os.path import join as path_join

from entity import Entity
from door import Door
from constants import ENEMY_DESTROYED_EVENT, SCREEN_SIZE
from maprender import MapRender
from settings import settings
from vector import Vector
from viewport import Viewport


class World:
    LEVEL_ONE_FILENAME = path_join('levels', 'one.tmx')

    def __init__(self):
        self.entities = {'all': pygame.sprite.Group()}

        mapRender = MapRender(World.LEVEL_ONE_FILENAME)
        self.map_surface = mapRender.get_surface()
        self.add_entity(
            mapRender.get_object_entities('blocker', Entity, passable=False),
            ('blockers', )
        )
        self.add_entity(
            mapRender.get_object_entities('door', Door, passable=False),
            ('doors', )
        )
        self.add_entity(
            mapRender.get_object_entities('trigger', Entity, passable=True),
            ('triggers', )
        )

        # parallax this
        basement = mapRender.map_data.get_layer_by_name('basement')
        self.basement = {
            'image': pygame.image.load(basement.source.replace('../', '')),
            'x': 800,
            'y': 650,
        }

        self.viewport = Viewport()

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

    def get_world_limits(self):
        return self.map_surface.get_size()

    def process(self, time_passed):
        self.viewport.move(time_passed)
        for entity in self.entities['all']:
            entity.process(time_passed)

        return self.detect_collisions()

    def detect_collisions(self):
        if (self.entities.get('enemies') and self.entities.get('ally_shots')):
            for enemy in self.entities['enemies']:
                collisions = pygame.sprite.spritecollide(enemy, self.entities['ally_shots'], False, pygame.sprite.collide_mask)
                if collisions:
                    event = pygame.event.Event(ENEMY_DESTROYED_EVENT, enemy_class=enemy.__class__)
                    pygame.event.post(event)
                    enemy.kill()

        if self.entities.get('enemy_shots') and not settings['debug']:
            for player in self.entities['player']:
                collisions = pygame.sprite.spritecollide(player, self.entities['enemy_shots'], False, pygame.sprite.collide_mask)
                if collisions:
                    if player.receive_hit():
                        player.kill()
                        return True  # should quit?

        if self.entities.get('blockers') and self.entities.get('shots'):
            for shot in self.entities['shots']:
                if pygame.sprite.spritecollideany(shot, self.entities['blockers'], pygame.sprite.collide_rect):
                    shot.kill()

        return False


    def render(self, surface):
        player = self.get_player()
        if player:
            old_left = self.viewport.get().left
            old_top = self.viewport.get().top
            self.viewport.center(player.rect.center, self.level_surface.get_rect())
            diff_left = self.viewport.get().left - old_left
            diff_top = self.viewport.get().top - old_top
            self.basement['x'] += int(diff_left * 0.3)
            self.basement['y'] += int(diff_top * 0.3)

        self.level_surface.blit(
            self.basement['image'],
            (self.basement['x'], self.basement['y'])
        )
        self.level_surface.blit(self.map_surface, self.viewport.get(), self.viewport.get())

        for entity in self.entities['all']:
            entity.render(self.level_surface)

        surface.blit(self.level_surface, (0, 0), self.viewport.get())

    def get_close_entities(self, group, location, close=100):
        return [e for e in self.entities[group]
                if location.get_distance_to(e.get_location()) < close]

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
