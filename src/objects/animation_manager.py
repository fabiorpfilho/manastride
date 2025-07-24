from objects.animation import Animation
from objects.sprite import Sprite
from objects.animation_type import AnimationType
import os
import pygame
import json

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


    def load_animations_from_json(self, sheet_path, json_path, animation_type: str):
        try:
            sheet = pygame.image.load(sheet_path).convert_alpha()
            
            with open(json_path, "r") as f:
                data = json.load(f)

            if animation_type not in data:
                print(f"Aviso: Animação '{animation_type}' não encontrada no JSON.")
                return

            sprites = []
            for x, y, w, h in data[animation_type]:
                frame = sheet.subsurface(pygame.Rect(x, y, w, h))
                sprites.append(Sprite(frame))

            animation = Animation(sprites, animation_type)
            self.animationList.append(animation)

        except Exception as e:
            print(f"Erro ao carregar spritesheet ou JSON: {e}")


    
