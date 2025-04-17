from rune import Rune
from spell import Spell
from typing import List

class SpellSystem:
    def __init__(self):
        self.runes: List[Rune] = []          # Runas disponíveis no sistema
        self.spellbook: List[Spell] = []     # Feitiços conhecidos ou salvos

    def cast_spell(self, spell: Spell):
        pass  # Realiza a execução de um feitiço selecionado

    def combine_runes(self, runes: List[Rune]) -> Spell:
        pass  # Junta várias runas para formar um novo feitiço

    def add_rune(self, rune: Rune):
        pass  # Adiciona uma nova runa ao sistema

    def remove_rune(self, rune: Rune):
        pass  # Remove uma runa do sistema
