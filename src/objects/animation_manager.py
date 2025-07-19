from objects.animation import Animation
from objects.sprite import Sprite
from objects.animation_type import AnimationType
import os
import pygame

class AnimationManager:
    def __init__(self, animationList=None):
        self.animationList = animationList if animationList is not None else []

    def load_sprites_from_folder(self, folder_path, animation_type: AnimationType):
        """Carrega sprites de uma pasta e cria uma animação, adicionando-a à lista."""
        sprites = []
        try:
            for filename in sorted(os.listdir(folder_path)):
                if filename.endswith(".png"):
                    path = os.path.join(folder_path, filename)
                    image = pygame.image.load(path).convert_alpha()
                    sprites.append(Sprite(image))
            if not sprites:
                print(f"Aviso: Nenhum sprite PNG encontrado em {folder_path}")
                return
            animation = Animation(sprites, animation_type)
            self.animationList.append(animation)
        except FileNotFoundError:
            print(f"Erro: Pasta {folder_path} não encontrada!")