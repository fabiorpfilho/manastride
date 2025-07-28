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


    def load_animations_from_json(self, size, image_path, json_path):
        try:
            sheet = pygame.image.load(image_path).convert_alpha()
            with open(json_path, 'r') as f:
                data = json.load(f)

            CHARACTER_WIDTH = size.x  # 20
            CHARACTER_HEIGHT = size.y  # 30
            ANCHOR_X = CHARACTER_WIDTH // 2  # 10
            ANCHOR_Y = CHARACTER_HEIGHT  # 30

            for anim_name, frames in data.items():
                sprites = []
                anim_type = AnimationType[anim_name.upper()]
                if anim_type in [AnimationType.ATTACK1, AnimationType.ATTACK2, AnimationType.ATTACK3] and image_path.endswith("adventurer-v1.5-Sheet1.png"):
                    print(f"Carregando animação {anim_name} de {image_path}")
                for i, (x, y, w, h) in enumerate(frames):
                    sprite_image = sheet.subsurface(pygame.Rect(x, y, w, h))

                    # Altura final: acomoda o sprite, mas mantém o chão fixo
                    extra_top = max(0, h - CHARACTER_HEIGHT)
                    final_height = CHARACTER_HEIGHT + extra_top
                    final_width = max(CHARACTER_WIDTH, w)

                    final_surface = pygame.Surface((final_width, final_height), pygame.SRCALPHA)

                    # Posição do sprite no surface final
                    draw_x = (final_width // 2) - (w // 2)
                    draw_y = final_height - h

                    final_surface.blit(sprite_image, (draw_x, draw_y))

                    # Armazenar offsets
                    sprite = Sprite(final_surface)
                    sprite.offset_x = -(final_width // 2 - ANCHOR_X)
                    sprite.offset_y = -(final_height - ANCHOR_Y)

                    # if anim_type in [AnimationType.ATTACK1, AnimationType.ATTACK2, AnimationType.ATTACK3]  and image_path.endswith("adventurer-v1.5-Sheet1.png"):
                    #    print(f"Frame {i+1}: w={w}, h={h}, final_width={final_width}, final_height={final_height}, draw_x={draw_x}, draw_y={draw_y}, offset_x={sprite.offset_x}, offset_y={sprite.offset_y}")
                    sprites.append(sprite)

                animation = Animation(sprites, anim_type)
                self.animationList.append(animation)

        except Exception as e:
            print(f"Erro ao carregar spritesheet ou JSON: {e}")


    
