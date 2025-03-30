
from objects.dynamic_objects.character import Character
import pygame


class Player(Character):
    def __init__(self, position, size, sprite=(0, 255, 0), solid=True, collide_damage=5, invincible=False, health=100, attackable=True, attack_speed=0, damage=10, speed=3, gravity=1, movement=(0, 0), jump_power=10):
        super().__init__(position, size, sprite, solid, collide_damage, invincible, health,
                         attackable, attack_speed, damage, speed, gravity, movement, jump_power)
        
    def movement_update(self):
        keys = pygame.key.get_pressed()
        self.movement.x = -self.speed if keys[pygame.K_LEFT] else \
            self.speed if keys[pygame.K_RIGHT] else 0

        if keys[pygame.K_SPACE] and self.on_ground:
            self.movement.y = -self.jump_power
            self.on_ground = False
