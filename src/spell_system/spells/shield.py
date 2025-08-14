from spell_system.spell import Spell
from spell_system.rune import Rune
from typing import List, Optional


class Shield(Spell):
    def __init__(self, major_rune: Optional[Rune] = None, minor_runes: List[Rune] = None):
        super().__init__(
            base_attributes={"health": 300, "mana_cost": 20},
            major_rune=major_rune,
            minor_runes=minor_runes or [],
        )

