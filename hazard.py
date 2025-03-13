from entity import Entity;


class Hazard(Entity):

    def __init__(self, x, y, width, height, collide_damage=False, invicible = False):
        super().__init__(x, y, width, height)
        self.attack_speed = 0
        self.damage = 10
        self.collide_damage = collide_damage
        self.solid = True;
        self.invicible = invicible
        
