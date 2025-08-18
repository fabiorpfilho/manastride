import pygame

class Menu:
    def __init__(self, screen, width, height, player):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont('arial', 24)
        self.selected_menu_item = 0  # Índice do item selecionado
        self.selected_section = 'spells'  # Seção atual: 'spells' ou 'runes'
        self.hovered_item = None  # Item sob o cursor do mouse
        self.menu_rects = []  # Retângulos das opções do menu
        self.menu_items = ["Continuar", "Feitiços", "Sair"]
        self.player = player
        self.current_menu = 'main'
        self.icon_cache = {}

    def handle_input(self, events, paused, running):
        """Processa eventos de entrada e retorna o estado atualizado de paused e running."""
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.current_menu == 'main':
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.selected_menu_item = max(0, self.selected_menu_item - 1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.selected_menu_item = min(len(self.menu_items) - 1, self.selected_menu_item + 1)
                    elif event.key == pygame.K_RETURN:
                        if self.selected_menu_item == 0:  # Continuar
                            paused = False
                            self.current_menu = 'main'
                        elif self.selected_menu_item == 1:  # Feitiços
                            self.current_menu = 'inventory'
                            self.selected_menu_item = 0
                            self.selected_section = 'spells'
                        elif self.selected_menu_item == 2:  # Sair
                            running = False
                elif self.current_menu == 'inventory':
                    max_spells = 3  # 3x1 grid para feitiços
                    max_runes = 24  # 6x4 grid para runas
                    if self.selected_section == 'spells':
                        max_index = max_spells - 1
                        if event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.selected_menu_item = max(0, self.selected_menu_item - 3)
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            if self.selected_menu_item + 3 <= max_index:
                                self.selected_menu_item += 3
                            else:
                                self.selected_section = 'runes'
                                self.selected_menu_item = 0
                        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            self.selected_menu_item = max(0, self.selected_menu_item - 1)
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            self.selected_menu_item = min(max_index, self.selected_menu_item + 1)
                    else:  # runes
                        max_index = max_runes - 1
                        col = self.selected_menu_item % 6
                        row = self.selected_menu_item // 6
                        if event.key == pygame.K_UP or event.key == pygame.K_w:
                            if row > 0:
                                self.selected_menu_item -= 6
                            else:
                                self.selected_section = 'spells'
                                self.selected_menu_item = 0
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.selected_menu_item = min(max_index, self.selected_menu_item + 6)
                        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            self.selected_menu_item = max(0, self.selected_menu_item - 1)
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            self.selected_menu_item = min(max_index, self.selected_menu_item + 1)
                    if event.key == pygame.K_ESCAPE:
                        self.current_menu = 'main'
                        self.selected_menu_item = 0
                        self.selected_section = 'spells'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clique esquerdo
                    for i, rect in enumerate(self.menu_rects):
                        if rect.collidepoint(mouse_pos):
                            if self.current_menu == 'main':
                                self.selected_menu_item = i
                                if i == 0:  # Continuar
                                    paused = False
                                    self.current_menu = 'main'
                                elif i == 1:  # Feitiços
                                    self.current_menu = 'inventory'
                                    self.selected_menu_item = 0
                                    self.selected_section = 'spells'
                                elif i == 2:  # Sair
                                    running = False
                            elif self.current_menu == 'inventory':
                                max_spells = 3
                                if i < max_spells:
                                    self.selected_section = 'spells'
                                    self.selected_menu_item = i
                                else:
                                    self.selected_section = 'runes'
                                    self.selected_menu_item = i - max_spells

        return paused, running

    def draw(self, mouse_pos):
        """Desenha o menu de pausa na tela."""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 255) if self.current_menu == 'inventory' else (0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        self.menu_rects = []
        self.hovered_item = None

        if self.current_menu == 'main':
            menu_y_start = self.height // 2 - 50
            for i, item in enumerate(self.menu_items):
                text = self.font.render(item, True, (255, 255, 255))
                text_rect = text.get_rect(center=(self.width // 2, menu_y_start + i * 60))
                is_hovered = text_rect.collidepoint(mouse_pos)
                color = (255, 255, 0) if (i == self.selected_menu_item or is_hovered) else (255, 255, 255)
                text = self.font.render(item, True, color)
                self.screen.blit(text, text_rect)
                self.menu_rects.append(text_rect)
                if is_hovered:
                    self.hovered_item = ('main', i)

        elif self.current_menu == 'inventory':
            center_x = self.width // 2
            center_y = self.height // 2
            self.draw_spell_section(center_x, center_y, mouse_pos)
            self.draw_rune_section(center_x, center_y, mouse_pos)
            self.draw_description_section(center_x, center_y, mouse_pos)

            back_text = self.font.render("Voltar (ESC)", True, (255, 255, 255))
            back_rect = back_text.get_rect(center=(center_x, center_y + 350))
            self.screen.blit(back_text, back_rect)

    def draw_spell_section(self, center_x, center_y, mouse_pos):
        """Desenha a seção de feitiços com grid de quadrados e símbolos."""
        spells_height = 100
        spells_width = 300
        spells_offset_x = -150
        spells_offset_y = -400
        spells_rect = pygame.Rect(center_x + spells_offset_x, center_y + spells_offset_y, spells_width, spells_height)
        pygame.draw.rect(self.screen, (100, 100, 100), spells_rect, 2)
        spells_title = self.font.render("Feitiços", True, (255, 255, 255))
        self.screen.blit(spells_title, (center_x + spells_offset_x + 100, center_y + spells_offset_y - 90))

        cell_size = spells_width // 3
        num_cols = 3
        num_rows = 1
        max_items = num_cols * num_rows

        spellbook = self.player.spell_system.spellbook
        for i in range(max_items):
            col = i % num_cols
            row = i // num_cols
            cell_x = center_x + spells_offset_x + col * cell_size
            cell_y = center_y + spells_offset_y + row * cell_size
            cell_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)
            pygame.draw.rect(self.screen, (150, 150, 150), cell_rect, 2)

            if i < len(spellbook):
                spell = spellbook[i]
                spell_name = spell.__class__.__name__.lower()
                icon_path = f"assets/ui/spells/{spell_name}.png"
                if icon_path not in self.icon_cache:
                    try:
                        self.icon_cache[icon_path] = pygame.image.load(icon_path)
                    except:
                        self.icon_cache[icon_path] = pygame.Surface((40, 40))
                        self.icon_cache[icon_path].fill((255, 0, 0))
                icon = pygame.transform.scale(self.icon_cache[icon_path], (cell_size - 20, cell_size - 20))
                icon_rect = icon.get_rect(center=(cell_x + cell_size // 2, cell_y + cell_size // 2))
                self.screen.blit(icon, icon_rect)

            is_hovered = cell_rect.collidepoint(mouse_pos)
            if is_hovered:
                pygame.draw.rect(self.screen, (255, 255, 0), cell_rect, 3)
                self.hovered_item = ('spells', i)
            if self.selected_section == 'spells' and i == self.selected_menu_item:
                pygame.draw.rect(self.screen, (255, 255, 0), cell_rect, 3)

            # Desenhar símbolos após o destaque para sobrescrever o amarelo
            # Losango superior (centro da linha de cima da célula)
            center_x_losango = cell_x + cell_size // 2
            center_y_losango = cell_y
            losango_points = [
                (center_x_losango, center_y_losango - 5),  # Topo
                (center_x_losango + 5, center_y_losango),  # Direita
                (center_x_losango, center_y_losango + 5),  # Baixo
                (center_x_losango - 5, center_y_losango)   # Esquerda
            ]
            pygame.draw.polygon(self.screen, (0, 0, 0), losango_points)  # Fundo preto
            pygame.draw.polygon(self.screen, (255, 255, 255), losango_points, 1)  # Contorno branco

            # Dois círculos ovais inferiores (equidistantes na linha de baixo)
            pygame.draw.circle(self.screen, (0, 0, 0), (cell_x + cell_size // 4, cell_y + cell_size - 3), 5)  # Fundo preto
            pygame.draw.circle(self.screen, (255, 255, 255), (cell_x + cell_size // 4, cell_y + cell_size - 3), 5, 1)  # Contorno branco
            pygame.draw.circle(self.screen, (0, 0, 0), (cell_x + 3 * cell_size // 4, cell_y + cell_size - 3), 5)  # Fundo preto
            pygame.draw.circle(self.screen, (255, 255, 255), (cell_x + 3 * cell_size // 4, cell_y + cell_size - 3), 5, 1)  # Contorno branco

            self.menu_rects.append(cell_rect)

    def draw_rune_section(self, center_x, center_y, mouse_pos):
        """Desenha a seção de runas com grid de quadrados sempre visíveis."""
        inventory_size = (600, 400)
        runes_offset_x = -(inventory_size[0] // 2)
        runes_offset_y = -200
        runes_rect = pygame.Rect(center_x + runes_offset_x, center_y + runes_offset_y, inventory_size[0], inventory_size[1])
        pygame.draw.rect(self.screen, (100, 100, 100), runes_rect, 2)
        
        runes_title = self.font.render("Runas", True, (255, 255, 255))
        self.screen.blit(runes_title, (center_x + runes_offset_x + 270, center_y + runes_offset_y - 30))

        cell_size = 100
        num_cols = 6
        num_rows = 4
        max_items = num_cols * num_rows

        runes = self.player.spell_system.runes
        for i in range(max_items):
            col = i % num_cols
            row = i // num_cols
            cell_x = center_x + runes_offset_x + col * cell_size
            cell_y = center_y + runes_offset_y + row * cell_size
            cell_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)
            pygame.draw.rect(self.screen, (150, 150, 150), cell_rect, 2)

            if i < len(runes):
                rune = runes[i]
                rune_name = rune.name if hasattr(rune, 'name') else 'runa'
                icon_path = f"assets/runes/asset32x32/{rune_name}.png"
                if icon_path not in self.icon_cache:
                    try:
                        self.icon_cache[icon_path] = pygame.image.load(icon_path)
                    except:
                        self.icon_cache[icon_path] = pygame.Surface((40, 40))
                        self.icon_cache[icon_path].fill((0, 255, 0))
                icon = pygame.transform.scale(self.icon_cache[icon_path], (cell_size - 20, cell_size - 20))
                icon_rect = icon.get_rect(center=(cell_x + cell_size // 2, cell_y + cell_size // 2))
                self.screen.blit(icon, icon_rect)

            is_hovered = cell_rect.collidepoint(mouse_pos)
            if is_hovered:
                pygame.draw.rect(self.screen, (255, 255, 0), cell_rect, 3)
                self.hovered_item = ('runes', i)
            if self.selected_section == 'runes' and i == self.selected_menu_item:
                pygame.draw.rect(self.screen, (255, 255, 0), cell_rect, 3)

            self.menu_rects.append(cell_rect)

    def draw_description_section(self, center_x, center_y, mouse_pos):
        """Desenha a seção de descrição."""
        description_size = (300, 400)
        desc_offset_x = 400
        desc_offset_y = -200
        desc_rect = pygame.Rect(center_x + desc_offset_x, center_y + desc_offset_y, description_size[0], description_size[1])
        pygame.draw.rect(self.screen, (100, 100, 100), desc_rect, 2)
        desc_title = self.font.render("Descrição", True, (255, 255, 255))
        self.screen.blit(desc_title, (center_x + desc_offset_x + 10, center_y + desc_offset_y + 10))

        if self.hovered_item:
            section, idx = self.hovered_item
            if section == 'spells':
                spellbook = self.player.spell_system.spellbook
                if idx < len(spellbook):
                    selected_item = spellbook[idx]
                    desc = f"Feitiço: {selected_item.__class__.__name__}\nDescrição: Ataque básico."
                else:
                    desc = ""
            elif section == 'runes':
                runes = self.player.spell_system.runes
                if idx < len(runes):
                    selected_item = runes[idx]
                    desc = f"Runa: {selected_item.name if hasattr(selected_item, 'name') else 'Runa'}\nDescrição: Aumenta poder."
                else:
                    desc = ""
            else:
                desc = "Nenhum item selecionado."
        else:
            if self.selected_section == 'spells':
                spellbook = self.player.spell_system.spellbook
                if self.selected_menu_item < len(spellbook):
                    selected_item = spellbook[self.selected_menu_item]
                    desc = f"Feitiço: {selected_item.__class__.__name__}\nDescrição: Ataque básico."
                else:
                    desc = ""
            elif self.selected_section == 'runes':
                runes = self.player.spell_system.runes
                if self.selected_menu_item < len(runes):
                    selected_item = runes[self.selected_menu_item]
                    desc = f"Runa: {selected_item.name if hasattr(selected_item, 'name') else 'Runa'}\nDescrição: Aumenta poder."
                else:
                    desc = ""
            else:
                desc = "Nenhum item selecionado."
        desc_lines = desc.split('\n')
        for i, line in enumerate(desc_lines):
            desc_text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(desc_text, (center_x + desc_offset_x + 10, center_y + desc_offset_y + 40 + i * 30))