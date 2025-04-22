from rune import Rune
from spell import Spell
from typing import List

class SpellSystem:
    def __init__(self):
        self.runes: List[Rune] = []          # Runas disponíveis no sistema
        self.spellbook: List[Spell] = []     # Feitiços conhecidos ou salvos

    def cast_spell(self, spell: Spell):
        # Realiza a execução de um feitiço selecionado
        if spell.validate():
            print(f"Lançando feitiço: {spell.name}")
            spell.execute()
        else:
            print(f"Feitiço inválido: {spell.name}")

    def combine_runes(self, runes: List[Rune]) -> Spell:
        # Junta várias runas para formar um novo feitiço
        name = "Feitiço Combinado"
        mana_cost = sum(rune.cost for rune in self.runes)
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