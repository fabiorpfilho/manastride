from spell_system.rune import Rune
from spell_system.rune_type import RuneType
from spell_system.spell import Spell
from typing import List
from spell_system.spells.projectile import Projectile
from spell_system.spells.dash import Dash
from spell_system.spells.shield import Shield
import pygame

class SpellSystem:
    def __init__(self):
        self.runes: List[Rune] = []  # Runas disponíveis no sistema
        self.spellbook: List[Spell] = [None, None, None]  # Feitiços fixos: [Projectile, Dash, Shield]

        self.setup_default_spells()

    def setup_default_spells(self):
        """Initialize spellbook with default spells in fixed order."""
        self.spellbook[0] = Projectile(
            major_rune=None,
            minor_runes=[],
        )
        self.spellbook[1] = Dash(
            major_rune=None,
            minor_runes=[],
        )
        self.spellbook[2] = Shield(
            major_rune=None,
            minor_runes=[],
        )

    def cast_spell(self, index: int, direction, owner):
        """
        Casts a spell from the spellbook based on the provided numeric index.
        Index 1 maps to spellbook[0] (Projectile), index 2 to spellbook[1] (Dash), index 3 to spellbook[2] (Shield).
        """
        print(f"Index: {index}")
        spell_index = index - 1  # Convert input index (1-based) to 0-based
        
        print(f"Spell index: {spell_index}")
        if 0 <= spell_index < len(self.spellbook) and self.spellbook[spell_index] is not None:
            spell = self.spellbook[spell_index]
            if spell.validate():
                spell.execute(direction, owner)
                return spell.mana_cost
            else:
                print(f"Feitiço inválido:, index: {spell_index}")
        else:
            print(f"Nenhum feitiço no índice {index}")

    def add_rune(self, rune: Rune):
        """Add a new rune to the system."""
        self.runes.append(rune)

    def remove_rune(self, rune: Rune):
        """Remove a rune from the system."""
        if rune in self.runes:
            self.runes.remove(rune)

    def update_spell(self, index: int, major_rune: Rune = None, minor_runes: List[Rune] = None):
        """
        Update the spell at the given index with new runes, keeping the spell type fixed.
        Index 1: Projectile, Index 2: Dash, Index 3: Shield.
        """
        spell_index = index - 1  # Convert to 0-based index
        if spell_index not in [0, 1, 2]:
            print(f"Índice inválido: {index}. Use 1 (Projectile), 2 (Dash) ou 3 (Shield).")
            return

        minor_runes = minor_runes or []
        if spell_index == 0:
            self.spellbook[0] = Projectile(major_rune=major_rune, minor_runes=minor_runes)
        elif spell_index == 1:
            self.spellbook[1] = Dash(major_rune=major_rune, minor_runes=minor_runes)
        elif spell_index == 2:
            self.spellbook[2] = Shield(major_rune=major_rune, minor_runes=minor_runes)