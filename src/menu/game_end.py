import pygame

class GameEnd:
    def __init__(self, menu):
        self.menu = menu
        self.screen = menu.screen
        self.width = menu.width
        self.height = menu.height
        self.font = menu.font
        
        # Texto de agradecimento
        self.thank_you_text = (
            "Este é o fim da versão atual do jogo! Você eliminou todos os inimigos da segunda fase\n"
            "Estamos coletando feedback para melhorar a experiência.\n"
            "Por favor, compartilhe suas impressão ao preencher o formulário!\n"
            "Se quiser continuar jogando sinta-se livre para reiniciar o jogo ao clica abaixo\n"
        )
        
        # Configuração da fonte do corpo
        try:
            original_size = self.font.get_height()
            body_font_size = int(original_size * 0.7)
            self.body_font = pygame.font.Font(self.font.get_default_font(), body_font_size)
        except:
            self.body_font = pygame.font.Font(None, 24)
        
        self.options = ["Reiniciar", "Sair"]
        self.selected_option = 0
        self.active = True
        
        # Variáveis para o fade-in
        self.alpha = 0  # Começa completamente transparente
        self.fade_speed = 255 / 60  # Aumenta alpha em 60 frames (ajuste conforme desejado)
        self.fading = True  # Controla se o fade-in está em progresso

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
        """Processa entrada do usuário para navegar e selecionar opções."""
        # Só processa entrada após o fade-in terminar
        if not self.fading:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        return self.options[self.selected_option]
        return None

    def draw(self):
        """Desenha a tela de agradecimento com fundo opaco e fade-in na caixa de texto."""
        # Desenha o overlay de fundo com transparência fixa
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))  # Fundo com alfa fixo para maior visibilidade do mapa
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
        menu_surface.fill((0, 0, 0, 180), desc_rect)  # Fundo da caixa semi-transparente
        
        # Renderiza o título
        title_text = self.font.render("Obrigado por jogar!", True, (255, 255, 255))
        title_width = title_text.get_width()
        title_x = (description_size[0] - title_width) // 2
        menu_surface.blit(title_text, (title_x, 10))

        # Renderiza o texto descritivo
        max_text_width = description_size[0] - 20
        desc_lines = self.thank_you_text.split('\n')
        y_offset = 40
        for line in desc_lines:
            wrapped_lines = self.wrap_text(line, self.body_font, max_text_width)
            for wrapped_line in wrapped_lines:
                desc_text = self.body_font.render(wrapped_line, True, (255, 255, 255))
                menu_surface.blit(desc_text, (10, y_offset))
                y_offset += 30
            y_offset += 30

        # Renderiza as opções
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
            option_text = self.body_font.render(option, True, color)
            option_width = option_text.get_width()
            option_x = (description_size[0] - option_width) // 2
            menu_surface.blit(option_text, (option_x, (y_offset + i * 40) - 50))

        # Aplica o efeito de fade-in apenas na caixa de texto
        if self.fading:
            self.alpha += self.fade_speed
            if self.alpha >= 255:
                self.alpha = 255
                self.fading = False  # Termina o fade-in
            menu_surface.set_alpha(int(self.alpha))

        # Desenha a superfície da caixa de texto na tela
        self.screen.blit(menu_surface, (center_x + desc_offset_x, center_y + desc_offset_y))

    def update(self, events):
        """Atualiza a tela e retorna a ação selecionada."""
        return self.handle_input(events)