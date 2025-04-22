from rune_type import RuneType

class Rune:
    def __init__(self, name: str, rune_type: RuneType, value=None):
        self.name = name            # Nome da runa (ex: "Fireball", "IF", "3x")
        self.rune_type = rune_type  # Tipo da runa, baseado no enum RuneType
        self.value = value          # Valor adicional (ex: número de repetições, condição lógica)
        self.cost = cost            # Custo de mana para usar a runa

    def __repr__(self):
        return f"<Rune {self.name} ({self.rune_type.name})>"
