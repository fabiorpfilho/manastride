from objects.entity_with_sprite import EntityWithSprite;
import pygame


class Alarm(EntityWithSprite):
    def __init__(self, position, size, name="Alarm"):
        super().__init__(position, size, image = pygame.Surface(size, pygame.SRCALPHA) )
        self.name = name
        self.add_collider((0, 0), (self.size.x, self.size.y), type='alarm', active=True)

