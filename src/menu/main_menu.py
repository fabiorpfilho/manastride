import pygame
from config import HIGHLIGHT_COLOR, BUTTON_COLOR
class MainMenu:
    def __init__(self, menu):
        self.menu = menu
        self.menu_items = ["Continuar", "Feitiços e Runas", "Controles", "Lista de Pontuação", "Sair"]
        self.selected_item = 0
        self.menu_rects = []
        self.hovered_item = None
        self.title_font = pygame.font.SysFont('arial', 72, bold=True)  # Fonte grande e em negrito para o título
        self.item_font = pygame.font.SysFont('arial', 28)  # Fonte para itens do menu
        self.button_font = pygame.font.SysFont('arial', 36, bold=True)  # Fonte para botões

    def handle_input(self, events, paused, running, mouse_pos):
        """Processa entrada para o menu principal."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_item = max(0, self.selected_item - 1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_item = min(
                        len(self.menu_items) - 1, self.selected_item + 1)
                elif event.key == pygame.K_RETURN:
                    if self.selected_item == 0:  # Continue
                        paused = False
                    elif self.selected_item == 1:  # Spells
                        self.menu.current_menu = 'inventory'
                        self.selected_item = 0
                    elif self.selected_item == 2:  # Controls
                        self.menu.current_menu = 'controls'
                        self.selected_item = 0
                    elif self.selected_item == 3:  # lista de pontuação
                        self.menu.current_menu = 'scores'
                        self.selected_item = 0
                    elif self.selected_item == 4:  # Exit
                        running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self.menu_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected_item = i
                        if i == 0:  # Continue
                            paused = False
                        elif i == 1:  # Spells
                            self.menu.current_menu = 'inventory'
                            self.selected_item = 0
                        elif i == 2:  # Controls
                            self.menu.current_menu = 'controls'
                            self.selected_item = 0
                        elif i== 3:  # lista de pontuação
                            self.menu.current_menu = 'scores'
                            self.selected_item = 0
                        elif i == 4:  # Exit
                            running = False
        return paused, running

    def draw(self, mouse_pos):
        """Desenha o menu principal com o estilo do menu inicial."""
        self.menu_rects = []
        self.hovered_item = None

        # Gradiente de fundo
        overlay = pygame.Surface((self.menu.width, self.menu.height), pygame.SRCALPHA)
        for y in range(self.menu.height):
            alpha = 180 + (y / self.menu.height) * 50  # Gradiente de 180 a 230 de opacidade
            overlay.fill((0, 0, 0, int(alpha)), (0, y, self.menu.width, 1))
        self.menu.screen.blit(overlay, (0, 0))

        # Título
        title = "Menu"
        title_text = self.title_font.render(title, True, (255, 255, 255))
        title_shadow = self.title_font.render(title, True, (50, 50, 50))  # Sombra cinza
        title_rect = title_text.get_rect(center=(self.menu.width // 2, self.menu.height // 2 - 200))
        title_shadow_rect = title_rect.copy()
        title_shadow_rect.move_ip(3, 3)  # Deslocamento da sombra
        self.menu.screen.blit(title_shadow, title_shadow_rect)
        self.menu.screen.blit(title_text, title_rect)

        # Itens do menu
        menu_y_start = self.menu.height // 2 - 50
        for i, item in enumerate(self.menu_items):
            # Renderiza o texto do item
            text = self.item_font.render(item, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.menu.width // 2, menu_y_start + i * 60))
            is_hovered = text_rect.collidepoint(mouse_pos)
            color = (255, 255, 0) if (i == self.selected_item or is_hovered) else (255, 255, 255)
            text = self.item_font.render(item, True, color)
            
            # Sombra do texto
            shadow = self.item_font.render(item, True, (50, 50, 50))
            shadow_rect = text_rect.copy()
            shadow_rect.move_ip(2, 2)  # Deslocamento da sombra
            
            # Fundo do botão com borda
            button_bg_rect = text_rect.inflate(20, 10)  # Expande o retângulo
            bg_color = (50, 50, 100) if color == BUTTON_COLOR else HIGHLIGHT_COLOR  # Destaque ao passar o mouse
            pygame.draw.rect(self.menu.screen, bg_color, button_bg_rect, border_radius=10)
            pygame.draw.rect(self.menu.screen, color, button_bg_rect, 2, border_radius=10)  # Borda
            
            # Desenha sombra e texto
            self.menu.screen.blit(shadow, shadow_rect)
            self.menu.screen.blit(text, text_rect)
            self.menu_rects.append(text_rect)
            
            if is_hovered:
                self.hovered_item = ('main', i)