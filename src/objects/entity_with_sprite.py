#Classe que sera herdada para todas as entidades com sprites, imagens estáticas

from objects.base_object import Object

# from ... import Sprite

class EntityWithSprite(Object):
    def __init__(self, position, size, sprite=(255, 255, 255)):
        super().__init__(position, size)
        # self.sprite = Sprite(sprite)
        self.sprite = sprite
        self.image.fill(self.sprite)
        


