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

    def update_position(self):
        self.rect.x = self.owner.rect.x + self.offset.x
        self.rect.y = self.owner.rect.y + self.offset.y

    def collides_with(self, other):
        rect = pygame.Rect(
            self.owner.rect.x + self.offset.x,
            self.owner.rect.y + self.offset.y,
            self.size.x,
            self.size.y
        )
        return rect.colliderect(other.rect)
    
    def draw_debug(self, surface, rect):
        color = (255, 0, 0) if self.solid else (0, 0, 255)
        pygame.draw.rect(surface, color, rect, 1)
