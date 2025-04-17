from rune_type import RuneType
from typing import Callable

class Rune:
    def __init__(self, name: str, type: RuneType, effect: Callable, cost: int):
        self.name = name              # Nome da runa
        self.type = type              # Tipo da runa, baseado no enum RuneType
        self.effect = effect          # Função que define o efeito da runa
        self.cost = cost              # Custo de mana ou recurso
