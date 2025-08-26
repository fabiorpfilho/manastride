import pygame


class MainMenu:
    def __init__(self, menu):
        self.menu = menu
        self.menu_items = ["Continuar", "Feitiços", "Sair"]
        self.selected_item = 0
        self.menu_rects = []
        self.hovered_item = None

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
                    if self.selected_item == 0:  # Continuar
                        paused = False
                    elif self.selected_item == 1:  # Feitiços
                        self.menu.current_menu = 'inventory'
                        self.selected_item = 0
                    elif self.selected_item == 2:  # Sair
                        running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self.menu_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected_item = i
                        if i == 0:  # Continuar
                            paused = False
                        elif i == 1:  # Feitiços
                            self.menu.current_menu = 'inventory'
                            self.selected_item = 0
                        elif i == 2:  # Sair
                            running = False
        return paused, running

    def draw(self, mouse_pos):
        """Desenha o menu principal."""
        self.menu_rects = []
        self.hovered_item = None
        menu_y_start = self.menu.height // 2 - 50
        for i, item in enumerate(self.menu_items):
            text = self.menu.font.render(item, True, (255, 255, 255))
            text_rect = text.get_rect(
                center=(self.menu.width // 2, menu_y_start + i * 60))
            is_hovered = text_rect.collidepoint(mouse_pos)
            color = (255, 255, 0) if (
                i == self.selected_item or is_hovered) else (255, 255, 255)
            text = self.menu.font.render(item, True, color)
            self.menu.screen.blit(text, text_rect)
            self.menu_rects.append(text_rect)
            if is_hovered:
                self.hovered_item = ('main', i)
