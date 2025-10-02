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
            "fan": "Raiz",
            "multiple": "Múltipla",
        }

        # Descrições base dos feitiços (sem quebras de linha manuais)
        self.spell_descriptions = {
            "Projectile": "Um projétil que causa dano no impacto.",
            "Dash": "Avança rapidamente em uma direção.",
            "Shield": "Gera um escudo que absorve uma pequena quantidade de dano.",
        }

        # Descrições das runas (sem quebras de linha manuais)
        self.rune_descriptions = {
            "fan": "Permite que o feitiço se espalhe como as raízes de uma árvore.",
            "multiple": "Multiplica o feitiço em algum aspecto.",
        }

        # Como cada runa altera a descrição do feitiço (sem quebras de linha manuais)
        self.rune_spell_effects = {
            "fan": (
                "Projétil: vários projéteis se dispersam à frente.\n"
                "Investida: permite avançar para cima ou na diagonal.\n"
                "Escudo: gera uma barreira sólida que impede inimigos de atravessar."
            ),
            "multiple": (
                "Projétil: Atira três projéteis um atrás do outro.\n"
                "Investida: Permite um curto avanço várias vezes sem ativar recarga ou custo de mana por um pequeno período.\n"
                "Escudo: Gera um escudo que absorve completamente os 3 próximos danos tomados."
            ),
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
            spell_name = self.get_name(item, "spell")
            base_desc = self.spell_descriptions.get(item.__class__.__name__, "Um feitiço misterioso sem descrição.")

            # Descrição base do feitiço
            desc_lines = [base_desc]

            # Adicionar informações da runa maior, se houver
            if hasattr(item, "major_rune") and item.major_rune is not None:
                rune_name = getattr(item.major_rune, "name", None)
                if rune_name and rune_name in self.rune_spell_effects:
                    rune_effect_text = self.rune_spell_effects[rune_name]
                    # Filtrar apenas a linha correspondente a este feitiço
                    effect_lines = rune_effect_text.split("\n")
                    for line in effect_lines:
                        if line.startswith(spell_name + ":"):
                            spell_effect_line = line.split(":", 1)[1].strip()
                            desc_lines.append(f"\nRuna maior: {self.get_name(item.major_rune, 'rune')}")
                            desc_lines.append(spell_effect_line)
                            break
            # Adicionar informações das runas menores, se houver
            if hasattr(item, "minor_runes") and item.minor_runes:
                print("Entrou aqui")
                for rune in item.minor_runes:
                    print("Runa descrição: ", rune)
                    rune_name = getattr(rune, "name", None)
                    if rune_name and rune_name in self.rune_spell_effects:
                        rune_effect_text = self.rune_spell_effects[rune_name]
                        effect_lines = rune_effect_text.split("\n")
                        for line in effect_lines:
                            if line.startswith(spell_name + ":"):
                                spell_effect_line = line.split(":", 1)[1].strip()
                                desc_lines.append(f"Runa menor: {self.get_name(rune, 'rune')}")
                                desc_lines.append(spell_effect_line)
                                break

            # Adicionar atributos do feitiço
            if hasattr(item, "attributes") and item.attributes:
                desc_lines.append("\nAtributos:")
                if "damage" in item.attributes:
                    desc_lines.append(f"Dano: {item.attributes['damage']}")
                if "distance" in item.attributes:
                    desc_lines.append(f"Distância: {item.attributes['distance']}")
                if "health" in item.attributes:
                    desc_lines.append(f"Vida: {item.attributes['health']}")
                if "mana_cost" in item.attributes:
                    desc_lines.append(f"Custo de Mana: {item.attributes['mana_cost']}")
                if hasattr(item, "cooldown"):
                    desc_lines.append(f"Cooldown: {item.cooldown:.1f}s")

            return "\n".join(desc_lines)

        elif item_type == "rune":
            base_desc = self.rune_descriptions.get(getattr(item, "name", "Runa"), "Um fragmento de algo maior, com pouco poder restante.")
            desc_lines = [base_desc]
            print('Item: ', item)
            # Adicionar atributos da runa, se for menor e tiver effect
            if hasattr(item, "rune_type") and item.rune_type == "MINOR" and hasattr(item, "effect") and item.effect:
                desc_lines.append("Atributos:")
                if "power" in item.effect:
                    desc_lines.append(f"Poder: {item.effect['power']}")
                if "cost" in item.effect:
                    desc_lines.append(f"Custo de Mana: {item.effect['cost']}")
                if "cooldown" in item.effect:
                    percentage = item.effect["cooldown"] / 10.0
                    desc_lines.append(f"Modificador de Cooldown: {percentage*100:+.0f}%")

            return "\n".join(desc_lines)

        return "Nenhum item selecionado."

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

    def draw(self, mouse_pos):
        center_x = self.menu.width // 2
        center_y = self.menu.height // 2
        description_size = (300, 400)
        desc_offset_x = 450
        desc_offset_y = -200
        desc_rect = pygame.Rect(center_x + desc_offset_x, center_y + desc_offset_y, description_size[0], description_size[1])
        pygame.draw.rect(self.menu.screen, (100, 100, 100), desc_rect, 2)
        desc_title = self.menu.font.render("Descrição", True, (255, 255, 255))
        title_width = desc_title.get_width()
        title_x = center_x + desc_offset_x + (description_size[0] - title_width) // 2  # Centraliza horizontalmente
        self.menu.screen.blit(desc_title, (title_x, center_y + desc_offset_y + 10))

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

        # Renderizar descrição mantendo desc.split('\n')
        max_text_width = description_size[0] - 20  # Margem de 10 pixels de cada lado
        desc_lines = desc.split('\n')  # Mantém a separação por \n
        y_offset = center_y + desc_offset_y + 40
        for line in desc_lines:
            # Aplicar quebra de texto automática para cada linha
            wrapped_lines = self.wrap_text(line, self.menu.font, max_text_width)
            for wrapped_line in wrapped_lines:
                desc_text = self.menu.font.render(wrapped_line, True, (255, 255, 255))
                self.menu.screen.blit(desc_text, (center_x + desc_offset_x + 10, y_offset))
                y_offset += 30  # Incrementa o offset vertical para a próxima linha