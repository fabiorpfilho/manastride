#Todos os parametros de um colisor, o tipo de colisão se o objeto ao sofre colisão fica com invenciblidade, etc.
#Também deverá ser salvo dentro do colider o objeto ao qual ele foi chamado, então por exemplo, o player terá
# uma lista de colliders, ex: O mario possui o collider geral do corpo topo, que serve para registrar hits, impedir
# que ele passe por paredes e vãos menores que ele, da mesma forma ele tem um collider na cabeça para registrar
import pygame

class Collider:
    def __init__(self, owner, offset_x, offset_y, width, height, type='default', solid=True, damage=0, invincible=False):
        self.owner = owner  # Objeto que possui esse collider
        self.offset_x = offset_x  # Distância em X relativa ao owner
        self.offset_y = offset_y  # Distância em Y relativa ao owner
        self.rect = pygame.Rect(
            owner.rect.x + offset_x,
            owner.rect.y + offset_y,
            width,
            height
        )
        self.type = type  # Tipo do collider (ex: hitbox, trigger, damage)
        self.solid = solid  # Define se impede passagem

    def update_position(self):
        self.rect.x = self.owner.rect.x + self.offset_x
        self.rect.y = self.owner.rect.y + self.offset_y

    def collides_with(self, other):
        return self.rect.colliderect(other.rect)
    
    def draw_debug(self, surface):
        color = (255, 0, 0) if self.solid else (0, 0, 255)
        pygame.draw.rect(surface, color, self.rect, 1)
