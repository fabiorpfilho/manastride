import pygame

class DescriptionSection:
    def __init__(self, menu):
        self.menu = menu
        self.hovered_item = None

    def draw(self, mouse_pos):
        """Desenha a seção de descrição."""
        center_x = self.menu.width // 2
        center_y = self.menu.height // 2
        description_size = (300, 400)
        desc_offset_x = 400
        desc_offset_y = -200
        desc_rect = pygame.Rect(center_x + desc_offset_x, center_y + desc_offset_y, description_size[0], description_size[1])
        pygame.draw.rect(self.menu.screen, (100, 100, 100), desc_rect, 2)
        desc_title = self.menu.font.render("Descrição", True, (255, 255, 255))
        self.menu.screen.blit(desc_title, (center_x + desc_offset_x + 10, center_y + desc_offset_y + 10))

        if self.hovered_item:
            section, idx = self.hovered_item
            if section == 'spells':
                spellbook = self.menu.player.spell_system.spellbook
                if idx < len(spellbook):
                    selected_item = spellbook[idx]
                    desc = f"Feitiço: {selected_item.__class__.__name__}\nDescrição: Ataque básico."
                else:
                    desc = ""
            elif section == 'runes':
                runes = self.menu.player.spell_system.runes
                if idx < len(runes):
                    selected_item = runes[idx]
                    desc = f"Runa: {selected_item.name if hasattr(selected_item, 'name') else 'Runa'}\nDescrição: Aumenta poder."
                else:
                    desc = ""
            else:
                desc = "Nenhum item selecionado."
        else:
            if self.menu.spells_section.selected_section == 'spells':
                spellbook = self.menu.player.spell_system.spellbook
                if self.menu.spells_section.selected_item < len(spellbook):
                    selected_item = spellbook[self.menu.spells_section.selected_item]
                    desc = f"Feitiço: {selected_item.__class__.__name__}\nDescrição: Ataque básico."
                else:
                    desc = ""
            elif self.menu.spells_section.selected_section == 'runes':
                runes = self.menu.player.spell_system.runes
                if self.menu.runes_section.selected_item < len(runes):
                    selected_item = runes[self.menu.runes_section.selected_item]
                    desc = f"Runa: {selected_item.name if hasattr(selected_item, 'name') else 'Runa'}\nDescrição: Aumenta poder."
                else:
                    desc = ""
            else:
                desc = "Nenhum item selecionado."
        desc_lines = desc.split('\n')
        for i, line in enumerate(desc_lines):
            desc_text = self.menu.font.render(line, True, (255, 255, 255))
            self.menu.screen.blit(desc_text, (center_x + desc_offset_x + 10, center_y + desc_offset_y + 40 + i * 30))