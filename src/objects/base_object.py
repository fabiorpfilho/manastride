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
        
        
    def add_collider(self, offset_x, offset_y, width, height, type, solid):
        collider = Collider(self, offset_x, offset_y, width, height, type)
        self.colliders.append(collider)

    def draw_colliders_debug(self, surface):
        for collider in self.colliders:
            collider.draw_debug(surface)
