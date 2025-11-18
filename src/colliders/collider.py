# colliders/collider.py
import pygame
from pygame.math import Vector2


class Collider:
    def __init__(self, owner, offset: tuple, size: tuple, active: bool = True):
        self.owner = owner
        self.offset = Vector2(offset)
        self.size = Vector2(size)
        self.active = active
        self.rect = pygame.Rect(0, 0, int(self.size.x), int(self.size.y))
        self.update_position()

    def update_position(self):
        """Atualiza a posição do collider com base no owner e facing direction."""
        owner_rect = self.owner.rect
        if getattr(self.owner, "facing_right", True):  # default True se não tiver
            x = owner_rect.x + self.offset.x
        else:
            x = owner_rect.right - self.offset.x - self.size.x
        y = owner_rect.y + self.offset.y
        self.rect.topleft = (x, y)

    def draw_debug(self, surface, color=(255, 255, 255)):
        """Desenha o retângulo do collider para debug."""
        if self.active:
            pygame.draw.rect(surface, color, self.rect, 2)

    def handle_collision(self, other_collider: 'Collider', collision_manager):
        """Método a ser sobrescrito por subclasses."""
        pass