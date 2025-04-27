from objects.entity_with_animation import EntityWithAnimation
from pygame.math import Vector2
# /*
# Classe para os personagens, que são entidades dinamicas/moveis, como inimigos e npcs
#  */


class Character(EntityWithAnimation):
    def __init__(self, position, size, sprite=(0, 255, 0), collide_damage=5, invincible=False, health=100, attackable=True, attack_speed=0, 
                 damage=10,  speed=3, gravity=1, speed_vector=(0, 0), jump_speed=10):
      
        super().__init__(position, size, sprite=sprite)
        self.attack_speed = attack_speed
        self.damage = damage
        self.speed = speed  
        self.gravity = gravity  
        self.speed_vector = Vector2(speed_vector)
        self.jump_speed = jump_speed
        self.on_ground = False
        self.collide_damage = collide_damage
        self.invincible = invincible
        self.health = health
        self.attackable = attackable
        