"""  Classe para as armadilhas do jogo, que são entidades estáticas que causam dano ou atrapalham o jogador, 
como espinhos, barris explosivos, ou portas que podem ser atacadas	"""

from objects.entity_with_animation import EntityWithAnimation


class Hazard(EntityWithAnimation):
    def __init__(self, position, size, sprite=(255, 255, 255), solid=True, collide_damage=5, invincible=False,  health=10, attackable=False, attack_speed=0,  damage=10):
        
        super().__init__(position, size, sprite=sprite, solid=solid,
                         collide_damage=collide_damage, invincible=invincible, health=health, attackable=attackable)
        self.damage = damage
        self.attack_speed = attack_speed

        
