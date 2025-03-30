#Classe que será responsável por gerenciar as colisões entre objetos
import pygame

class CollisionManager:
    def __init__(self, player, platforms, screen_width):
        self.player = player
        self.platforms = platforms
        self.screen_width = screen_width 

    def update(self):
        self._handle_horizontal_collisions()
        self._handle_vertical_collisions()

    def _handle_horizontal_collisions(self):
        self.player.rect.x += self.player.movement.x

        if self.player.rect.left < 0:
            self.player.rect.left = 0
        if self.player.rect.right > self.screen_width: 
            self.player.rect.right = self.screen_width

        for platform in self.platforms:
            if self.player.rect.colliderect(platform.rect):
                if self.player.movement.x > 0:
                    self.player.rect.right = platform.rect.left
                elif self.player.movement.x < 0:
                    self.player.rect.left = platform.rect.right

    def _handle_vertical_collisions(self):
        self.player.movement.y += self.player.gravity
        self.player.rect.y += self.player.movement.y

        self.player.on_ground = False
        for platform in self.platforms:
            if self.player.rect.colliderect(platform.rect):
                if self.player.movement.y > 0:
                    self.player.rect.bottom = platform.rect.top
                    self.player.movement.y = 0
                    self.player.on_ground = True
                elif self.player.movement.y < 0:
                    self.player.rect.top = platform.rect.bottom
                    self.player.movement.y = 0
