""" Classe para o terreno do jogo, são entidades sólidas que não podem ser atacadas """
from objects.entity_with_sprite import EntityWithSprite
from pygame.math import Vector2
import pygame


class Terrain(EntityWithSprite):
    def __init__(self, position, size, image=None):
        super().__init__(position, size, image)
        self.add_collider((0, 0), (self.size.x, self.size.y), type='terrain', active=True)
        # Growth animation attributes
        self.is_growing = False  # Flag to indicate if growth animation is active
        self.grow_time = 0.0  # Time elapsed for growth animation
        self.grow_duration = 1.0  # Duration of the growth animation (in seconds)
        self.final_height = self.size.y  # Final height of the terrain
        self.grow_height = self.size.y  # Current height, defaults to full height
        self.base_image = self.image  # Store base image for scaling

    def update(self, delta_time):
        if self.is_growing:
            self.grow_time += delta_time
            # Linear interpolation for height
            progress = min(self.grow_time / self.grow_duration, 1.0)
            self.grow_height = self.final_height * progress
            # Update the image and rect for the animation
            self.image = pygame.transform.scale(self.base_image, (int(self.size.x), int(self.grow_height)))
            self.rect = self.image.get_rect(bottomleft=(self.position.x, self.position.y + self.final_height))
            # Update collider size to match current height
            self.colliders[0].size = Vector2(self.size.x, self.grow_height)
            self.colliders[0].rect = pygame.Rect(self.position.x, self.position.y + self.final_height - self.grow_height, self.size.x, self.grow_height)
            if progress >= 1.0:
                self.is_growing = False  # Stop animation when complete