from spell_system.spell import Spell
from spell_system.rune import Rune
from typing import List, Optional
import pygame
import math


class Dash(Spell):
    def __init__(self, major_rune: Optional[Rune] = None, minor_runes: List[Rune] = None):
        super().__init__(
            base_attributes={"distance": 150, "mana_cost": 25, "duration": 0.15},
            major_rune=major_rune,
            minor_runes=minor_runes or [],
            cooldown=1.0  # Cooldown de 1 segundo entre dashes
        )

        # Inicialização das variáveis específicas de runas
        if self.major_rune and self.major_rune.name.lower() == "multiple":
            self.remaining_charges = 0
            self.delay_timer = 0.0
            self.max_charges = 3
            self.delay_duration = 2.0
            self.short_distance = 100
        else:
            self.remaining_charges = None
            self.delay_timer = None
            self.max_charges = None
            self.delay_duration = None
            self.short_distance = None


    def execute(self, direction: int, caster):
        """
        direction: 1 para direita, -1 para esquerda
        caster: Player ou outra entidade
        """
        print("Passou aqui 1")

        mana_cost = self.attributes.get("mana_cost", 10)
        distance = self.attributes.get("distance", 150)
        duration = self.attributes.get("duration", 0.15)
        duration = max(duration, 1e-4)

        # Escolhe qual dash executar
        if self.major_rune and self.major_rune.name.lower() == "multiple":
            mana_cost, distance = self._execute_multiple_dash(caster)
        elif self.major_rune and self.major_rune.name.lower() == "fan":
            dx, dy = self._execute_fan_dash(direction)
        else:
            dx, dy = self._execute_normal_dash(direction)

        # Se o dash foi do tipo multiple, o dx/dy vem do último dash (horizontal)
        if not (self.major_rune and self.major_rune.name.lower() == "fan"):
            dx, dy = 1 if direction >= 0 else -1, 0

        dash_speed = distance / duration

        # Normaliza o vetor de direção
        magnitude = math.sqrt(dx ** 2 + dy ** 2)
        if magnitude > 0:
            dx /= magnitude
            dy /= magnitude

        # Aplica a velocidade
        caster.speed_vector.x = dx * dash_speed
        caster.speed_vector.y = dy * dash_speed
        caster.dash_timer = duration

        # Animação
        if hasattr(caster, "animation_manager"):
            anim = getattr(caster.animation_manager.AnimationType, "DASH",
                          caster.animation_manager.AnimationType.WALK)
            caster.set_animation(anim)

        # Som e cooldown
        if not (self.major_rune and self.major_rune.name.lower() == "multiple" and self.remaining_charges > 0):
            print(f"Dash executado: direção {direction}, distância {distance}, duração {duration}, velocidade {dash_speed:.2f}")
            self.current_cooldown = self.cooldown

        pygame.mixer.Sound("assets/audio/soundEffects/spells/dash.mp3").play()
        return mana_cost


    # ======================================================
    # FUNÇÕES SEPARADAS POR TIPO DE DASH
    # ======================================================

    def _execute_normal_dash(self, direction: int):
        """Dash horizontal simples."""
        dx = 1 if direction >= 0 else -1
        dy = 0
        return dx, dy


    def _execute_fan_dash(self, direction: int):
        """Dash com runa 'Fan' — permite diagonais e vertical."""
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_UP] and not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
            dx, dy = 0, -1
        elif keys[pygame.K_UP] and keys[pygame.K_RIGHT]:
            angle = math.radians(45) if direction >= 0 else math.radians(135)
            dx = math.cos(angle)
            dy = -math.sin(angle)
        elif keys[pygame.K_UP] and keys[pygame.K_LEFT]:
            angle = math.radians(135)
            dx = math.cos(angle)
            dy = -math.sin(angle)
        else:
            dx = 1 if direction >= 0 else -1
            dy = 0

        return dx, dy


    def _execute_multiple_dash(self, caster):
        """Dash com runa 'Multiple' — 3 dashes rápidos."""
        # Quando as cargas acabaram (ou é o primeiro uso), reinicia e cobra mana
        if self.remaining_charges is None or self.remaining_charges <= 0:
            self.remaining_charges = self.max_charges
            mana_cost = self.attributes["mana_cost"]
            # 🔹 Define o custo de mana para zero após o primeiro uso,
            #    para que as próximas cargas não cobrem novamente
            self.mana_cost = 0
        else:
            # Dashes subsequentes na sequência múltipla não têm custo
            mana_cost = 0

        distance = self.short_distance
        self.remaining_charges -= 1

        if self.remaining_charges > 0:
            self.delay_timer = self.delay_duration
        else:
            self.delay_timer = 0
            # 🔹 Quando as cargas acabam, restaura o custo normal de mana
            self.mana_cost = self.attributes["mana_cost"]

        return mana_cost, distance



    def update_runes(self, rune):
        print("Update rune")
        super().update_runes(rune)
        if rune and rune.name.lower() == "multiple":
            print("Update rune 2")
            self.remaining_charges = 0
            self.delay_timer = 0.0
            self.max_charges = 3
            self.delay_duration = 1.0
            self.short_distance = 100
