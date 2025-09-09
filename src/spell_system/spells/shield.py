from spell_system.spell import Spell
from spell_system.rune import Rune
from objects.static_objects.barrier import Barrier
from typing import List, Optional
import pygame
from objects.dynamic_objects.shield_instance import ShieldInstance
from dataclasses import dataclass
from typing import Optional, List, Any

@dataclass
class ShieldData:
    """Data structure for shield attributes."""
    health: float
    duration: float
    owner: Any
    facing_right: bool
    spawn_time: Optional[int] = None
    stack_position: int = 0  # Mantido para compatibilidade

class Shield(Spell):
    def __init__(self, major_rune: Optional[Rune] = None, minor_runes: List[Rune] = None):
        super().__init__(
            base_attributes={"health": 20, "mana_cost": 20},  # Saúde padrão
            major_rune=major_rune,
            minor_runes=minor_runes or [],
            cooldown=5.0  # Cooldown de 5 segundos entre escudos
        )
        self.shields: List[ShieldInstance] = []  # Escudos ativos na tela
        self.pending_shields: List[ShieldData] = []  # Escudos esperando o tempo de spawn
        self.owner = None  # Referência a entidade que possui o escudo
        self.duration = 10.0  # Duração do escudo em segundos
        # self.shield_sfx = pygame.mixer.Sound("assets/audio/soundEffects/spells/Shield Activation.ogg")  # Som de ativação
        # self.shield_hit_sfx = pygame.mixer.Sound("assets/audio/soundEffects/spells/Shield Hit.ogg")  # Som de impacto

    def execute(self, direction: float, owner) -> None:
        """Executa o feitiço, criando escudos com base nas runas."""
        self.owner = owner
        # Toca o som de ativação
        # self.shield_sfx.play()
        if self.shields:
            if self.major_rune and self.major_rune.name == "fan":
                return 0
            # Reseta a saúde e o timer do escudo existente
            if self.shields[0].health <= 0 or self.shields[0].marked_for_removal:
                self.shields[0].health = self.attributes["health"] if not self.major_rune or self.major_rune.name == "None" else 3
                if not self.major_rune or self.major_rune.name == "None":
                    self.owner.shield_health = self.shields[0].health
            else:
                self.shields[0].health = self.attributes["health"] if not self.major_rune or self.major_rune.name == "None" else 3
                self.shields[0].time_remaining = self.duration
                if not self.major_rune or self.major_rune.name == "None":
                    self.owner.shield_health = self.shields[0].health
            self.current_cooldown = self.cooldown
            return self.attributes["mana_cost"]

        # Calcula a posição base do escudo (à frente do jogador)
        offset_x = 20 if owner.facing_right else -20
        base_position = (owner.position.x + offset_x, owner.position.y)

        # Configura os dados base do escudo
        base_data = ShieldData(
            health=self.attributes["health"] if not self.major_rune or self.major_rune.name == "None" else 3,
            duration=self.duration,
            owner=owner,
            facing_right=direction == 1
        )

        rune_handlers = {
            "None": self._handle_no_rune,
            "multiple": self._handle_multiple_rune,
            "fan": self._handle_fan_rune 
        }
        print("Runa usada:", self.major_rune.name if self.major_rune else "None")
        handler = rune_handlers.get(self.major_rune.name if self.major_rune else "None")
        if handler:
            handler(base_data, base_position)
        self.current_cooldown = self.cooldown
        return self.attributes["mana_cost"]

    def _handle_no_rune(self, base_data: ShieldData, base_position: tuple) -> None:
        """Cria um único escudo sem pendência."""
        shield = ShieldInstance(
            position=base_position,
            health=base_data.health,
            owner=base_data.owner,
            duration=base_data.duration,
        )
        self.shields.append(shield)
        self.owner.shield_health = base_data.health

    def _handle_multiple_rune(self, base_data: ShieldData, base_position: tuple) -> None:
        """Cria um único escudo com três vidas."""
        shield = ShieldInstance(
            position=base_position,
            health=base_data.health,
            owner=base_data.owner,
            duration=base_data.duration,
            is_multiple=True
        )
        self.shields.append(shield)
        # Não atualiza shield_health para "multiple"
    
    def _handle_fan_rune(self, base_data: ShieldData, base_position: tuple) -> None:
        """Cria uma única barreira estática para a runa 'fan' que desaparece após a duração."""
        # Tamanho da barreira
        barrier_size = (10, 40)  # Mantido conforme fornecido

        # Calcula a posição para alinhar o bottom da barreira com o bottom do jogador
        offset_x = 20 if base_data.facing_right else -20
        offset_y = -0  # Deslocamento para cima para "subir mais" a barreira
        barrier_position = (
            base_data.owner.position.x + offset_x,
            base_data.owner.rect.bottom - barrier_size[1] + offset_y  # Alinha com o bottom e ajusta para cima
        )

        # Cria a barreira
        barrier = Barrier(
            position=barrier_position,
            size=barrier_size,
            duration=base_data.duration,  # Duração de 10 segundos
            owner=base_data.owner,
            facing_right=base_data.facing_right
        )

        # Adiciona a barreira à lista de escudos para gerenciamento
        self.shields.append(barrier)
        # Não atualiza owner.shield_health para runa "fan", conforme lógica existente

    def _create_shield(self, data: ShieldData, base_position: tuple) -> ShieldInstance:
        """Cria uma instância de escudo a partir dos dados fornecidos."""
        return ShieldInstance(
            position=base_position,
            health=data.health,
            owner=data.owner,
            duration=data.duration,
            is_multiple=True
        )

    def update(self, delta_time: float):
        """Atualiza todos os escudos ativos e pendentes."""
        current_time = pygame.time.get_ticks()

        # Spawn escudos pendentes (não usado para "fan" ou "multiple" agora)
        for pending in self.pending_shields[:]:
            if pending.spawn_time is None or current_time >= pending.spawn_time:
                shield = self._create_shield(pending, (self.owner.position.x + (20 if self.owner.facing_right else -20), self.owner.position.y))
                self.shields.append(shield)
                self.pending_shields.remove(pending)
                if not self.major_rune or self.major_rune.name == "None":
                    self.owner.shield_health = pending.health  # Atualiza apenas para "None"

        # Atualizar escudos ativos
        for shield in self.shields[:]:
            # Chama update com argumentos apenas para ShieldInstance
            if isinstance(shield, ShieldInstance):
                shield.update(delta_time, self.owner.shield_health, self.owner.on_ground)
            else:
                shield.update(delta_time)  # Barrier não usa shield_health ou on_ground
            if shield.marked_for_removal:
                self.shields.remove(shield)
                if shield.owner:
                    self.owner.shield_health = 0 if not self.shields else self.shields[0].health if not self.major_rune or self.major_rune.name == "None" else 0