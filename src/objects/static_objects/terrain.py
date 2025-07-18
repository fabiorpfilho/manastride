""" Classe para o terreno do jogo, são entidades sólidas que não podem ser atacadas	"""
from objects.entity_with_sprite import EntityWithSprite;
from collider import Collider


class Terrain(EntityWithSprite):
    def __init__(self, position, size, image= None):
        super().__init__(position, size, image)
        self.add_collider((0, 0), (self.size.x, self.size.y), type='terrain', solid=True)
