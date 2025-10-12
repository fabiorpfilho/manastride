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
        # Novo: Inicializa timers e variáveis para cooldown e multiple
        if self.major_rune and self.major_rune.name.lower() == "multiple":
            self.remaining_charges = 0
            self.delay_timer = 0.0
            self.max_charges = 3
            self.delay_duration = 2.0  # Tempo após o último dash para iniciar cooldown se cargas não esgotadas
            self.short_distance = 100  # Distância curta para dashes multiple (ajuste se necessário)
        else:
            self.remaining_charges = None
            self.delay_timer = None
            self.max_charges = None
            self.delay_duration = None
            self.short_distance = None


    def execute(self, direction: int, caster):
        print("Passou aqui 1")
        """
        direction: 1 para direita, -1 para esquerda
        caster: Player ou outra entidade
        """
        # Novo: Verifica se está em cooldown; se sim, não executa nada

        mana_cost = self.attributes.get("mana_cost", 10)
        distance = self.attributes.get("distance", 150)
        duration = self.attributes.get("duration", 0.15)

        is_multiple = self.major_rune and self.major_rune.name.lower() == "multiple"
        if is_multiple:
            # Lógica para multiple: gerencia cargas e timers
            if self.remaining_charges <= 0:
                # Início de uma nova sequência: paga mana, define cargas máximas
                self.remaining_charges = self.max_charges
                mana_cost = self.attributes["mana_cost"]
            else:
                # Dash adicional: sem custo de mana
                mana_cost = 0
            distance = self.short_distance
            self.remaining_charges -= 1
            if self.remaining_charges > 0:
                # Ainda tem cargas: reseta o delay para dar chance de usar mais
                self.delay_timer = self.delay_duration
            else:
                # Cargas esgotadas: inicia cooldown imediatamente, sem delay
                self.delay_timer = 0
        print("Passou aqui 3")
        duration = max(duration, 1e-4)
        dash_speed = distance / duration

        # Determinar a direção do dash (dx, dy)
        dx, dy = 0, 0
        keys = pygame.key.get_pressed()

        if self.major_rune and self.major_rune.name.lower() == "fan":
            # Dash com runa "Fan" - suporta diagonais e vertical
            if keys[pygame.K_UP] and not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
                # Dash vertical puro (cima)
                dx = 0
                dy = -1
            elif keys[pygame.K_UP] and keys[pygame.K_RIGHT]:
                # Dash diagonal direita+cima
                angle = math.radians(45) if direction >= 0 else math.radians(135)
                dx = math.cos(angle)
                dy = -math.sin(angle)
            elif keys[pygame.K_UP] and keys[pygame.K_LEFT]:
                # Dash diagonal esquerda+cima
                angle = math.radians(135)  # 135 graus para diagonal
                dx = math.cos(angle)
                dy = -math.sin(angle)
            else:
                # Dash horizontal
                dx = 1 if direction >= 0 else -1
                dy = 0
        else:
            # Dash horizontal
            dx = 1 if direction >= 0 else -1
            dy = 0

        # Normalizar o vetor de direção para garantir velocidade consistente
        magnitude = math.sqrt(dx**2 + dy**2)
        if magnitude > 0:
            dx /= magnitude
            dy /= magnitude

        # Aplicar a velocidade ao vetor do caster
        caster.speed_vector.x = dx * dash_speed
        caster.speed_vector.y = dy * dash_speed

        # Definir o temporizador do dash
        caster.dash_timer = duration

        # Animação (usa DASH se disponível, senão WALK)
        if hasattr(caster, "animation_manager"):
            anim = getattr(caster.animation_manager.AnimationType, "DASH",
                          caster.animation_manager.AnimationType.WALK)
            caster.set_animation(anim)
        if not is_multiple or self.remaining_charges == 0:
            print(f"Dash executado: direção {direction}, distância {distance}, duração {duration}, velocidade {dash_speed:.2f}")
            self.current_cooldown = self.cooldown
        pygame.mixer.Sound("assets/audio/soundEffects/spells/dash.mp3").play()
        return mana_cost