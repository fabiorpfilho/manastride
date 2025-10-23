import pygame
from config import HIGHLIGHT_COLOR, BUTTON_COLOR

class CreditMenu:
    def __init__(self, menu):
        self.menu = menu
        self.width = menu.width
        self.height = menu.height
        self.title_font = pygame.font.SysFont('arial', 72, bold=True)  # Fonte grande e em negrito para o título
        self.credits_font = pygame.font.SysFont('arial', 28)  # Fonte para os créditos
        self.button_font = pygame.font.SysFont('arial', 36, bold=True)  # Fonte para botão
        self.credits_text = [
            "Créditos:",
            "Desenvolvimento: Fabio Roberto Pereira Filho",  
            "Orientação: Eduardo Henrique Molina Da Cruz",  
            "Arte: Recursos públicos do itch.io e outras fontes",
            "Agradecimentos: Comunidade de jogadores e desenvolvedores"
        ]

    def draw(self, mouse_pos):
        """Desenha o menu de créditos."""
        # Título
        title = "Créditos"
        title_text = self.title_font.render(title, True, (255, 255, 255))
        title_shadow = self.title_font.render(title, True, (50, 50, 50))  # Sombra cinza
        title_rect = title_text.get_rect(center=(self.width // 2, self.height // 2 - 200))
        title_shadow_rect = title_rect.copy()
        title_shadow_rect.move_ip(3, 3)  # Deslocamento da sombra
        self.menu.screen.blit(title_shadow, title_shadow_rect)
        self.menu.screen.blit(title_text, title_rect)

        # Texto dos créditos
        for i, line in enumerate(self.credits_text[1:]):  # Pula a primeira linha ("Créditos:")
            text = self.credits_font.render(line, True, (255, 255, 255))
            shadow = self.credits_font.render(line, True, (50, 50, 50))  # Sombra cinza
            text_rect = text.get_rect(center=(self.width // 2, self.height // 2 - 50 + i * 40))
            shadow_rect = text_rect.copy()
            shadow_rect.move_ip(2, 2)  # Deslocamento da sombra
            self.menu.screen.blit(shadow, shadow_rect)
            self.menu.screen.blit(text, text_rect)

        # Botão "Voltar"
        button_text = "Voltar (Enter/Esc)"
        button_y = self.height // 2 + 300
        button_color = (255, 255, 0) if self.button_font.render(button_text, True, BUTTON_COLOR).get_rect(
            center=(self.width // 2, button_y)).collidepoint(mouse_pos) else BUTTON_COLOR
        button = self.button_font.render(button_text, True, button_color)
        button_rect = button.get_rect(center=(self.width // 2, button_y))
        
        # Fundo do botão com borda
        button_bg_rect = button_rect.inflate(20, 10)  # Expande o retângulo
        bg_color = (50, 50, 100) if button_color == BUTTON_COLOR else HIGHLIGHT_COLOR
        pygame.draw.rect(self.menu.screen, bg_color, button_bg_rect, border_radius=10)
        pygame.draw.rect(self.menu.screen, button_color, button_bg_rect, 2, border_radius=10)  # Borda
        self.menu.screen.blit(button, button_rect)

        return button_rect  # Retorna o retângulo do botão para uso no handle_input

    def handle_input(self, events, mouse_pos, running):
        """Processa entrada para o menu de créditos."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                print("Clique do mouse detectado no menu de créditos")
                button_rect = self.button_font.render("Voltar (Enter/Esc)", True, (255, 255, 255)).get_rect(
                    center=(self.width // 2, self.height // 2 + 300))
                if button_rect.collidepoint(mouse_pos):
                    print("Voltando ao menu principal via clique do mouse")
                    self.menu.current_menu = 'main'
                    self.menu.main_menu.selected_item = 0
        return running