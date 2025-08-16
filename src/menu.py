import pygame

class Menu:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont('arial', 36)  # Fonte para o menu
        self.selected_menu_item = 0  # Item selecionado (0: Continuar, 1: Sair)
        self.menu_rects = []  # Retângulos das opções do menu
        self.menu_items = ["Continuar", "Feitiços", "Sair"]  # Opções do menu

    def handle_input(self, events, paused, running):
        """Processa eventos de entrada e retorna o estado atualizado de paused e running."""
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_menu_item = max(0, self.selected_menu_item - 1)
                elif event.key == pygame.K_DOWN:
                    self.selected_menu_item = min(len(self.menu_items) - 1, self.selected_menu_item + 1)
                elif event.key == pygame.K_RETURN:
                    if self.selected_menu_item == 0:  # Continuar
                        paused = False
                    elif self.selected_menu_item == 1:  # Sair
                        running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and paused:
                if event.button == 1:  # Clique esquerdo
                    for i, rect in enumerate(self.menu_rects):
                        if rect.collidepoint(mouse_pos):
                            self.selected_menu_item = i
                            if i == 0:  # Continuar
                                paused = False
                            elif i == 1:  # Sair
                                running = False
        return paused, running

    def draw(self, mouse_pos):
        """Desenha o menu de pausa na tela."""
        # Fundo semitransparente
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Preto com transparência
        self.screen.blit(overlay, (0, 0))

        # Desenha as opções do menu
        menu_y_start = self.height // 2 - 50
        self.menu_rects = []  # Limpa a lista de retângulos

        for i, item in enumerate(self.menu_items):
            # Verifica se o mouse está sobre a opção
            text = self.font.render(item, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.width // 2, menu_y_start + i * 60))
            is_hovered = text_rect.collidepoint(mouse_pos)
            color = (255, 255, 0) if (i == self.selected_menu_item or is_hovered) else (255, 255, 255)

            # Redesenha o texto com a cor atualizada
            text = self.font.render(item, True, color)
            self.screen.blit(text, text_rect)
            self.menu_rects.append(text_rect)  # Armazena o retângulo para cliques

            # Atualiza a seleção se o mouse está sobre a opção
            if is_hovered:
                self.selected_menu_item = i