import pygame
import pytmx
from pytmx.util_pygame import load_pygame

from vector import Vector


class MapRender:

    def __init__(self, filename):
        self.map_data = load_pygame(filename)
        self.map_surface = None
        self.blocker_entities = None

    def get_size(self):
        return (self.map_data.width * self.map_data.tilewidth,
                self.map_data.height * self.map_data.tileheight)

    def get_surface(self):
        if not self.map_surface:
            self.map_surface = pygame.Surface(self.get_size())

            if self.map_data.background_color:
                self.map_surface.fill(pygame.Color(self.map_data.background_color))

            for layer in self.map_data.visible_layers:
                if isinstance(layer, pytmx.TiledTileLayer):
                    for x, y, image in layer.tiles():
                        self.map_surface.blit(
                            image,
                            (x * self.map_data.tilewidth,
                             y * self.map_data.tileheight)
                        )

        self.map_surface.set_colorkey(pygame.Color(self.map_data.background_color))
        return self.map_surface

    def get_object_entities(self, name, entity_class, **kwargs):
        entities = []
        for layer in self.map_data.visible_layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                for obj in layer:
                    properties = obj.__dict__
                    if properties['name'] == name:
                        left = properties['x']
                        top = properties['y']
                        width = properties['width']
                        height = properties['height']
                        entity = entity_class(
                            self,
                            name,
                            rect=pygame.Rect(left, top, width, height),
                            location=Vector(left, top),
                            **kwargs
                        )
                        entities.append(entity)
        return entities
