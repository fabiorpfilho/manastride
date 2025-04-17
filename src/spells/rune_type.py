from enum import Enum


class RuneType(Enum):
    COMMAND = "COMMAND"      # Representa ações diretas, como lançar projéteis
    CONDITION = "CONDITION"  # Representa condições (ex: se inimigo está próximo)
    LOOP = "LOOP"            # Representa repetições (ex: repetir feitiço)
    # FUNCTION = "FUNCTION"    # Representa blocos reutilizáveis de lógica
    OPERATOR = "OPERATOR"    # Representa operadores lógicos ou matemáticos
    MODIFIER = "MODIFIER"    # Modifica atributos do feitiço (ex: dano, duração)