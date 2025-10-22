from objects.dynamic_objects.character import Character
from config import SPEED, GRAVITY
import pygame
from typing import Optional
from objects.animation_manager import AnimationManager
import json
import math

class Drone(Character):
    def __init__(self, position, size, sprite=(255, 0, 0), invincible=False, 
                 max_health=30, attackable=True, damage=15, 
                 custom_speed=None, gravity=0, speed_vector=(0, 0), jump_speed=0,
                 custom_max_health=None, custom_damage=None, id=None):
        # Define speed com base em custom_speed ou usa o valor padrão
        speed = custom_speed if custom_speed is not None else SPEED - 100
        # Define max_health com base em custom_max_health ou usa o valor padrão
        max_health = custom_max_health if custom_max_health is not None else max_health
        # Define damage com base em custom_damage ou usa o valor padrão
        damage = custom_damage if custom_damage is not None else damage
        
        super().__init__(position, size, sprite, invincible, max_health,
                         attackable, damage, speed, gravity, speed_vector, jump_speed)
        self.id = id
        self.health = max_health
        self.tag = "enemy_npc"
        self.current_animation = None
        self.current_frame = 0
        self.is_attacking = False
        self.attack_cooldown = 0.3
        self.marked_for_removal = False  # Para remoção após morte
        self.animation_speeds = {
            self.animation_manager.AnimationType.WALK: 0.1,
        }
        self.facing_right = True
        self.add_collider((0, 0), self.size, type='body', active=True)
        self.add_collider((0, 0), self.size, type='hurt_box', active=True)
        self.add_collider((0, 0), self.size, type='attack_box', active=True)
        print(f"Drone criado em: {position} com ID: {self.id}")
        # Levitation parameters
        # self.base_y = position[1]
        # self.levitation_amplitude = 20
        # self.levitation_speed = 2  # Frequency
        # self.levitation_timer = 0
        
        if self.animation_manager:
            self.animation_manager.load_animations_from_json(
                self.size,
                image_path="assets/drone_bot/drone_bot.png",
                json_path="assets/drone_bot/drone_bot.json"
            )
            print(f"Animações do drone bot carregadas: {(self.animation_manager.animationList)}")
            if not self.animation_manager.animationList:
                print("Erro: Nenhuma animação do drone bot carregada")
            else:
                self.set_animation(self.animation_manager.AnimationType.WALK)


    def update(self, delta_time, platforms):
        # No gravity for flying drone
        
        # Update levitation timer
        self.levitation_timer += delta_time

        # Set movement direction based on facing, unless attacking
        if not self.is_attacking:
            self.speed_vector.x = self.speed if self.facing_right else -self.speed
        
        
        # Update position
        self.position.x += self.speed_vector.x * delta_time
        
        # Apply levitation if not attacking
        if not self.is_attacking:
            levitation_offset = math.sin(self.levitation_timer * self.levitation_speed) * self.levitation_amplitude
            self.position.y = self.base_y + levitation_offset

        self.update_animation(delta_time)
        self.sync_position()

    def update_animation(self, delta_time):
        if not self.animation_manager or not self.current_animation:
            # Use default image if no animation
            self.image = self.default_image
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
                    self.current_animation = None
                    self.image = self.default_image
                else:
                    self.update_image()
        else:
            self.image = self.default_image

    def set_animation(self, animation_type):
        if not self.animation_manager:
            print("Aviso: Nenhum AnimationManager fornecido")
            return
        for animation in self.animation_manager.animationList:
            if animation.type == animation_type:
                if self.current_animation != animation:
                    self.current_animation = animation
                    self.current_frame = 0
                    self.animation_timer = 0
                    self.is_attacking = (animation_type == self.animation_manager.AnimationType.ATTACK1)
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
            self.image = self.default_image


    def handle_damage(self, enemy_damage, damage_source_position=None):
        if self.health <= 0:
            return  # Já morreu, ignora

        self.health -= enemy_damage
        print(f"Drone sofreu {enemy_damage} de dano. Vida restante: {self.health}")

        if self.health <= 0:
            pygame.mixer.Sound("assets/audio/soundEffects/enemy_death.mp3").play()
            self.marked_for_removal = True
            self.colliders[2].active = False
        else:
            # No hurt animation, just apply knockback
            knockback_strength = 150  # Adjust as needed
            direction = 1 if damage_source_position and damage_source_position.x > self.position.x else -1
            self.speed_vector.x = direction * knockback_strength
            self.speed_vector.y = -150  # Slight upward knockback