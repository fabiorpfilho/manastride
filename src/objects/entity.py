from objects.base_object import Object

# /*
# Classe para as entidades do jogo, que são objetos que podem ser interagidos e/ou atacados
#  */
class Entity(Object):
    def __init__(self, x, y, width, height, health=100,  color=(255, 255, 255), solid=False, collide_damage=5, attackable=False, invincible=False):
        super().__init__(x, y, width, height, color, solid) 
        self.collide_damage = collide_damage
        self.invincible = invincible
        self.health = health
        self.attackable = attackable
    
