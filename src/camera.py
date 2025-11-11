import pygame
from pygame.math import Vector2

class Camera:
    _instance = None  # Armazena a única instância

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Camera, cls).__new__(cls)
            # Inicialização única aqui (evita chamar __init__ múltiplas vezes)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, screen_size, world_width, world_height, zoom=1.0):
        # Evita reinicializar se já foi criada
        if self._initialized:
            return

        self.screen_size = screen_size
        self.world_width = world_width
        self.world_height = world_height
        self.zoom = zoom
        self.offset = Vector2(0, 0)
        self.target_offset = Vector2(0, 0)
        self.lerp_speed = 0.05  # Velocidade de suavização (0.0 a 1.0)

        self._initialized = True

    @classmethod
    def get_instance(cls, screen_size=None, world_width=None, world_height=None, zoom=1.0):
        """
        Método alternativo para acessar a instância.
        Útil se você quiser reinicializar com novos valores (ex: novo nível).
        """
        if cls._instance is None:
            # Cria a instância com valores padrão se não existir
            dummy_screen = (800, 600)  # Tamanho temporário
            cls(dummy_screen, 1000, 1000, zoom)
        return cls._instance

    def set_zoom(self, zoom):
        self.zoom = max(0.5, min(zoom, 3.0))

    def update(self, player):
        if player is None:
            return

        screen_width, screen_height = self.screen_size
        offset_y = player.current_animation.animation[player.current_frame].offset_y
        target_x = player.rect.centerx - (screen_width / (2 * self.zoom))
        target_y = player.rect.centery - (screen_height / (2 * self.zoom))

        self.target_offset.x = target_x
        self.target_offset.y = target_y

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
        return pygame.transform.scale(surface,
            (int(surface.get_width() * self.zoom), int(surface.get_height() * self.zoom)))

    # Métodos auxiliares para reinicializar mundo/zoom (útil ao trocar de nível)
    def reset_world(self, world_width, world_height, zoom=1.0):
        self.world_width = world_width
        self.world_height = world_height
        self.zoom = zoom
        self.offset = Vector2(0, 0)
        self.target_offset = Vector2(0, 0)

    def set_screen_size(self, screen_size):
        self.screen_size = screen_size