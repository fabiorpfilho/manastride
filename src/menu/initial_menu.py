import pygame
from config import HIGHLIGHT_COLOR, BUTTON_COLOR

class InitialMenu:
    def __init__(self, menu):
        self.menu = menu
        self.width = menu.width
        self.height = menu.height
        self.title_font = pygame.font.SysFont('arial', 72, bold=True)  # Fonte grande e em negrito para o título
        self.controls_font = pygame.font.SysFont('arial', 28)  # Fonte maior para controles
        self.button_font = pygame.font.SysFont('arial', 36, bold=True)  # Fonte para botão
        self.controls_text = [
            "Controles:",
            "Movimentação - Setas",
            "Pulo - Espaço",
            "Ataque Corpo a Corpo - Z",
            "Projétil - 1",
            "Avanço - 2",
            "Escudo - 3",
            "Pausar - Esc"
        ]

    def draw(self, mouse_pos, is_initial=True):
        """Desenha o menu inicial ou de controles com base no parâmetro is_initial."""
        # Gradiente de fundo
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for y in range(self.height):
            alpha = 180 + (y / self.height) * 50  # Gradiente de 180 a 230 de opacidade
            overlay.fill((0, 0, 0, int(alpha)), (0, y, self.width, 1))
        self.menu.screen.blit(overlay, (0, 0))

        # Título
        title = "Manastride" if is_initial else "Controles"
        title_text = self.title_font.render(title, True, (255, 255, 255))
        title_shadow = self.title_font.render(title, True, (50, 50, 50))  # Sombra cinza
        title_rect = title_text.get_rect(center=(self.width // 2, self.height // 2 - 200))
        title_shadow_rect = title_rect.copy()
        title_shadow_rect.move_ip(3, 3)  # Deslocamento da sombra
        self.menu.screen.blit(title_shadow, title_shadow_rect)
        self.menu.screen.blit(title_text, title_rect)

        # Texto dos controles (exclui "Controles:" no menu de controles)
        start_index = 0 if is_initial else 1  # Pula a primeira linha ("Controles:") se não for inicial
        for i, line in enumerate(self.controls_text[start_index:]):
            text = self.controls_font.render(line, True, (255, 255, 255))
            shadow = self.controls_font.render(line, True, (50, 50, 50))  # Sombra cinza
            text_rect = text.get_rect(center=(self.width // 2, self.height // 2 - 50 + i * 40))
            shadow_rect = text_rect.copy()
            shadow_rect.move_ip(2, 2)  # Deslocamento da sombra
            self.menu.screen.blit(shadow, shadow_rect)
            self.menu.screen.blit(text, text_rect)

        # Botão "Iniciar Jogo" (menu inicial) ou "Voltar" (menu de controles)
        button_text = "Iniciar Jogo (Enter)" if is_initial else "Voltar (Enter/Esc)"
        button_y = self.height // 2 + 300  # Mesma posição para ambos os menus
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

    def handle_input(self, events, mouse_pos, running, is_initial=True):
        """Processa entrada para o menu inicial ou de controles."""
        start_game = False
        for event in events:
            if event.type == pygame.KEYDOWN:
                if is_initial and event.key == pygame.K_RETURN:
                    print("Iniciar jogo selecionado via tecla Enter")
                    start_game = True  # Inicia o jogo
                elif event.key == pygame.K_ESCAPE:
                    if is_initial:
                        print("Sair do jogo selecionado via tecla Esc")
                        running = False  # Sai do jogo
                    else:
                        print("Voltando ao menu principal via tecla Esc")
                        self.menu.current_menu = 'main'  # Volta ao menu principal
                        self.menu.main_menu.selected_item = 0
                elif not is_initial and event.key == pygame.K_RETURN:
                    print("Voltando ao menu principal via tecla Enter")
                    self.menu.current_menu = 'main'  # Volta ao menu principal
                    self.menu.main_menu.selected_item = 0
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                print("Clique do mouse detectado no menu")
                button_text = "Iniciar Jogo (Enter)" if is_initial else "Voltar (Enter/Esc)"
                button_rect = self.button_font.render(button_text, True, (255, 255, 255)).get_rect(
                    center=(self.width // 2, self.height // 2 + 300))
                if button_rect.collidepoint(mouse_pos):
                    print("Clique do mouse dentro do retângulo do botão")
                    if is_initial:
                        print("Iniciar jogo selecionado via clique do mouse")
                        start_game = True
                    else:
                        print("Voltando ao menu principal via clique do mouse")
                        self.menu.current_menu = 'main'
                        self.menu.main_menu.selected_item = 0
        return start_game, running