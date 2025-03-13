import pygame


class Object(pygame.sprite.Sprite):

    def __init__(self, x, y, width, height, health=100, attackable=False, solid=False, invicible=False, color=(255, 255, 255)):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.health = health
        self.attackable = attackable
        self.invincible = invicible
        self.solid = solid
        self.color = color

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
