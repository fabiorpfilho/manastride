import pygame

# /*
# Classe básica para todos os objetos do jogo
#  */
class Object(pygame.sprite.Sprite):

    def __init__(self, x, y, width, height, color=(255, 255, 255), solid=False):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.solid = solid

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
