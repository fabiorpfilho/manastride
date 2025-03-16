from objects.entity import Entity;

# /*
# Classe para as armadilhas do jogo, que são entidades estáticas que causam dano ou atrapalham o jogador, como espinhos, barris explosivos, ou portas que podem ser atacadas
#  */

class Hazard(Entity):
    def __init__(self, x, y, width, height, color=(255, 255, 255), solid=True, collide_damage=5, invincible=False,  health = 10, attackable=False, attack_speed=0,  damage=10):
        
        super().__init__(x, y, width, height, color=color, solid=solid, collide_damage=collide_damage, invincible=invincible, health=health, attackable=attackable)
        self.damage = damage
        self.attack_speed = attack_speed

        
