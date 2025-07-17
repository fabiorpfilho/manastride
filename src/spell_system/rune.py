from spell_system.rune_type import RuneType
from typing import Dict, Optional, Callable

class Rune:
    def __init__(self, name: str, rune_type: RuneType, cost: int, effect: Dict):
        self.name = name
        self.rune_type = rune_type
        self.cost = cost
        # Para MINOR (ex: {"slow": 0.5}) ou MAJOR (ex: {})
        self.effect = effect
