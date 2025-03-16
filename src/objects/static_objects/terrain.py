from objects.base_object import Object;

# /*
# Classe para o terreno do jogo, são entidades sólidas que não podem ser atacadas	
#  */

class Terrain(Object):
    def __init__(self, x, y, width, height, color=(100, 100, 100), solid=True, texture=None,  friction=1.0, damage=0):
        super().__init__(x, y, width, height, color=color, solid=solid)
        self.texture = texture  # Pode ser uma imagem carregada
        self.friction = friction  # Define se o terreno afeta a movimentação
        self.damage = damage  # Dano causado ao jogador ao tocar

    #     if self.texture:
    #         self.image = pygame.image.load(self.texture)
    #         self.image = pygame.transform.scale(self.image, (self.width, self.height))

    # def apply_effect(self, entity):
    #     """Aplica efeitos ao jogador ou outros objetos"""
    #     if self.damage > 0:
    #         entity.take_damage(self.damage)
    #     entity.speed *= self.friction
