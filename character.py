
from entity import Entity


class Character(Entity):

    def __init__(self, x, y, width, height, collide_damage=False, speed, gravity):
        super().__init__(x, y, width, height, )
        self.speed = speed
        self.gravity = gravity
        self.velocity_x = 0
        self.velocity_y = 0
        self.attack_speed = 0
        self.collide_damage = collide_damage
        
