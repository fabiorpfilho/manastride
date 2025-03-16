from objects.entity import Entity
import pygame

# /*
# Classe para os personagens, que são entidades dinamicas/moveis, com inimigos, npcs, e o jogador
#  */

class Character(Entity):
    def __init__(self, x, y, width, height, color=(0, 255, 0),  solid=True, collide_damage=5, invincible=False, health=100, attackable=True, attack_speed=0, damage=10,  speed=3, gravity=1, velocity_x=0, velocity_y=0, jump_power=10):
      
        super().__init__(x, y, width, height, color=color, solid=solid,collide_damage=collide_damage, invincible=invincible, health=health, attackable=attackable)
        self.attack_speed = attack_speed
        self.damage = damage
        self.speed = speed  
        self.gravity = gravity  
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.jump_power = jump_power
        self.on_ground = False
        
    def update(self, platforms, screen_width):
        keys = pygame.key.get_pressed()

        self.velocity_x = -self.speed if keys[pygame.K_LEFT] else self.speed if keys[pygame.K_RIGHT] else 0

        self.rect.x += self.velocity_x
        
        if self.rect.left < 0:
          self.rect.left = 0
        if self.rect.right > screen_width:
          self.rect.right = screen_width

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:
                    self.rect.right = platform.rect.left
                elif self.velocity_x < 0:
                    self.rect.left = platform.rect.right

        self.velocity_y += self.gravity  

     
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = -self.jump_power
            self.on_ground = False

        self.rect.y += self.velocity_y


        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:  
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:  
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0

