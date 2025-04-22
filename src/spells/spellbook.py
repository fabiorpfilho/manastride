from typing import List
from spell import Spell
from spell_system import SpellSystem


class SpellBook:
    def __init__(self):
        self.spells = []  # Lista de feitiços armazenados

    def add_spell(self, spell: Spell):
        # Adiciona um feitiço à coleção
        self.spells.append(spell)

    def get_spell(self, index: int) -> Spell:
        # Retorna um feitiço pelo índice
        return self.spells[index]

    def list_spells(self):
        # Exibe todos os feitiços disponíveis
        for i, spell in enumerate(self.spells):
            print(f"{i}: {spell.runes}")
