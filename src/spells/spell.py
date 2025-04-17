from typing import List
from rune import Rune

class Spell:
    def __init__(self, name: str, runes: List[Rune], mana_cost: int):
        self.name = name                  # Nome do feitiço
        self.runes = runes                # Lista de runas que compõem o feitiço
        self.compiled_effect = None       # Função resultante da combinação das runas
        self.mana_cost = mana_cost        # Custo total de mana para lançar o feitiço


    def execute(self, caster):
        pass  # Executa o efeito do feitiço
