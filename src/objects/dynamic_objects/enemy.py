from objects.dynamic_objects.character import Character
from config import SPEED, JUMP_SPEED, GRAVITY
import pygame
from objects.animation_type import AnimationType
from typing import Optional
from objects.animation_manager import AnimationManager
from objects.sprite import Sprite
from objects.animation import Animation
import json

class Enemy(Character):
    def __init__(self, position, size, animation_manager: Optional['AnimationManager'] = None, 
                 sprite=(0, 255, 0), collide_damage=5, invincible=False, health=100, 
                 attackable=True, attack_speed=0, damage=10, speed=0, gravity=0, 
                 speed_vector=(0, 0), jump_speed=0):
        
        super().__init__(position, size, None, sprite, collide_damage, invincible, health,
                         attackable, attack_speed, damage, speed, gravity, speed_vector, jump_speed)
        
        self.animation_manager = animation_manager
        self.current_animation = None
        self.current_frame = 0
        self.animation_timer = 0
        self.is_attacking = False
        self.attack_cooldown = 0.3

        self.animation_speeds = {
            AnimationType.IDLE1: 0.35,
            AnimationType.WALK: 0.1,
            AnimationType.ATTACK1: 0.1,
            AnimationType.JUMP: 0.15,
            AnimationType.FALLING: 0.15,
        }

        self.facing_right = True
        self.add_collider((0, 0), self.size, type='body', solid=True)

        if self.animation_manager:
            self.load_animations_from_json(
                image_path="assets/hammer_bot/PackedSpriteSheet.png",
                json_path="assets/hammer_bot/PackedSpriteSheet.json"
            )
            if not self.animation_manager.animationList:
                print("Erro: Nenhuma animação carregada")
            else:
                self.set_animation(AnimationType.IDLE1)

    def load_animations_from_json(self, image_path, json_path):
        try:    
            sheet = pygame.image.load(image_path).convert_alpha()
            with open(json_path, 'r') as f:
                data = json.load(f)

            for anim_name, frames in data.items():
                sprites = []
                for x, y, w, h in frames:
                    sprite_image = sheet.subsurface(pygame.Rect(x, y, w, h))
                    sprites.append(Sprite(sprite_image))

                anim_type = AnimationType[anim_name.upper()]
                animation = Animation(sprites, anim_type)
                self.animation_manager.animationList.append(animation)
        except Exception as e:
            print(f"Erro ao carregar spritesheet ou JSON: {e}")

    def set_animation(self, animation_type: AnimationType):
        if not self.animation_manager:
            print("Aviso: Nenhum AnimationManager fornecido")
            return
        for animation in self.animation_manager.animationList:
            if animation.type == animation_type:
                if self.current_animation != animation:
                    self.current_animation = animation
                    self.current_frame = 0
                    self.animation_timer = 0
                    self.is_attacking = (animation_type == AnimationType.ATTACK1)
                    self.update_image()
                return
        print(f"Aviso: Animação {animation_type} não encontrada")

    def update_image(self):
        if self.current_animation and self.current_animation.animation:
            sprite = self.current_animation.animation[self.current_frame].image
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)
            self.image = sprite
            self.rect = self.image.get_rect(topleft=(self.position.x, self.position.y))
        else:
            self.image.fill(self.sprite)

    def movement_update(self, delta_time):
        # Movimento autônomo (exemplo: andar em linha reta)
        self.speed_vector.x = self.speed
        self.position.x += self.speed_vector.x * delta_time

        # Gravidade e queda
        g = (self.gravity + GRAVITY)
        self.position.y += self.speed_vector.y * delta_time + ((g * (delta_time ** 2)) / 2)
        self.speed_vector.y += g * delta_time

        for collider in self.colliders:
            collider.update_position()

        self.update_animation(delta_time)

    def update_animation(self, delta_time):
        if not self.animation_manager or not self.current_animation:
            return

        if self.is_attacking:
            self.animation_timer += delta_time
            animation_speed = self.animation_speeds.get(self.current_animation.type, 0.1)
            if self.animation_timer >= animation_speed:
                self.animation_timer -= animation_speed
                self.current_frame += 1
                if self.current_frame >= len(self.current_animation.animation):
                    self.current_frame = 0
                    self.is_attacking = False
                    self.set_animation(AnimationType.IDLE1)
                self.update_image()
            return

        if not self.on_ground:
            if self.speed_vector.y < 0:
                self.set_animation(AnimationType.JUMP)
            else:
                self.set_animation(AnimationType.FALLING)
        else:
            if abs(self.speed_vector.x) > 0.1:
                self.set_animation(AnimationType.WALK)
            else:
                self.set_animation(AnimationType.IDLE1)

        self.animation_timer += delta_time
        animation_speed = self.animation_speeds.get(self.current_animation.type, 0.1)
        if self.animation_timer >= animation_speed:
            self.animation_timer -= animation_speed
            if self.current_animation.type == AnimationType.JUMP:
                self.current_frame = min(self.current_frame + 1, len(self.current_animation.animation) - 1)
            else:
                self.current_frame = (self.current_frame + 1) % len(self.current_animation.animation)
            self.update_image()
