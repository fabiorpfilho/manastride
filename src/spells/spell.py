from typing import List
from rune import Rune
from rune_type import RuneType
from spell_effect_type import SpellEffectType


class Spell:
    def __init__(self, name: str, runes: List[Rune], mana_cost: int, effect_type: SpellEffectTté):
        self.name = name                  # Nome do feitiço
        self.runes = runes                # Lista de runas que compõem o feitiço
        self.compiled_effect = None       # Função resultante da combinação das runas
        self.mana_cost = mana_cost        # Custo total de mana para lançar o feitiço
        self.effect_type

    def validate(self):
        """
        Verifica se a sequência de runas forma um feitiço válido.
        Exemplo de validações:
        - Um LOOP deve conter ao menos um comando dentro
        - Uma CONDITION deve ser seguida por um comando ou bloco
        - MODIFIERS devem modificar comandos válidos
        """
        if not self.runes:
            return False

        for i, rune in enumerate(self.runes):
            if rune.rune_type == RuneType.CONDITION:
                if i + 1 >= len(self.runes) or self.runes[i + 1].rune_type != RuneType.COMMAND:
                    return False
            elif rune.rune_type == RuneType.LOOP:
                if i + 1 >= len(self.runes) or self.runes[i + 1].rune_type != RuneType.COMMAND:
                    return False
            elif rune.rune_type == RuneType.MODIFIER:
                if i == 0 or self.runes[i - 1].rune_type != RuneType.COMMAND:
                    return False

        return True

    def execute(self):
        """
        Executa o feitiço interpretando as runas como uma mini linguagem.
        Exemplo: [Fireball] [Dano=5] => Cria e lança um projétil com 5 de dano.
        """
        current_command = None
        modifiers = {}

        for rune in self.runes:
            if rune.rune_type == RuneType.COMMAND:
                current_command = rune.name
                modifiers = {}  # limpa modificadores anteriores

            elif rune.rune_type == RuneType.MODIFIER:
                if current_command:
                    # Espera-se que value seja um dicionário como {"dano": 5}
                    modifiers.update(rune.value)

            # Aqui você pode adicionar outros tipos (CONDITION, LOOP) no futuro

        if self.effect_type == SpellEffectType.PROJECTILE:
            self._launch_projectile(modifiers)
            
    def _launch_projectile(self, modifiers):
        """
        Método genérico para lançar um projétil. Por enquanto só printa,
        """
        dano = modifiers.get("dano", 1)
        velocidade = modifiers.get("velocidade", 10)

        print(f"🔥 Fireball lançada com dano {dano} e velocidade {velocidade}")