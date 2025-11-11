
from ui.ui import Ui
import pygame


class Score(Ui):
    def __init__(self, screen):
        super().__init__(screen)
        self.font = pygame.font.SysFont('arial', 24)

    def draw(self, score_value):
        score_text = self.font.render(f'Pontuação: {score_value}', True, (255, 255, 255))
        score_rect = score_text.get_rect(topright=(self.screen.get_width() - 10, 10))
        self.screen.blit(score_text, score_rect)
        # In the future, replace with image-based rendering when resources are ready