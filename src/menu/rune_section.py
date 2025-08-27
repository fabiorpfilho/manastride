import pygame
from spell_system.rune_type import RuneType
from config import RUNE_COLORS

class RunesSection:
    def __init__(self, menu):
        self.menu = menu
        self.selected_item = 0
        self.selected_section = 'runes'
        self.menu_rects = []

    def handle_input(self, events, paused, running, mouse_pos):
        """Processa entrada para a seção de runas."""
        max_runes = 24
        for event in events:
            if event.type == pygame.KEYDOWN and self.menu.spells_section.selected_section == 'runes':
                col = self.selected_item % 6
                row = self.selected_item // 6
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    if row > 0:
                        self.selected_item -= 6
                    else:
                        self.menu.spells_section.selected_section = 'spells'
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_item = min(max_runes - 1, self.selected_item + 6)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.selected_item = max(0, self.selected_item - 1)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.selected_item = min(max_runes - 1, self.selected_item + 1)
                elif event.key == pygame.K_RETURN:
                    # Select rune and assign to selected spell
                    if self.menu.selected_spell is not None and self.selected_item < len(self.menu.player.spell_system.runes):
                        rune = self.menu.player.spell_system.runes[self.selected_item]
                        spell = self.menu.player.spell_system.spellbook[self.menu.selected_spell]
                        if rune.rune_type == RuneType.MAJOR:
                            # Allow replacing the major rune
                            self.menu.player.spell_system.update_spell(
                                self.menu.selected_spell + 1,
                                major_rune=rune,
                                minor_runes=spell.minor_runes
                            )
                            self.menu.selected_spell = None
                            self.menu.spells_section.selected_section = 'spells'
                            self.selected_item = 0
                        elif rune.rune_type == RuneType.MINOR and len(spell.minor_runes) < 2:
                            new_minor_runes = spell.minor_runes + [rune]
                            self.menu.player.spell_system.update_spell(
                                self.menu.selected_spell + 1,
                                major_rune=spell.major_rune,
                                minor_runes=new_minor_runes
                            )
                            self.menu.selected_spell = None
                            self.menu.spells_section.selected_section = 'spells'
                            self.selected_item = 0
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self.menu_rects):
                    if rect.collidepoint(mouse_pos):
                        self.menu.spells_section.selected_section = 'runes'
                        self.selected_item = i
        return paused, running

    def draw(self, mouse_pos):
        """Desenha a seção de runas."""
        center_x = self.menu.width // 2
        center_y = self.menu.height // 2
        inventory_size = (600, 400)
        runes_offset_x = -(inventory_size[0] // 2)
        runes_offset_y = -200
        runes_rect = pygame.Rect(center_x + runes_offset_x, center_y + runes_offset_y, inventory_size[0], inventory_size[1])
        pygame.draw.rect(self.menu.screen, (100, 100, 100), runes_rect, 2)

        runes_title = self.menu.font.render("Runas", True, (255, 255, 255))
        self.menu.screen.blit(runes_title, (center_x + runes_offset_x + 270, center_y + runes_offset_y - 30))

        cell_size = 100
        num_cols = 6
        num_rows = 4
        max_items = num_cols * num_rows
        self.menu_rects = []

        runes = self.menu.player.spell_system.runes
        for i in range(max_items):
            col = i % num_cols
            row = i // num_cols
            cell_x = center_x + runes_offset_x + col * cell_size
            cell_y = center_y + runes_offset_y + row * cell_size
            cell_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)
            pygame.draw.rect(self.menu.screen, (150, 150, 150), cell_rect, 2)

            if i < len(runes):
                rune = runes[i]
                rune_name = rune.name if hasattr(rune, 'name') else 'runa'
                icon_path = f"assets/runes/asset32x32/{rune_name}.png"
                if icon_path not in self.menu.icon_cache:
                    try:
                        self.menu.icon_cache[icon_path] = pygame.image.load(icon_path)
                    except:
                        self.menu.icon_cache[icon_path] = pygame.Surface((40, 40))
                        self.menu.icon_cache[icon_path].fill((0, 255, 0))
                icon = pygame.transform.scale(self.menu.icon_cache[icon_path], (cell_size - 20, cell_size - 20))
                icon_rect = icon.get_rect(center=(cell_x + cell_size // 2, cell_y + cell_size // 2))
                self.menu.screen.blit(icon, icon_rect)

            is_hovered = cell_rect.collidepoint(mouse_pos)
            highlight_color = RUNE_COLORS.get(runes[i].name, (255, 255, 0)) if i < len(runes) else (255, 255, 0)
            if is_hovered or (self.menu.spells_section.selected_section == 'runes' and i == self.selected_item):
                pygame.draw.rect(self.menu.screen, highlight_color, cell_rect, 3)
                self.menu.description_section.hovered_item = ('runes', i)

            self.menu_rects.append(cell_rect)