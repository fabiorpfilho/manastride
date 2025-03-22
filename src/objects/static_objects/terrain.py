""" Classe para o terreno do jogo, são entidades sólidas que não podem ser atacadas	"""
from objects.entity_with_sprite import EntityWithSprite;


class Terrain(EntityWithSprite):
    def __init__(self, position, size, sprite=(100, 100, 100), texture=None,  friction=1.0, damage=0):
        super().__init__(position, size)
        self.texture = texture  
        self.friction = friction  
        self.damage = damage  
        self.sprite = sprite
        
        self.image.fill(self.sprite)
