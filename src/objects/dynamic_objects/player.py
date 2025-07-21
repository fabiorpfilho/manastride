from objects.dynamic_objects.character import Character
from config import SPEED, JUMP_SPEED, GRAVITY
import pygame
from objects.animation_type import AnimationType
from typing import Optional
from objects.animation_manager import AnimationManager

class Player(Character):
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
        self.is_casting = False
        self.is_attacking = False
        self.current_attack = None
        self.attack_combo_timer = 0
        self.attack_combo_timeout = 0.5
        self.attack_cooldown = 0.3  # Cooldown entre ataques
        self.attack_cooldown_timer = 0  # Temporizador do cooldown de ataque

        self.animation_speeds = {
            AnimationType.IDLE1: 0.35,
            AnimationType.WALK: 0.1,
            AnimationType.JUMP: 0.1,
            AnimationType.FALLING: 0.1,
            AnimationType.CASTING: 0.1,
            AnimationType.ATTACK1: 0.1,
            AnimationType.ATTACK2: 0.1,
            AnimationType.ATTACK3: 0.1
        }

        self.facing_right = True
        self.add_collider((0, 0), self.size, type='body', solid=True)
        self.spell_cooldown = 0.5
        self.spell_cooldown_timer = 0
        
        if self.animation_manager:
            self.animation_manager.load_sprites_from_folder("assets/idle1", AnimationType.IDLE1)
            self.animation_manager.load_sprites_from_folder("assets/run", AnimationType.WALK)
            self.animation_manager.load_sprites_from_folder("assets/jump", AnimationType.JUMP)
            self.animation_manager.load_sprites_from_folder("assets/fall", AnimationType.FALLING)
            self.animation_manager.load_sprites_from_folder("assets/casting", AnimationType.CASTING)
            self.animation_manager.load_sprites_from_folder("assets/attack1", AnimationType.ATTACK1)
            self.animation_manager.load_sprites_from_folder("assets/attack2", AnimationType.ATTACK2)
            self.animation_manager.load_sprites_from_folder("assets/attack3", AnimationType.ATTACK3)
            if not self.animation_manager.animationList:
                print("Erro: Nenhuma animação carregada")
            self.set_animation(AnimationType.IDLE1)

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
                    if animation_type == AnimationType.CASTING:
                        self.is_casting = True
                        self.is_attacking = False
                    elif animation_type in (AnimationType.ATTACK1, AnimationType.ATTACK2, AnimationType.ATTACK3):
                        self.is_attacking = True
                        self.is_casting = False
                        self.current_attack = animation_type
                        self.attack_combo_timer = self.attack_combo_timeout
                    else:
                        self.is_casting = False
                        self.is_attacking = False
                        self.current_attack = None
                    self.update_image()
                break
        else:
            print(f"Aviso: Animação {animation_type} não encontrada")

    def update_image(self):
        if self.current_animation and self.current_animation.animation:
            sprite = self.current_animation.animation[self.current_frame].image
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)
            self.image = sprite
            self.rect = self.image.get_rect(topleft=(self.position.x, self.position.y))
        else:
            print("Aviso: Nenhuma animação disponível, usando sprite padrão")
            self.image.fill(self.sprite)

    def movement_update(self, delta_time):
        keys = pygame.key.get_pressed()

        # Atualizar cooldowns
        if self.spell_cooldown_timer > 0:
            self.spell_cooldown_timer -= delta_time
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= delta_time

        # Atualizar timer de combo
        if self.attack_combo_timer > 0:
            self.attack_combo_timer -= delta_time
            if self.attack_combo_timer <= 0:
                self.current_attack = None

        acceleration = (self.speed + SPEED)
        if keys[pygame.K_LEFT]:
            self.speed_vector.x = -acceleration
            self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            self.speed_vector.x = acceleration
            self.facing_right = True
        else:
            self.speed_vector.x *= 0.8
            if abs(self.speed_vector.x) < 0.1:
                self.speed_vector.x = 0

        self.position.x += self.speed_vector.x * delta_time

        if keys[pygame.K_SPACE] and self.on_ground:
            self.speed_vector.y += -(self.jump_speed + JUMP_SPEED)
            self.on_ground = False

        # Ataque corpo a corpo
        if keys[pygame.K_z] and not self.is_casting and self.attack_cooldown_timer <= 0:
            if not self.is_attacking:
                self.set_animation(AnimationType.ATTACK1)
            elif self.current_attack == AnimationType.ATTACK1 and self.attack_combo_timer > 0:
                self.set_animation(AnimationType.ATTACK2)
            elif self.current_attack == AnimationType.ATTACK2 and self.attack_combo_timer > 0:
                self.set_animation(AnimationType.ATTACK3)
            elif self.current_attack == AnimationType.ATTACK3 and self.attack_combo_timer > 0:
                self.set_animation(AnimationType.ATTACK1)
            self.attack_cooldown_timer = self.attack_cooldown

        key_to_index = {
            pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3,
            pygame.K_4: 4, pygame.K_5: 5, pygame.K_6: 6,
            pygame.K_7: 7, pygame.K_8: 8, pygame.K_9: 9
        }

        for key, index in key_to_index.items():
            if keys[key] and self.spell_cooldown_timer <= 0:
                if hasattr(self, 'spell_system'):
                    direction = 1 if self.facing_right else -1
                    self.spell_system.cast_spell(index, direction)
                    self.spell_cooldown_timer = self.spell_cooldown
                    self.set_animation(AnimationType.CASTING)

        g = (self.gravity + GRAVITY)
        self.position.y += self.speed_vector.y * delta_time + ((g * (delta_time ** 2)) / 2)
        self.speed_vector.y += g * delta_time

        for collider in self.colliders:
            collider.update_position()

        self.update_animation(delta_time)

    def update_animation(self, delta_time):
        if not self.animation_manager or not self.current_animation:
            return

        if self.is_casting or self.is_attacking:
            self.animation_timer += delta_time
            animation_speed = self.animation_speeds.get(self.current_animation.type, 0.1)
            if self.animation_timer >= animation_speed:
                self.animation_timer -= animation_speed
                self.current_frame += 1
                if self.current_frame >= len(self.current_animation.animation):
                    self.current_frame = 0
                    self.is_casting = False
                    self.is_attacking = False
                    if self.current_attack == AnimationType.ATTACK3:
                        self.current_attack = None
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
