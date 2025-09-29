from spell_system.rune import Rune
from spell_system.spell import Spell
from typing import List
from spell_system.spells.projectile import Projectile
from spell_system.spells.dash import Dash
from spell_system.spells.shield import Shield
import pygame


class SpellSystem:
    def __init__(self):
        self.runes: List[Rune] = []
        self.spellbook: List[Spell] = [None, None, None]
        self.setup_default_spells()

    def setup_default_spells(self):
        """Initialize spellbook with default spells in fixed order."""
        self.spellbook[0] = Projectile(major_rune=None, minor_runes=[])
        self.spellbook[1] = Dash(major_rune=None, minor_runes=[])
        self.spellbook[2] = Shield(major_rune=None, minor_runes=[])

    def cast_spell(self, index: int, direction, owner):
        """Casts a spell from the spellbook based on the provided numeric index."""
        spell_index = index - 1
        if 0 <= spell_index < len(self.spellbook) and self.spellbook[spell_index] is not None:
            spell = self.spellbook[spell_index]
            if spell.validate() and spell.current_cooldown <= 0:
                print(f"Casting spell at index {index} with direction {direction}")
                mana_cost = spell.execute(direction, owner)
                return mana_cost
            else:
                print(f"Feitiço inválido ou em cooldown, index: {spell_index}")
                return 0
        else:
            print(f"Nenhum feitiço no índice {index}")

    def add_rune(self, rune: Rune):
        print(f"Adicionando a runa {rune}")
        print("Efeito da runa: ", rune.effect)
        """Add a new rune to the system."""
        self.runes.append(rune)

    def remove_rune(self, rune: Rune):
        """Remove a rune from the system."""
        if rune in self.runes:
            self.runes.remove(rune)

    def update(self, delta_time: float, player_pos: List[float]):
        """Atualiza cooldowns, projéteis e escudos."""
        for spell in self.spellbook:
            if not spell:
                continue

            # --- Reduz cooldown ---
            if spell.current_cooldown > 0:
                spell.current_cooldown = max(0.0, spell.current_cooldown - delta_time)

            # --- Atualiza projéteis ---
            if hasattr(spell, "projectiles"):
                spell.update(delta_time, player_pos)  # apenas lógica de projéteis
                for proj in spell.projectiles:
                    proj.sync_position()

            # --- Atualiza escudos ---
            if hasattr(spell, "shields"):
                spell.update(delta_time)  # apenas lógica de escudos
                for shield in spell.shields:
                    shield.sync_position()

    def update_spell(self, index: int, major_rune: Rune = None, minor_runes: List[Rune] = None):
        """
        Atualiza o feitiço no índice dado, aplicando toggle de runas
        (remove se já estiver vinculada), garantindo exclusividade
        entre feitiços e respeitando limites de major/minor.
        """
        spell_index = index - 1
        if spell_index not in [0, 1, 2]:
            print(f"Índice inválido: {index}. Use 1 (Projectile), 2 (Dash) ou 3 (Shield).")
            return

        current_spell = self.spellbook[spell_index]
        minor_runes = minor_runes or []

        # --- Toggle Major ---
        if major_rune and current_spell.major_rune == major_rune:
            major_rune = None  # desativa se já estava

        # --- Toggle Minor ---
        new_minor_runes = list(current_spell.minor_runes)  # cópia
        for r in minor_runes:
            if r in new_minor_runes:
                new_minor_runes.remove(r)  # toggle → remove
            else:
                new_minor_runes.append(r)  # adiciona

        # Garantir limite de 2 minors
        if len(new_minor_runes) > 2:
            new_minor_runes = new_minor_runes[:2]

        # --- Exclusividade: remover runas iguais de outros feitiços ---
        for i, spell in enumerate(self.spellbook):
            if spell is None or i == spell_index:
                continue

            # Major única
            if major_rune and spell.major_rune == major_rune:
                spell.major_rune = None

            # Minors únicas
            spell.minor_runes = [r for r in spell.minor_runes if r not in new_minor_runes]
        print(f"Feitiço no índice {index} atualizado: Major={major_rune}, Minors={new_minor_runes}")
        # --- Reatribuir feitiço atualizado ---
        if spell_index == 0:
            self.spellbook[0] = Projectile(major_rune=major_rune, minor_runes=new_minor_runes)
        elif spell_index == 1:
            self.spellbook[1] = Dash(major_rune=major_rune, minor_runes=new_minor_runes)
        elif spell_index == 2:
            self.spellbook[2] = Shield(major_rune=major_rune, minor_runes=new_minor_runes)
