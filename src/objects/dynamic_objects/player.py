
from objects.dynamic_objects.character import Character
from config import SPEED, JUMP_POWER, GRAVITY
import pygame


class Player(Character):
    def __init__(self, position, size, sprite=(0, 255, 0), 
                 collide_damage=5, invincible=False, health=100, attackable=True, 
                 attack_speed=0, damage=10, speed=0, gravity=0, movement=(0, 0), jump_power=0):
        
        super().__init__(position, size, sprite, collide_damage, invincible, health,
                         attackable, attack_speed, damage, speed, gravity, movement, jump_power)
        
        self.add_collider((0, 0), self.size, type='body', solid=True)
        
    def movement_update(self, delta_time):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.position.x += -(self.speed + SPEED) * delta_time
        elif keys[pygame.K_RIGHT]: 
            self.position.x += (self.speed + SPEED) * delta_time
        
        if keys[pygame.K_SPACE] and self.on_ground:
            self.movement.y += -(self.jump_power + JUMP_POWER) 
            self.on_ground = False
            print(f"[PULO] delta_time={delta_time:.4f} | força={(self.jump_power + JUMP_POWER):.2f} | movimento_y={self.movement.y:.2f}")
        
        self.movement.y += (self.gravity + GRAVITY) * delta_time
        self.position.y += self.movement.y

        for collider in self.colliders:
            collider.update_position()
    