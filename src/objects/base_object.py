"""Classe básica para todos os objetos do jogo"""

import pygame
from pygame.math import Vector2
from collider import Collider

class Object:

    def __init__(self, position, size):
        self.position = Vector2(position)
        self.size = Vector2(size)
        self.colliders = []
        self.image = pygame.Surface((self.size))
        self.rect = self.image.get_rect(
            topleft=(self.position.x, self.position.y))
        
    def add_collider(self, offset, size, type, solid):
        collider = Collider(self, offset, size, type, solid)
        self.colliders.append(collider)

    def draw_colliders_debug(self, surface, camera):
        # Aplica o deslocamento e o zoom da câmera nos colliders
        for collider in self.colliders:
            # Usa camera.apply para transformar o retângulo do colisor
            collider_rect = camera.apply(collider.rect)
            # Desenha o colisor com o retângulo já escalado
            # collider.draw_debug(surface, collider_rect)