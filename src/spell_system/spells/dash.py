from spell_system.spell import Spell
from spell_system.rune import Rune
from typing import List, Optional
import pygame

class Dash(Spell):
    def __init__(self, major_rune: Optional[Rune] = None, minor_runes: List[Rune] = None):
        super().__init__(
            base_attributes={"distance": 150, "mana_cost": 20, "duration": 0.15},
            major_rune=major_rune,
            minor_runes=minor_runes or [],
            cooldown=1.0  # Cooldown de 1 segundo entre dashes
        )

    def execute(self, direction: int, caster):
        """
        direction: 1 para direita, -1 para esquerda
        caster: Player ou outra entidade
        """
        # Lê direto do dicionário de atributos
        distance   = self.attributes.get("distance", 300)
        duration   = self.attributes.get("duration", 0.15)
        mana_cost  = self.attributes.get("mana_cost", 0)

        # Evita divisão por zero
        duration = max(duration, 1e-4)

        dash_speed = distance / duration

        # Aplica o dash
        caster.speed_vector.x += dash_speed * (1 if direction >= 0 else -1)
        caster.speed_vector.y = 0

        # Marca um timer de dash no caster para encerrar o efeito no update
        caster.dash_timer = duration

        # Animação (usa WALK se não existir DASH)
        if hasattr(caster, "animation_manager"):
            anim = getattr(caster.animation_manager.AnimationType, "DASH",
                           caster.animation_manager.AnimationType.WALK)
            caster.set_animation(anim)

        return mana_cost
