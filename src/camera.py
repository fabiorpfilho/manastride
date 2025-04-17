import pygame
from pygame.math import Vector2


class Camera:
    def __init__(self, screen_size, world_width, world_height):
        self.screen_width, self.screen_height = screen_size
        self.world_width = world_width
        self.world_height = world_height
        self.offset = Vector2(0, 0)

    def update(self, target_rect):
        camera_x = target_rect.centerx - self.screen_width // 2
        camera_y = target_rect.centery - self.screen_height // 2

        # Corrige para que a câmera não ultrapasse os limites do mundo
        max_x = self.world_width - self.screen_width
        max_y = self.world_height - self.screen_height

        # Permite valores negativos, mas limita ao mínimo - ou seja, mostra o mundo até onde ele existe
        self.offset.x = min(max(camera_x, 0), max_x if max_x > 0 else 0)
        self.offset.y = min(max(camera_y, 0), max_y if max_y > 0 else 0)

    def apply(self, rect):
        return rect.move(-int(self.offset.x), -int(self.offset.y))
