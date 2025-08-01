#Todos os parametros de um colisor, o tipo de colisão se o objeto ao sofre colisão fica com invenciblidade, etc.
#Também deverá ser salvo dentro do colider o objeto ao qual ele foi chamado, então por exemplo, o player terá
# uma lista de colliders, ex: O mario possui o collider geral do corpo topo, que serve para registrar hits, impedir
# que ele passe por paredes e vãos menores que ele, da mesma forma ele tem um collider na cabeça para registrar
import pygame
from pygame.math import Vector2

class Collider:
    def __init__(self, owner, offset, size, type='body', solid=True):
        self.owner = owner  # Objeto que possui esse collider
        self.offset = Vector2(offset)
        self.size = Vector2(size)
        self.rect = pygame.Rect(
            owner.rect.x + self.offset.x,
            owner.rect.y + self.offset.y,
            self.size.x,
            self.size.y
        )
        self.type = type  # Tipo do collider (ex: hitbox, ataque, damage)
        self.solid = solid  # Define se impede passagem

    def update_position(self, facing_rigt):
        # print(f"Collider.update_position: collider.rect.x={self.rect.x}, collider.rect.y={self.rect.y}, parent.position.x={self.owner.position.x}, parent.position.y={self.owner.position.y}, parent.rect.x={self.owner.rect.x}, parent.rect.y={self.owner.rect.y}")
        if not facing_rigt:
            self.rect.x = self.owner.rect.centerx + self.offset.x
            self.rect.y = self.owner.rect.centery + self.offset.y
        else:    
            self.rect.x = self.owner.rect.centerx + self.offset.x
            self.rect.y = self.owner.rect.centery + self.offset.y
    
    def draw_debug(self, surface, rect):
        color = (255, 0, 0) if self.solid else (0, 0, 255)
        pygame.draw.rect(surface, color, rect, 1)
