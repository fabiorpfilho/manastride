
from objects.dynamic_objects.character import Character
import pygame


class Player(Character):
    def __init__(self, position, size, sprite=(0, 255, 0), 
                 collide_damage=5, invincible=False, health=100, attackable=True, 
                 attack_speed=0, damage=10, speed=8, gravity=0.5, movement=(0, 0), jump_power=40):
        
        super().__init__(position, size, sprite, collide_damage, invincible, health,
                         attackable, attack_speed, damage, speed, gravity, movement, jump_power)
        
        self.add_collider((0, 0), self.size, type='body', solid=True)
        
    def movement_update(self, delta_time):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.position.x += -self.speed * delta_time
        elif keys[pygame.K_RIGHT]: 
            self.position.x += self.speed * delta_time
        
        if keys[pygame.K_SPACE] and self.on_ground:
            self.movement.y += -self.jump_power * delta_time
            self.on_ground = False
        
        self.movement.y += self.gravity * delta_time
        self.position.y += self.movement.y

        for collider in self.colliders:
            collider.update_position()
    
