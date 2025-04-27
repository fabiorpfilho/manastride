from spells.rune import Rune
from spells.spell import Spell
from typing import List

class SpellSystem:
    def __init__(self):
        self.runes: List[Rune] = []          # Runas disponíveis no sistema
        self.spellbook: List[Spell] = []     # Feitiços conhecidos ou salvos

    def cast_spell(self, index: int, direction):
        """
        Casts a spell from the spellbook based on the provided numeric index.
        Index 1 maps to spellbook[0], index 2 to spellbook[1], etc.
        """
        spell_index = index - 1  # Convert input index (1-based) to 0-based
        if 0 <= spell_index < len(self.spellbook):
            spell = self.spellbook[spell_index]
            if spell.validate():
                print(f"Lançando feitiço: {spell.name}")
                spell.execute(direction)
            else:
                print(f"Feitiço inválido: {spell.name}")
        else:
            print(f"Nenhum feitiço no índice {index}")


    def combine_runes(self, runes: List[Rune]) -> Spell:
        # Junta várias runas para formar um novo feitiço
        name = "Feitiço Combinado"
        mana_cost = sum(rune.cost for rune in runes)
        spell = Spell(name, runes, mana_cost)
        if spell.validate():
            self.spellbook.append(spell)
            return spell
        else:
            print("Falha ao compilar feitiço: combinação inválida.")
            return None

    def add_rune(self, rune: Rune):
        # Adiciona uma nova runa ao sistema
        self.runes.append(rune)

    def remove_rune(self, rune: Rune):
        # Remove uma runa do sistema
        if rune in self.runes:
            self.runes.remove(rune)