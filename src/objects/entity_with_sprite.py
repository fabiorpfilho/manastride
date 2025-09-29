#Classe que sera herdada para todas as entidades com sprites, imagens estáticas
import pygame
from objects.base_object import Object
from asset_loader import AssetLoader
from objects.sprite import Sprite


class EntityWithSprite(Object):
    def __init__(self, position, size, image= None):
        super().__init__(position, size)
        self.asset_loader = AssetLoader()
        # self.sprite = Sprite(sprite)
        
        # Se uma imagem for fornecida, usá-la; caso contrário, criar uma superfície padrão
        if image:
            self.image = image
        else:
            self.image = pygame.Surface(size)
            self.image.fill((100, 100, 100))



