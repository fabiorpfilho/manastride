import pygame
import time

class GameEnd:
    def __init__(self, menu):
        self.menu = menu
        self.screen = menu.screen
        self.width = menu.width
        self.height = menu.height
        self.font = menu.font
        
        # Texto de agradecimento
        self.thank_you_text = (
            "Este é o fim da versão atual do jogo! Você eliminou todos os inimigos e conquistou a arena!\n"
            "Estamos coletando feedback para melhorar a experiência.\n"
            "Por favor, compartilhe suas impressão ao preencher o formulário!\n"
            "Digite seu nome abaixo e selecione uma opção para continuar.\n"
        )
        
        # Configuração da fonte do corpo
        try:
            original_size = self.font.get_height()
            body_font_size = int(original_size * 0.7)
            self.body_font = pygame.font.Font(self.font.get_default_font(), body_font_size)
        except:
            self.body_font = pygame.font.Font(None, 24)
        
        self.options = ["Reiniciar", "Sair"]
        self.selected_option = -1  # Start with input field selected
        self.active = True
        
        # Variáveis para o fade-in
        self.alpha = 0  # Começa completamente transparente
        self.fade_speed = 255 / 60  # Aumenta alpha em 60 frames
        self.fading = True  # Controla se o fade-in está em progresso
        
        # Text input for player's name
        self.player_name = ""
        self.name_input_active = True  # Start with input active
        self.name_rect = pygame.Rect(0, 0, 200, 30)  # Rectangle for name input field, y will be set dynamically
        self.cursor_visible = True  # Control cursor blinking
        self.cursor_timer = time.time()  # Timer for cursor blink

    def wrap_text(self, text, font, max_width):
        """Quebra o texto em várias linhas com base na largura máxima."""
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            test_surface = font.render(test_line, True, (255, 255, 255))
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines

    def handle_input(self, events):
        """Processa entrada do usuário para digitar nome, navegar e selecionar opções."""
        if not self.fading:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check if the name input field is clicked
                    mouse_pos = pygame.mouse.get_pos()
                    center_x = self.width // 2
                    center_y = self.height // 2
                    desc_offset_x = -200
                    desc_offset_y = -250
                    # Calculate y_offset to match draw method
                    y_offset = 50
                    max_text_width = 400 - 20  # description_size[0] - 20
                    for line in self.thank_you_text.split('\n'):
                        wrapped_lines = self.wrap_text(line, self.body_font, max_text_width)
                        for _ in wrapped_lines:
                            y_offset += 20
                        y_offset += 30
                    name_rect_absolute = pygame.Rect(
                        center_x + desc_offset_x + 100,
                        center_y + desc_offset_y + y_offset - 50,
                        200, 30
                    )
                    if name_rect_absolute.collidepoint(mouse_pos):
                        self.name_input_active = True
                        self.selected_option = -1
                    else:
                        self.name_input_active = False
                        # Check if an option was clicked
                        for i, option in enumerate(self.options):
                            option_text = self.body_font.render(option, True, (255, 255, 255))
                            option_width = option_text.get_width()
                            option_x = (400 - option_width) // 2
                            option_rect = pygame.Rect(
                                center_x + desc_offset_x + option_x,
                                center_y + desc_offset_y + y_offset + i * 40,
                                option_width, 30
                            )
                            if option_rect.collidepoint(mouse_pos):
                                self.selected_option = i
                                self.name_input_active = False

                if event.type == pygame.KEYDOWN:
                    if self.name_input_active or self.selected_option == -1:
                        if event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                            self.name_input_active = False
                            self.selected_option = 0  # Move to first option
                        elif event.key == pygame.K_DOWN:
                            self.name_input_active = False
                            self.selected_option = 0  # Move to first option
                        elif event.key == pygame.K_UP:
                            self.name_input_active = False
                            self.selected_option = len(self.options) - 1  # Move to last option ("Sair")
                        elif event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        elif event.unicode.isprintable() and len(self.player_name) < 20:  # Limit name length
                            self.player_name += event.unicode
                    else:
                        if event.key == pygame.K_UP:
                            self.selected_option = (self.selected_option - 1) if self.selected_option > 0 else -1
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_TAB:
                            self.selected_option = (self.selected_option + 1) % len(self.options) if self.selected_option < len(self.options) - 1 else -1
                        elif event.key == pygame.K_RETURN:
                            return self.options[self.selected_option], self.player_name
        return None, None

    def draw(self):
        """Desenha a tela de agradecimento com fundo opaco, fade-in e campo de entrada de nome."""
        # Update cursor blinking
        if time.time() - self.cursor_timer > 0.5:  # Blink every 0.5 seconds
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = time.time()

        # Desenha o overlay de fundo com transparência fixa
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))
        
        # Cria uma superfície para a caixa de texto
        description_size = (400, 500)
        menu_surface = pygame.Surface(description_size, pygame.SRCALPHA)
        
        center_x = self.width // 2
        center_y = self.height // 2
        desc_offset_x = -200
        desc_offset_y = -250
        desc_rect = pygame.Rect(0, 0, description_size[0], description_size[1])
        
        # Desenha a borda e o fundo da caixa
        pygame.draw.rect(menu_surface, (100, 100, 100), desc_rect, 2)
        menu_surface.fill((0, 0, 0, 180), desc_rect)
        
        # Renderiza o título
        title_text = self.font.render("Obrigado por jogar!", True, (255, 255, 255))
        title_width = title_text.get_width()
        title_x = (description_size[0] - title_width) // 2
        menu_surface.blit(title_text, (title_x, 10))

        # Renderiza o texto descritivo
        max_text_width = description_size[0] - 20
        desc_lines = self.thank_you_text.split('\n')
        y_offset = 50
        for line in desc_lines:
            wrapped_lines = self.wrap_text(line, self.body_font, max_text_width)
            for wrapped_line in wrapped_lines:
                desc_text = self.body_font.render(wrapped_line, True, (255, 255, 255))
                menu_surface.blit(desc_text, (10, y_offset))
                y_offset += 20
            y_offset += 30

        # Renderiza o campo de entrada de nome após o texto descritivo
        name_rect = pygame.Rect(100, y_offset - 50, 200, 30)
        border_color = (255, 255, 0) if self.selected_option == -1 else (255, 255, 255) if self.name_input_active else (150, 150, 150)
        pygame.draw.rect(menu_surface, border_color, name_rect, 2)
        name_text = self.body_font.render(self.player_name if self.player_name else "Digite seu nome", True, (255, 255, 255))
        name_text_rect = name_text.get_rect(center=name_rect.center)
        menu_surface.blit(name_text, name_text_rect)
        # Draw blinking cursor
        if (self.name_input_active or self.selected_option == -1) and self.cursor_visible:
            cursor_x = name_text_rect.right + 2 if self.player_name else name_rect.left + 5
            cursor_y = name_rect.centery
            pygame.draw.line(menu_surface, (255, 255, 255), (cursor_x, cursor_y - 10), (cursor_x, cursor_y + 10), 2)

        # Renderiza as opções
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
            option_text = self.body_font.render(option, True, color)
            option_width = option_text.get_width()
            option_x = (description_size[0] - option_width) // 2
            menu_surface.blit(option_text, (option_x, y_offset + i * 40))

        # Aplica o efeito de fade-in apenas na caixa de texto
        if self.fading:
            self.alpha += self.fade_speed
            if self.alpha >= 255:
                self.alpha = 255
                self.fading = False
            menu_surface.set_alpha(int(self.alpha))

        # Desenha a superfície da caixa de texto na tela
        self.screen.blit(menu_surface, (center_x + desc_offset_x, center_y + desc_offset_y))

    def update(self, events):
        """Atualiza a tela e retorna a ação selecionada e o nome do jogador."""
        return self.handle_input(events)