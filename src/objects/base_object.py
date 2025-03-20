"""Classe básica para todos os objetos do jogo"""

import pygame
from pygame.math import Vector2

class Object(pygame.sprite.Sprite):

    def __init__(self, position, size):
        super().__init__()
        self.position = Vector2(position)
        self.size = Vector2(size)
   
        self.image = pygame.Surface((self.size))
        self.rect = self.image.get_rect(
            topleft=(self.position.x, self.position.y))
