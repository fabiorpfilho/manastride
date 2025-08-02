import pygame
from pygame.math import Vector2

class Camera:
    def __init__(self, screen_size, world_width, world_height, zoom=1.0):
        self.screen_size = screen_size
        self.world_width = world_width
        self.world_height = world_height
        self.zoom = zoom
        self.offset = pygame.math.Vector2(0, 0)
        self.target_offset = pygame.math.Vector2(0, 0)
        self.lerp_speed = 0.05  # Velocidade de suavização (0.0 a 1.0)

    def set_zoom(self, zoom):
        self.zoom = max(0.5, min(zoom, 3.0))  # Limita o zoom entre 0.5x e 3x para evitar problemas

    def update(self, player):
        # Calcula a posição desejada da câmera
        screen_width, screen_height = self.screen_size
        offset_y = player.current_animation.animation[player.current_frame].offset_y

        # Use midbottom como referência em vez de center
        target_x = player.rect.centerx - (screen_width / (2 * self.zoom))
        # Subtraia o offset_y para compensar o deslocamento vertical do sprite
        target_y = player.rect.centery - (screen_height / (2 * self.zoom))

        # Define o offset alvo
        self.target_offset.x = target_x
        self.target_offset.y = target_y

        # Interpola suavemente para o offset alvo
        self.offset.x += (self.target_offset.x - self.offset.x) * self.lerp_speed
        self.offset.y += (self.target_offset.y - self.offset.y) * self.lerp_speed

        # Limita o offset para não mostrar fora do mundo
        self.offset.x = max(0, min(self.offset.x, self.world_width - screen_width / self.zoom))
        self.offset.y = max(0, min(self.offset.y, self.world_height - screen_height / self.zoom))

    def apply(self, rect):
        scaled_width = rect.width * self.zoom
        scaled_height = rect.height * self.zoom
        scaled_rect = pygame.Rect(0, 0, scaled_width, scaled_height)
        scaled_x = (rect.x - self.offset.x) * self.zoom
        scaled_y = (rect.y - self.offset.y) * self.zoom
        scaled_rect.topleft = (scaled_x, scaled_y)
        
        return scaled_rect

    def apply_surface(self, surface):
        """Escala uma superfície (imagem) para o zoom atual."""
        return pygame.transform.scale(surface, 
            (int(surface.get_width() * self.zoom), int(surface.get_height() * self.zoom)))