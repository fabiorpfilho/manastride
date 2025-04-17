from typing import List
from spell import Spell
from spell_system import SpellSystem

class SpellBook(SpellSystem):
    def __init__(self):
        super().__init__()
        self.equipped_spells: List[Spell] = []  # Feitiços equipados em slots

    def bind_spell_to_slot(self, spell: Spell, slot: int):
        pass  # Associa um feitiço a um slot específico

    def get_spell_from_slot(self, slot: int) -> Spell:
        pass  # Retorna o feitiço associado ao slot especificado
