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
        

    def validate(self, owner=None):
        print("Validando spell...: ", self)
        """Verifica se as runas são válidas."""
        if self.major_rune and self.major_rune.rune_type != RuneType.MAJOR:
            return False
        if len(self.minor_runes) > 2:
            return False
        if any(r.rune_type != RuneType.MINOR for r in self.minor_runes):
            return False
        if owner.mana < self.mana_cost:
            print("Mana insuficiente para lançar o feitiço.", self.mana_cost, owner.mana)
            return False
        return True

    def execute(self, direction, owner, player_pos=None):
        """Executa a spell somente se o cooldown terminou."""
        return self.mana_cost

    def update(self, delta_time, player_pos=None):
        """Atualiza o cooldown da spell."""
        if self.current_cooldown > 0:
            self.current_cooldown = max(0.0, self.current_cooldown - delta_time)

    def update_runes(self, rune):
        if rune.rune_type == RuneType.MAJOR:
            if self.major_rune == rune:
                self.major_rune = None
            else: 
                self.major_rune = rune
        elif rune.rune_type == RuneType.MINOR:
            operation_type = 1
            if rune in self.minor_runes:
                self.minor_runes.remove(rune)
                operation_type = -1
            else:
                if len(self.minor_runes) < 2:
                    self.minor_runes.append(rune)
            self.recalculate_attributes(rune, operation_type)

        # Now recalculate instead of inline application

    
    def recalculate_attributes(self, rune, operation_type):
        # Apply major rune effects if any (not shown in original code, so assuming none for now)
        print("eTNROU AQUI")
        # Apply all minor rune effects
        if rune.effect:
            if "power" in rune.effect:
                power = rune.effect["power"]
                if "damage" in self.attributes:
                    self.attributes["damage"] += power * operation_type
                elif "distance" in self.attributes:
                    self.attributes["distance"] += power * operation_type
            if "cost" in rune.effect:
                self.attributes["mana_cost"] += rune.effect["cost"] * operation_type
            if "cooldown" in rune.effect:
                percentage = rune.effect["cooldown"] / 10.0 * operation_type
                self.cooldown *= (1 + percentage)

        # Enforce minimums
        for key in self.attributes:
            self.attributes[key] = max(0, self.attributes[key])
        self.cooldown = max(0.1, self.cooldown)


    def draw(self, surface, camera):
        pass
