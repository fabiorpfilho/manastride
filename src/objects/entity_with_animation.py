#Classe que será herdado para todos que tiverem animação
from objects.base_object import Object


class EntityWithAnimation(Object):
    def __init__(self, position, size, sprite=(255, 255, 255)):
        super().__init__(position, size)

        self.sprite = sprite
        self.image.fill(self.sprite)
# A ser construido
