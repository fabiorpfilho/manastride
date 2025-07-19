from objects.dynamic_objects.character import Character
from config import SPEED, JUMP_SPEED, GRAVITY
import pygame
from objects.animation_type import AnimationType
from typing import Optional

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
        self.animation_speed = 0.1  # Tempo em segundos por frame
        self.facing_right = True
        self.add_collider((0, 0), self.size, type='body', solid=True)
        self.spell_cooldown = 0.5
        self.spell_cooldown_timer = 0
        
        # Carregar animação de corrida, se animation_manager estiver presente
        if self.animation_manager:
            self.animation_manager.load_sprites_from_folder("assets/run", AnimationType.WALK)
            if not self.animation_manager.animationList:
                print("Erro: Nenhuma animação carregada em assets/run_teste")
            self.set_animation(AnimationType.WALK)

    def set_animation(self, animation_type: AnimationType):
        """Define a animação atual com base no tipo."""
        if not self.animation_manager:
            print("Aviso: Nenhum AnimationManager fornecido")
            return
        for animation in self.animation_manager.animationList:
            if animation.type == animation_type:
                if self.current_animation != animation:  # Evita reinicializar desnecessariamente
                    self.current_animation = animation
                    self.current_frame = 0
                    self.animation_timer = 0
                    self.update_image()
                break
        else:
            print(f"Aviso: Animação {animation_type} não encontrada")

    def update_image(self):
        """Atualiza a imagem do jogador com o frame atual da animação."""
        if self.current_animation and self.current_animation.animation:
            sprite = self.current_animation.animation[self.current_frame].image
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)
            self.image = sprite
            self.rect = self.image.get_rect(topleft=(self.position.x, self.position.y))
        else:
            print("Aviso: Nenhuma animação disponível, usando sprite padrão")
            self.image.fill(self.sprite)  # Usa a cor padrão se não houver animação

    def movement_update(self, delta_time):
        keys = pygame.key.get_pressed()
        
        if self.spell_cooldown_timer > 0:
            self.spell_cooldown_timer -= delta_time
        
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

        g = (self.gravity + GRAVITY)
        self.position.y += self.speed_vector.y * delta_time + ((g * (delta_time ** 2)) / 2)
        self.speed_vector.y += g * delta_time

        for collider in self.colliders:
            collider.update_position()

        self.update_animation(delta_time)

    def update_animation(self, delta_time):
        """Atualiza o frame da animação com base no movimento e no tempo."""
        if not self.animation_manager or not self.current_animation:
            return  # Sem AnimationManager ou animação, mantém a imagem padrão
        
        if abs(self.speed_vector.x) > 0.1:
            self.set_animation(AnimationType.WALK)
            self.animation_timer += delta_time
            if self.animation_timer >= self.animation_speed:
                self.animation_timer -= self.animation_speed  # Subtrai o tempo acumulado
                self.current_frame = (self.current_frame + 1) % len(self.current_animation.animation)
                print(f"Frame atual: {self.current_frame}, Total de frames: {len(self.current_animation.animation)}")
                self.update_image()
        else:
            self.current_frame = 0
            self.update_image()