from objects.entity_with_sprite import EntityWithSprite;
import pygame


class Door(EntityWithSprite):
    def __init__(self, position, size, target_map):
        super().__init__(position, size, image = pygame.Surface(size, pygame.SRCALPHA) )
        self.target_map = target_map
        self.add_collider((0, 0), (self.size.x, self.size.y), type='door', active=True)

