
from objects.dynamic_objects.character import Character
from config import SPEED, JUMP_SPEED, GRAVITY
import pygame


class Player(Character):
    def __init__(self, position, size, sprite=(0, 255, 0), 
                 collide_damage=5, invincible=False, health=100, attackable=True, 
                 attack_speed=0, damage=10, speed=0, gravity=0, speed_vector=(0, 0), jump_speed=0, ):
        
        super().__init__(position, size, sprite, collide_damage, invincible, health,
                         attackable, attack_speed, damage, speed, gravity, speed_vector, jump_speed)
        
        self.add_collider((0, 0), self.size, type='body', solid=True)
        self.spell_cooldown = 0.5  # Cooldown de 0.5 segundos entre feitiços
        self.spell_cooldown_timer = 0
        self.facing_right = True
        
    def movement_update(self, delta_time):
        keys = pygame.key.get_pressed()
        
        if self.spell_cooldown_timer > 0:
            self.spell_cooldown_timer -= delta_time
        
        
        if keys[pygame.K_LEFT]:
            self.position.x += -(self.speed + SPEED) * delta_time
            self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            self.position.x += (self.speed + SPEED) * delta_time
            self.facing_right = True
        
        if keys[pygame.K_SPACE] and self.on_ground:
            self.speed_vector.y += -(self.jump_speed + JUMP_SPEED)
            self.on_ground = False

        key_to_index = {
            pygame.K_1: 1,
            pygame.K_2: 2,
            pygame.K_3: 3,
            pygame.K_4: 4,
            pygame.K_5: 5,
            pygame.K_6: 6,
            pygame.K_7: 7,
            pygame.K_8: 8,
            pygame.K_9: 9
        }
        for key, index in key_to_index.items():
            if keys[key] and self.spell_cooldown_timer <= 0:
                if hasattr(self, 'spell_system'):
                    direction = 1 if self.facing_right else -1  # 1 para direita, -1 para esquerda
                    self.spell_system.cast_spell(index, direction)
                    self.spell_cooldown_timer = self.spell_cooldown

        g = self.gravity + GRAVITY
        self.position.y += self.speed_vector.y * delta_time + ((g * (delta_time ** 2)) / 2)
        self.speed_vector.y += g * delta_time
        for collider in self.colliders:
            collider.update_position()
            
        #MUDAR O speed_vector PARA speed_vector

