#Todos os parametros de um colisor, o tipo de colisão se o objeto ao sofre colisão fica com invenciblidade, etc.
#Também deverá ser salvo dentro do colider o objeto ao qual ele foi chamado, então por exemplo, o player terá
# uma lista de colliders, ex: O mario possui o collider geral do corpo topo, que serve para registrar hits, impedir
# que ele passe por paredes e vãos menores que ele, da mesma forma ele tem um collider na cabeça para registrar
import pygame
from pygame.math import Vector2

class Collider:
    def __init__(self, owner, offset, size, type='body', active=True):
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
        self.active = active  # Define se a colisão será tratada ou não

    def update_position(self, owner_rect, facing_right=None):
        offset_x = self.offset[0]
        offset_y = self.offset[1]

        if facing_right is None:
            # Ignora espelhamento
            self.rect.topleft = (
                owner_rect.x + offset_x,
                owner_rect.y + offset_y
            )
        elif facing_right:
            self.rect.topleft = (
                owner_rect.x + offset_x,
                owner_rect.y + offset_y
            )
        else:
            self.rect.topleft = (
                owner_rect.right - offset_x - self.size.x,
                owner_rect.y + offset_y
            )

            
    
    def draw_debug(self, surface, rect):
        if self.type == 'hurt_box':
            color = (255, 100, 100)
        elif self.type == 'attack_box':
            color = (100, 255, 100) if self.active else (200, 200, 200) 
        elif self.type == 'body':
            color = (0, 0, 255)
        pygame.draw.rect(surface, color, rect, 1)
