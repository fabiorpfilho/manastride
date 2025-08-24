from spell_system.spell import Spell
from spell_system.rune import Rune
from typing import List, Optional
import pygame
from objects.dynamic_objects.shield_instance import ShieldInstance

class Shield(Spell):
    def __init__(self, major_rune: Optional[Rune] = None, minor_runes: List[Rune] = None):
        super().__init__(
            base_attributes={"health": 20, "mana_cost": 20},
            major_rune=major_rune,
            minor_runes=minor_runes or [],
        )
        self.shields: List[ShieldInstance] = []  # Escudos ativos na tela
        self.owner = None  # Referência a entidade que possui o escudo
        # self.shield_sfx = pygame.mixer.Sound("assets/audio/soundEffects/spells/Shield Activation.ogg")  # Som de ativação
        # self.shield_hit_sfx = pygame.mixer.Sound("assets/audio/soundEffects/spells/Shield Hit.ogg")  # Som de impacto

    def execute(self, direction: float, owner) -> None:
        """Executa o feitiço, criando um escudo na frente do jogador."""
        self.owner = owner
        # Toca o som de ativação
        # self.shield_sfx.play()

        # Calcula a posição do escudo (à frente do jogador)
        offset_x = 20 if owner.facing_right else -20  # Deslocamento horizontal
        position = (owner.position.x + offset_x, owner.position.y)
        

        # Cria a instância do escudo
        shield = ShieldInstance(
            position=position,
            health=self.attributes["health"],
            owner=owner,
            # hit_sfx=self.shield_hit_sfx
        )
        self.shields.append(shield)

        # Atualiza a saúde do escudo do jogador (se necessário)
        owner.shield_health = self.attributes["health"]

        # Retorna o custo de mana para dedução
        return self.attributes["mana_cost"]

    def update(self, delta_time: float):
        """Atualiza todos os escudos ativos."""
        for shield in self.shields[:]:
            shield.update(delta_time, self.owner.shield_health)
            if shield.marked_for_removal:
                self.shields.remove(shield)
                if shield.owner:
                    shield.owner.shield_health = 0  # Reseta a saúde do escudo do jogador

    def draw(self, surface: pygame.Surface, camera) -> None:
        """Desenha todos os escudos ativos."""
        for shield in self.shields:
            shield.draw(surface, camera)