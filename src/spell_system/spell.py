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
        
        for rune in self.minor_runes:
            print("Aplicando efeito da runa menor:", rune.effect)
            print("Tipo de runa:", rune.rune_type)
            if rune.rune_type == RuneType.MINOR and rune.effect:
                # Modifica atributos com base no effect da runa
                if "power" in rune.effect:
                    print("Aumentando poder da runa menor:", rune.effect["power"])
                    self.attributes["damage"] = max(0, self.attributes["damage"] + rune.effect["power"])
                    print("Poder atual:", self.attributes["damage"])
                if "cost" in rune.effect:
                    print("Modificando custo da runa menor:", rune.effect["cost"])
                    self.attributes["mana_cost"] = max(0, self.attributes["mana_cost"] + rune.effect["cost"])
                    print("Custo atual:", self.attributes["mana_cost"])
                if "cooldown" in rune.effect:
                    print("Modificando cooldown da runa menor:", rune.effect["cooldown"])
                    # Interpreta o valor como porcentagem (ex.: -5 = -50%, 5 = +50%)
                    percentage = rune.effect["cooldown"] / 10.0  # Converte para fração (ex.: -5 -> -0.5, 5 -> 0.5)
                    self.cooldown = max(0.1, self.cooldown * (1 + percentage))  # Aplica a porcentagem
                    print("Cooldown atual:", self.cooldown)

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
