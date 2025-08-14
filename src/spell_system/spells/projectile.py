from spell_system.spell import Spell
from spell_system.rune import Rune
from typing import List, Optional, Dict, Tuple
from objects.dynamic_objects.projectile_instance import ProjectileInstance
import pygame
import math
import random
from dataclasses import dataclass

@dataclass
class ProjectileData:
    """Data structure for projectile attributes."""
    direction: float
    speed: float
    damage: float
    effects: Dict[str, float]
    major_rune: str
    minor_runes: List[str]
    owner: any
    facing_right: bool
    spawn_time: Optional[int] = None
    homing: bool = False

class Projectile(Spell):
    """Classe que gerencia o feitiço de projétil e suas instâncias."""
    def __init__(self, major_rune: Optional[Rune] = None, minor_runes: List[Rune] = None):
        super().__init__(
            base_attributes={"damage": 10, "speed": 300, "mana_cost": 20},
            major_rune=major_rune,
            minor_runes=minor_runes or [],
        )
        self.projectiles: List[ProjectileInstance] = []  # Projéteis ativos na tela
        self.pending_projectiles: List[ProjectileData] = []  # Projéteis esperando o tempo de spawn
        self.marked_for_removal: bool = False
        
        
        self.fireball_sfx = [
            pygame.mixer.Sound("assets/audio/soundEffects/spells/Fireball 1.ogg"),
            pygame.mixer.Sound("assets/audio/soundEffects/spells/Fireball 2.ogg"),
            pygame.mixer.Sound("assets/audio/soundEffects/spells/Fireball 3.ogg"),
        ]
        self.icebolt_sfx = [
            pygame.mixer.Sound("assets/audio/soundEffects/spells/Ice Barrage 1.ogg"),
            pygame.mixer.Sound("assets/audio/soundEffects/spells/Ice Barrage 2.ogg"),
        ]
        self.spell_hit_sfx = [
            pygame.mixer.Sound("assets/audio/soundEffects/spells/Spell Impact 1.ogg"),
            pygame.mixer.Sound("assets/audio/soundEffects/spells/Spell Impact 2.ogg"),
            pygame.mixer.Sound("assets/audio/soundEffects/spells/Spell Impact 3.ogg"),
        ]

    def execute(self, direction: float, owner) -> None:
        """Executa o feitiço, criando projéteis com base nas runas."""
        if not self.validate():
            return

        effects = {k: v for k, v in self.attributes.items() if k in ["slow", "burn"]}
        minor_rune_names = [rune.name for rune in self.minor_runes]
        if "Ice" in minor_rune_names:
            random.choice(self.icebolt_sfx).play()
        elif "Fire" in minor_rune_names:
            random.choice(self.fireball_sfx).play()

        base_data = ProjectileData(
            direction=direction,
            speed=self.attributes["speed"],
            damage=self.attributes["damage"],
            effects=effects,
            major_rune="Default",
            minor_runes=minor_rune_names,
            owner=owner,
            facing_right=direction == 1
        )

        rune_handlers = {
            "None": self._handle_no_rune,
            "Fan": self._handle_fan_rune,
            "Multiple": self._handle_multiple_rune,
            "Homing": self._handle_homing_rune
        }

        handler = rune_handlers.get(self.major_rune.name if self.major_rune else "None")
        if handler:
            handler(base_data, owner)
            
    def _handle_no_rune(self, base_data: ProjectileData, owner) -> None:
        """Cria um único projétil com atraso, semelhante ao Multiple."""
        projectile_dict = base_data.__dict__.copy()
        projectile_dict['major_rune'] = "Default"
        projectile_data = ProjectileData(**projectile_dict)
        self.pending_projectiles.append(projectile_data)

    def _handle_fan_rune(self, base_data: ProjectileData, owner) -> None:
        """Cria projéteis em leque."""
        base_angle = 0.5 if base_data.facing_right else math.pi - 0.5
        angles = [base_angle + (i * 0.1) - 0.2 for i in range(5)]
        for angle in angles:
            # Create a copy of base_data.__dict__ and update direction
            projectile_dict = base_data.__dict__.copy()
            projectile_dict['direction'] = angle
            projectile_dict['damage'] = base_data.damage * 0.6
            projectile_dict['major_rune'] = "Fan"
            projectile_data = ProjectileData(**projectile_dict)
            self.pending_projectiles.append(projectile_data)

    def _handle_multiple_rune(self, base_data: ProjectileData, owner) -> None:
        """Cria múltiplos projéteis com atraso."""
        for i in range(3):
            # Create a copy of base_data.__dict__ and update spawn_time
            projectile_dict = base_data.__dict__.copy()
            projectile_dict['spawn_time'] = pygame.time.get_ticks() + (i * 200)
            projectile_dict['major_rune'] = "Multiple"
            projectile_data = ProjectileData(**projectile_dict)
            self.pending_projectiles.append(projectile_data)

    def _handle_homing_rune(self, base_data: ProjectileData, owner) -> None:
        """Cria um projétil teleguiado."""
        projectile_data = ProjectileData(
            **base_data.__dict__,
            homing=True,
            major_rune="Homing"
        )
        self.pending_projectiles.append(projectile_data)

    def _create_projectile(self, data: ProjectileData, position: Tuple[float, float]) -> ProjectileInstance:
        """Cria uma instância de projétil a partir dos dados fornecidos."""
        return ProjectileInstance(
            position=position,
            size=(10, 10),
            speed=data.speed,
            damage=data.damage,
            direction=data.direction,
            effects=data.effects,
            major_rune_name=data.major_rune,
            minor_rune_names=data.minor_runes,
            owner=data.owner,
            facing_right=data.facing_right,
            homing=data.homing,
            hit_sfx=self.spell_hit_sfx
        )

    def draw(self, surface: pygame.Surface, camera) -> None:
        """Desenha todos os projéteis ativos."""
        for proj in self.projectiles:
            proj.draw(surface, camera)
            

    def update(self, delta_time: float, player_pos: Tuple[float, float]) -> None:
        """Atualiza todos os projéteis ativos e pendentes."""
        current_time = pygame.time.get_ticks()

        # Spawn projéteis pendentes
        for pending in self.pending_projectiles[:]:
            if pending.spawn_time is None or current_time >= pending.spawn_time:
                self.projectiles.append(self._create_projectile(pending, player_pos))
                self.pending_projectiles.remove(pending)

        # Atualizar projéteis ativos
        for proj in self.projectiles[:]:
            proj.update(delta_time)
            if proj.marked_for_removal:
                self.projectiles.remove(proj)