import pygame

class InstructionSection:
    def __init__(self, menu):
        self.menu = menu
        # Texto estático de instrução (pode ser editado aqui)
        self.instruction_text = (
            "Tecle ENTER para selecionar uma runa e um feitiço para vinculá-los.\n "
            "Cada feitiço pode ter uma runa maior e duas runas menores vinculadas a ele\n "
            "Runas só podem ser vinculadas a um feitiço por vez, equipar uma mesma runa a outro feitiço irá desvincula-la.\n"
        )
        # Criar uma fonte menor para o texto do corpo (tamanho reduzido em relação à fonte do menu)
        try:
            original_size = self.menu.font.get_height()
            body_font_size = int(original_size * 0.7)  # Reduz para 70% do tamanho original
            self.body_font = pygame.font.Font(self.menu.font.get_default_font(), body_font_size)
        except:
            # Fallback para um tamanho fixo se não for possível obter o tamanho da fonte
            self.body_font = pygame.font.Font(None, 24)

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

    def draw(self):
        center_x = self.menu.width // 2
        center_y = self.menu.height // 2
        description_size = (300, 400)
        desc_offset_x = -750
        desc_offset_y = -200
        desc_rect = pygame.Rect(center_x + desc_offset_x, center_y + desc_offset_y, description_size[0], description_size[1])
        pygame.draw.rect(self.menu.screen, (100, 100, 100), desc_rect, 2)
        
        # Renderizar título centralizado
        desc_title = self.menu.font.render("Instruções", True, (255, 255, 255))
        title_width = desc_title.get_width()
        title_x = center_x + desc_offset_x + (description_size[0] - title_width) // 2  # Centraliza horizontalmente
        self.menu.screen.blit(desc_title, (title_x, center_y + desc_offset_y + 10))

        # Renderizar texto de instrução com fonte menor e linha vazia entre parágrafos
        max_text_width = description_size[0] - 20  # Margem de 10 pixels de cada lado
        desc_lines = self.instruction_text.split('\n')  # Suporta quebras manuais no texto
        y_offset = center_y + desc_offset_y + 40
        for line in desc_lines:
            # Aplicar quebra de texto automática para cada linha usando a fonte do corpo
            wrapped_lines = self.wrap_text(line, self.body_font, max_text_width)
            for wrapped_line in wrapped_lines:
                desc_text = self.body_font.render(wrapped_line, True, (255, 255, 255))
                self.menu.screen.blit(desc_text, (center_x + desc_offset_x + 10, y_offset))
                y_offset += 30  # Incrementa o offset vertical para cada linha
            y_offset += 30  # Adiciona espaço extra (linha vazia) após cada parágrafo