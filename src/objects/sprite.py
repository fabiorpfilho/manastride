import pygame

class Sprite:
    def __init__(self, image):
        self.image = image
        self.offset_x = 0  # Offset para alinhar o centro do corpo
        self.offset_y = 0  # Offset para alinhar a base