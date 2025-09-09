from objects.base_object import Object
import pygame
from objects.animation_manager import AnimationManager
from typing import Optional

class EntityWithAnimation(Object):
    def __init__(self, position, size, sprite=(255, 255, 255)):
        super().__init__(position, size)
        self.sprite = sprite
        self.animation_manager = AnimationManager()
        self.animation_timer = 0
        self.image.fill(self.sprite)  # Preenche com a cor padrão se não houver animação
        
                
