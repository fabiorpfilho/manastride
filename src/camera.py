import pygame
from pygame.math import Vector2

class Camera:
    def __init__(self, screen_size, world_width, world_height, zoom=1.0):
        self.screen_width, self.screen_height = screen_size
        self.world_width = world_width
        self.world_height = world_height
        self.offset = Vector2(0, 0)
        self.zoom = zoom  # Fator de zoom inicial (1.0 = sem zoom, 2.0 = 2x maior, etc.)

    def set_zoom(self, zoom):
        """Define o nível de zoom."""
        self.zoom = max(0.5, min(zoom, 3.0))  # Limita o zoom entre 0.5x e 3x para evitar problemas

    def update(self, target_rect):
        # Calcula a posição da câmera centrada no alvo
        camera_x = target_rect.centerx - (self.screen_width / (2 * self.zoom))
        camera_y = target_rect.centery - (self.screen_height / (2 * self.zoom))

        # Corrige para que a câmera não ultrapasse os limites do mundo
        max_x = self.world_width - self.screen_width / self.zoom
        max_y = self.world_height - self.screen_height / self.zoom

        # Permite valores negativos, mas limita ao mínimo
        self.offset.x = min(max(camera_x, 0), max_x if max_x > 0 else 0)
        self.offset.y = min(max(camera_y, 0), max_y if max_y > 0 else 0)

    def apply(self, rect):
        """Aplica o deslocamento e o zoom ao retângulo."""
        # Escala o retângulo com base no zoom
        scaled_width = rect.width * self.zoom
        scaled_height = rect.height * self.zoom
        scaled_rect = pygame.Rect(0, 0, scaled_width, scaled_height)

        # Calcula a posição escalada e ajustada pelo offset
        scaled_x = (rect.x - self.offset.x) * self.zoom
        scaled_y = (rect.y - self.offset.y) * self.zoom
        scaled_rect.topleft = (scaled_x, scaled_y)

        return scaled_rect

    def apply_surface(self, surface):
        """Escala uma superfície (imagem) para o zoom atual."""
        return pygame.transform.scale(surface, 
            (int(surface.get_width() * self.zoom), int(surface.get_height() * self.zoom)))