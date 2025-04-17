
from objects.dynamic_objects.character import Character
from config import SPEED, JUMP_SPEED, GRAVITY
import pygame


class Player(Character):
    def __init__(self, position, size, sprite=(0, 255, 0), 
                 collide_damage=5, invincible=False, health=100, attackable=True, 
                 attack_speed=0, damage=10, speed=0, gravity=0, movement=(0, 0), jump_speed=0):
        
        super().__init__(position, size, sprite, collide_damage, invincible, health,
                         attackable, attack_speed, damage, speed, gravity, movement, jump_speed)
        
        self.add_collider((0, 0), self.size, type='body', solid=True)
        
    def movement_update(self, delta_time):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.position.x += -(self.speed + SPEED) * delta_time
        elif keys[pygame.K_RIGHT]: 
            self.position.x += (self.speed + SPEED) * delta_time
        
        if keys[pygame.K_SPACE] and self.on_ground:
            self.movement.y += -(self.jump_speed + JUMP_SPEED) 
            self.on_ground = False
        
        g = self.gravity + GRAVITY
        
        self.position.y += self.movement.y * delta_time + ( (g * (delta_time ** 2)) / 2)
        self.movement.y += g * delta_time
        for collider in self.colliders:
            collider.update_position()
        #MUDAR O MOVEMENT PARA speed_vector

