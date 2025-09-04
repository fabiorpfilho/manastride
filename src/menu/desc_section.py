import pygame

class DescriptionSection:
    def __init__(self, menu):
        self.menu = menu
        self.hovered_item = None

        # Traduções de nomes dos feitiços
        self.spell_names = {
            "Projectile": "Projétil",
            "Dash": "Investida",
            "Shield": "Escudo",
        }

        # Traduções de nomes das runas
        self.rune_names = {
            "fan": "Leque",
            "multiple": "Múltipla",
        }

        # Descrições base dos feitiços
        self.spell_descriptions = {
            "Projectile": "Um projétil que causa\n dano no impacto.",
            "Dash": "Avança rapidamente em\n uma direção.",
            "Shield": "Gera um escudo que\n absorve uma pequena\n quantidade de dano.",
        }

        # Descrições das runas
        self.rune_descriptions = {
            "fan": "Atribui um comportamento\n de leque ao feitiço.",
            "multiple": "Multiplica o feitiço\n em algum aspecto.",
        }

        # Como cada runa altera a descrição do feitiço
        self.rune_spell_effects = {
            "fan": "O feitiço é lançado em\n formato de leque.",
            "multiple": "O feitiço é multiplicado em\n várias cópias.",
        }

    def get_name(self, item, item_type):
        """Retorna o nome traduzido do feitiço ou runa."""
        if item_type == "spell":
            return self.spell_names.get(item.__class__.__name__, item.__class__.__name__)
        elif item_type == "rune":
            return self.rune_names.get(getattr(item, "name", "Runa"), getattr(item, "name", "Runa"))
        return "Desconhecido"

    def get_description(self, item, item_type):
        """Retorna a descrição personalizada para feitiço ou runa."""
        if item_type == "spell":
            base_desc = self.spell_descriptions.get(item.__class__.__name__, "Um feitiço misterioso sem descrição.")

            # Se o feitiço tiver uma major_rune, adiciona a descrição da runa
            if hasattr(item, "major_rune") and item.major_rune is not None:
                rune_name = getattr(item.major_rune, "name", None)
                if rune_name and rune_name in self.rune_spell_effects:
                    return f"{base_desc}\n\nRuna aplicada: {self.get_name(item.major_rune, 'rune')}\n{self.rune_spell_effects[rune_name]}"
            return base_desc

        elif item_type == "rune":
            return self.rune_descriptions.get(getattr(item, "name", "Runa"), "Uma runa misteriosa sem descrição.")

        return "Nenhum item selecionado."

    def draw(self, mouse_pos):
        center_x = self.menu.width // 2
        center_y = self.menu.height // 2
        description_size = (300, 400)
        desc_offset_x = 400
        desc_offset_y = -200
        desc_rect = pygame.Rect(center_x + desc_offset_x, center_y + desc_offset_y, description_size[0], description_size[1])
        pygame.draw.rect(self.menu.screen, (100, 100, 100), desc_rect, 2)
        desc_title = self.menu.font.render("Descrição", True, (255, 255, 255))
        self.menu.screen.blit(desc_title, (center_x + desc_offset_x + 10, center_y + desc_offset_y + 10))

        # Determinar qual item está selecionado/hovered
        if self.hovered_item:
            section, idx = self.hovered_item
            if section == 'spells':
                spellbook = self.menu.player.spell_system.spellbook
                if idx < len(spellbook):
                    selected_item = spellbook[idx]
                    name = self.get_name(selected_item, "spell")
                    desc = f"Feitiço: {name}\n{self.get_description(selected_item, 'spell')}"
                else:
                    desc = ""
            elif section == 'runes':
                runes = self.menu.player.spell_system.runes
                if idx < len(runes):
                    selected_item = runes[idx]
                    name = self.get_name(selected_item, "rune")
                    desc = f"Runa: {name}\n{self.get_description(selected_item, 'rune')}"
                else:
                    desc = ""
            else:
                desc = "Nenhum item selecionado."
        else:
            if self.menu.spells_section.selected_section == 'spells':
                spellbook = self.menu.player.spell_system.spellbook
                if self.menu.spells_section.selected_item < len(spellbook):
                    selected_item = spellbook[self.menu.spells_section.selected_item]
                    name = self.get_name(selected_item, "spell")
                    desc = f"Feitiço: {name}\n{self.get_description(selected_item, 'spell')}"
                else:
                    desc = ""
            elif self.menu.spells_section.selected_section == 'runes':
                runes = self.menu.player.spell_system.runes
                if self.menu.runes_section.selected_item < len(runes):
                    selected_item = runes[self.menu.runes_section.selected_item]
                    name = self.get_name(selected_item, "rune")
                    desc = f"Runa: {name}\n{self.get_description(selected_item, 'rune')}"
                else:
                    desc = ""
            else:
                desc = "Nenhum item selecionado."

        # Renderizar descrição em múltiplas linhas
        desc_lines = desc.split('\n')
        for i, line in enumerate(desc_lines):
            desc_text = self.menu.font.render(line, True, (255, 255, 255))
            self.menu.screen.blit(desc_text, (center_x + desc_offset_x + 10, center_y + desc_offset_y + 40 + i * 30))
