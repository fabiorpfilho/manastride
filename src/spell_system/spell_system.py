from spell_system.rune import Rune
from spell_system.rune_type import RuneType
from spell_system.spell import Spell
from typing import List
from spell_system.spells.projectile import Projectile

class SpellSystem:
    def __init__(self):
        self.runes: List[Rune] = self.create_runes()         # Runas disponíveis no sistema
        self.spellbook: List[Spell] = []     # Feitiços conhecidos ou salvos
        self.setup_default_spells()
        
    def setup_default_spells(self):
        ice_spell = Projectile(
            major_rune=self.runes[2],
            minor_runes=[self.runes[3]]
        )
        fan_spell = Projectile(
            major_rune=self.runes[0],
            minor_runes=[self.runes[4]]
        )

        self.spellbook.append(ice_spell)
        self.spellbook.append(fan_spell)


    def cast_spell(self, index: int, direction):
        """
        Casts a spell from the spellbook based on the provided numeric index.
        Index 1 maps to spellbook[0], index 2 to spellbook[1], etc.
        """
        spell_index = index - 1  # Convert input index (1-based) to 0-based
        if 0 <= spell_index < len(self.spellbook):
            spell = self.spellbook[spell_index]
            if spell.validate():
                # print(f"Lançando feitiço: {spell.name}")
                spell.execute(direction)
            else:
                print(f"Feitiço inválido: {spell.name}")
        else:
            print(f"Nenhum feitiço no índice {index}")


    def add_rune(self, rune: Rune):
        # Adiciona uma nova runa ao sistema
        self.runes.append(rune)

    def remove_rune(self, rune: Rune):
        # Remove uma runa do sistema
        if rune in self.runes:
            self.runes.remove(rune)
            
    def create_runes(self):
        return [
            Rune(
                name="Fan",
                rune_type=RuneType.MAJOR,
                cost=10,
                effect={}
            ),
            Rune(
                name="Homing",
                rune_type=RuneType.MAJOR,
                cost=12,
                effect={}
            ),
            Rune(
                name="Multiple",
                rune_type=RuneType.MAJOR,
                cost=8,
                effect={}    
            ),
            Rune(
                name="Ice",
                rune_type=RuneType.MINOR,
                cost=5,
                effect={"slow": {"amount": 0.5, "duration": 3}}
            ),
            Rune(
                name="Fire",
                rune_type=RuneType.MINOR,
                cost=6,
                effect={"burn": {"damage": 2, "duration": 3}}
            )
        ]
        

