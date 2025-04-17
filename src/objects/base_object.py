"""Classe básica para todos os objetos do jogo"""

import pygame
from pygame.math import Vector2
from collider import Collider

class Object(pygame.sprite.Sprite):

    def __init__(self, position, size):
        super().__init__()
        self.position = Vector2(position)
        self.size = Vector2(size)
        self.colliders = []
        self.image = pygame.Surface((self.size))
        self.rect = self.image.get_rect(
            topleft=(self.position.x, self.position.y))
        
        
    def add_collider(self, offset, size, type, solid):
        collider = Collider(self, offset, size, type, solid)
        self.colliders.append(collider)


    def draw_colliders_debug(self, surface, offset=Vector2(0, 0)):
        # Aplica o deslocamento da câmera nos colliders
        for collider in self.colliders:
            collider_rect = collider.rect.move(-int(offset.x), -int(offset.y))
            # Supondo que o método draw_debug aceite um rect
            collider.draw_debug(surface, collider_rect)
