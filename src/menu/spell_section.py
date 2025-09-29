import pygame
from spell_system.rune_type import RuneType
from config import RUNE_COLORS

class SpellsSection:
    def __init__(self, menu):
        self.menu = menu
        self.selected_item = 0
        self.selected_section = 'spells'
        self.menu_rects = []

    def handle_input(self, events, paused, running, mouse_pos):
        """Processa entrada para a seção de feitiços."""
        max_spells = 3
        for event in events:
            if event.type == pygame.KEYDOWN and self.selected_section == 'spells':
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    pass
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_section = 'runes'
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.selected_item = max(0, self.selected_item - 1)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.selected_item = min(max_spells - 1, self.selected_item + 1)
                elif event.key == pygame.K_RETURN:
                    # Se uma runa já está selecionada, vincular a runa ao feitiço
                    if self.menu.selected_rune is not None and self.selected_item < len(self.menu.player.spell_system.spellbook):
                        rune = self.menu.player.spell_system.runes[self.menu.selected_rune]
                        spell = self.menu.player.spell_system.spellbook[self.selected_item]
                        if rune.rune_type == RuneType.MAJOR:
                            self.menu.player.spell_system.update_spell(
                                self.selected_item + 1,
                                major_rune=rune,
                                minor_runes=spell.minor_runes
                            )
                        elif rune.rune_type == RuneType.MINOR:
                            self.menu.player.spell_system.update_spell(
                                self.selected_item + 1,
                                major_rune=spell.major_rune,
                                minor_runes=[rune]
                            )
                        # Resetar seleção
                        self.menu.selected_spell = None
                        self.menu.selected_rune = None
                        self.selected_section = 'spells'
                        self.selected_item = 0
                    # Se nenhuma runa está selecionada, selecionar o feitiço e mudar para a seção de runas
                    elif self.selected_item < len(self.menu.player.spell_system.spellbook):
                        self.menu.selected_spell = self.selected_item
                        self.selected_section = 'runes'

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self.menu_rects):
                    if rect.collidepoint(mouse_pos) and i < max_spells:
                        self.selected_section = 'spells'
                        self.selected_item = i
        return paused, running

    def draw(self, mouse_pos):
        """Desenha a seção de feitiços."""
        center_x = self.menu.width // 2
        center_y = self.menu.height // 2
        spells_height = 100
        spells_width = 300
        spells_offset_x = -150
        spells_offset_y = -400
        spells_rect = pygame.Rect(center_x + spells_offset_x, center_y + spells_offset_y, spells_width, spells_height)
        pygame.draw.rect(self.menu.screen, (100, 100, 100), spells_rect, 2)
        spells_title = self.menu.font.render("Feitiços", True, (255, 255, 255))
        self.menu.screen.blit(spells_title, (center_x + spells_offset_x + 100, center_y + spells_offset_y - 90))

        cell_size = spells_width // 3
        num_cols = 3
        num_rows = 1
        max_items = num_cols * num_rows
        self.menu_rects = []

        spellbook = self.menu.player.spell_system.spellbook
        for i in range(max_items):
            col = i % num_cols
            row = i // num_cols
            cell_x = center_x + spells_offset_x + col * cell_size
            cell_y = center_y + spells_offset_y + row * cell_size
            cell_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)
            pygame.draw.rect(self.menu.screen, (150, 150, 150), cell_rect, 2)

            if i < len(spellbook):
                spell = spellbook[i]
                spell_name = spell.__class__.__name__.lower()
                icon_path = f"assets/ui/spells/{spell_name}.png"
                if icon_path not in self.menu.icon_cache:
                    try:
                        self.menu.icon_cache[icon_path] = pygame.image.load(icon_path)
                    except:
                        self.menu.icon_cache[icon_path] = pygame.Surface((40, 40))
                        self.menu.icon_cache[icon_path].fill((255, 0, 0))
                icon = pygame.transform.scale(self.menu.icon_cache[icon_path], (cell_size - 20, cell_size - 20))
                icon_rect = icon.get_rect(center=(cell_x + cell_size // 2, cell_y + cell_size // 2))
                self.menu.screen.blit(icon, icon_rect)

            is_hovered = cell_rect.collidepoint(mouse_pos)
            if is_hovered or (self.selected_section == 'spells' and i == self.selected_item):
                pygame.draw.rect(self.menu.screen, (255, 255, 0), cell_rect, 3)
                self.menu.description_section.hovered_item = ('spells', i)

            # Draw symbols with rune colors
            center_x_losango = cell_x + cell_size // 2
            center_y_losango = cell_y
            losango_points = [
                (center_x_losango, center_y_losango - 5),
                (center_x_losango + 5, center_y_losango),
                (center_x_losango, center_y_losango + 5),
                (center_x_losango - 5, center_y_losango)
            ]
            # Fill diamond if major rune is assigned
            major_color = (0, 0, 0)
            if i < len(spellbook) and spellbook[i].major_rune:
                major_color = RUNE_COLORS.get(spellbook[i].major_rune.name, (0, 0, 0))
            pygame.draw.polygon(self.menu.screen, major_color, losango_points)
            pygame.draw.polygon(self.menu.screen, (255, 255, 255), losango_points, 1)

            # Draw circles for minor runes
            minor_rune_colors = [(0, 0, 0), (0, 0, 0)]
            if i < len(spellbook):
                for j, rune in enumerate(spellbook[i].minor_runes[:2]):
                    minor_rune_colors[j] = RUNE_COLORS.get("fire_rune", (0, 0, 0))
            pygame.draw.circle(self.menu.screen, minor_rune_colors[0], (cell_x + cell_size // 4, cell_y + cell_size - 3), 5)
            pygame.draw.circle(self.menu.screen, (255, 255, 255), (cell_x + cell_size // 4, cell_y + cell_size - 3), 5, 1)
            pygame.draw.circle(self.menu.screen, minor_rune_colors[1], (cell_x + 3 * cell_size // 4, cell_y + cell_size - 3), 5)
            pygame.draw.circle(self.menu.screen, (255, 255, 255), (cell_x + 3 * cell_size // 4, cell_y + cell_size - 3), 5, 1)

            self.menu_rects.append(cell_rect)