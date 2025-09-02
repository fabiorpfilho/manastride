from typing import List, Dict, Optional
from spell_system.rune import Rune
from spell_system.rune_type import RuneType


class Spell():
    def __init__(self, base_attributes: dict, major_rune: Optional[Rune] = None, 
                 minor_runes: List[Rune] = None, cooldown: float = 0.0):
        self.attributes = base_attributes.copy()
        self.major_rune = major_rune
        self.minor_runes = minor_runes or []
        self.mana_cost = base_attributes["mana_cost"] + (
            major_rune.cost if major_rune else 0) + sum(r.cost for r in self.minor_runes)
        self.active = False
        self.cooldown = cooldown           # Cooldown total da spell
        self.current_cooldown = 0.0       # Timer de cooldown atual
        self.apply_minor_runes()

    def apply_minor_runes(self):
        """Aplica efeitos das runas menores."""
        for rune in self.minor_runes:
            for key, value in rune.effect.items():
                if key.endswith("_mult"):
                    attr = key.replace("_mult", "")
                    self.attributes[attr] = self.attributes.get(attr, 1) * value
                elif key.endswith("_add"):
                    attr = key.replace("_add", "")
                    self.attributes[attr] = self.attributes.get(attr, 0) + value
                else:
                    self.attributes[key] = value  # Ex: slow, burn

    def validate(self):
        """Verifica se as runas são válidas."""
        if self.major_rune and self.major_rune.rune_type != RuneType.MAJOR:
            return False
        if len(self.minor_runes) > 2:
            return False
        if any(r.rune_type != RuneType.MINOR for r in self.minor_runes):
            return False
        return True

    def execute(self, direction, owner, player_pos=None):
        """Executa a spell somente se o cooldown terminou."""
        return self.mana_cost

    def update(self, delta_time, player_pos=None):
        """Atualiza o cooldown da spell."""
        if self.current_cooldown > 0:
            self.current_cooldown = max(0.0, self.current_cooldown - delta_time)

    def draw(self, surface, camera):
        pass
