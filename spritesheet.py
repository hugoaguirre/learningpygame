import pygame


class Spritesheet(object):
    """
    Load a pritesheet and return a single sprite according to its index.
    Right now it only works with one line of sprites, all the same size
    """
    def __init__(self, filename, sprite_width):
        self.spritesheet = pygame.image.load(filename).convert_alpha()
        self.sprite_width = sprite_width
        self.number_sprites = self.spritesheet.get_width() / sprite_width

    def get_image(self, index):
        if index >= self.number_sprites:
            raise ValueError('Sprite {} was requested. not available'.format(index))

        rect = pygame.Rect(self.sprite_width * index,
                           0,
                           self.sprite_width,
                           self.spritesheet.get_height())
        # this line creates a black rectangle
        image = pygame.surface.Surface(rect.size)
        # makes black alpha
        image.set_colorkey(pygame.color.Color('black'))
        # self.spritesheet is already alpha
        image.blit(self.spritesheet, (0, 0), rect)
        return image

    def get_images(self):
        return [self.get_image(i) for i in range(0, self.number_sprites-1)]
