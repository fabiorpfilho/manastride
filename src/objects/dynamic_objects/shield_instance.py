from objects.entity_with_sprite import EntityWithSprite
import pygame
import math
from typing import Optional, List

class ShieldInstance(EntityWithSprite):
    def __init__(self, position: tuple, health: float,owner, hit_sfx: List[pygame.mixer.Sound] = None):
        super().__init__(position=position, size=(29,16), image=(0, 255, 255))  # Cor ciano como fallback
        self.tag = "shield"
        self.health = health
        self.owner = owner
        self.hit_sfx = hit_sfx or []
        self.marked_for_removal = False
        self.levitation_amplitude = 5  # Distância de levitação
        self.levitation_speed = 2  # Velocidade de oscilação
        self.levitation_timer = 0
        
        self.base_y_offset = -10
        self.base_y = owner.position.y + self.base_y_offset
        self.offset_x = -4

        # Carrega a imagem do escudo
        self.image = self.asset_loader.load_image("assets/spells/shield.png")


    def update(self, delta_time: float, owner_shield_health):
            """Atualiza a posição e levitação do escudo."""
            if owner_shield_health <= 0:
                self.marked_for_removal = True
                return

            # Atualiza a posição x para seguir o jogador
            if self.owner:
                self.position.x = self.owner.position.x + self.offset_x

            # Atualiza levitação em relação à posição base
            self.levitation_timer += delta_time * self.levitation_speed
            offset_y = math.sin(self.levitation_timer) * self.levitation_amplitude
            self.position.y = self.base_y + offset_y

            # Atualiza o retângulo e colisores
            self.sync_position()


    def draw(self, surface: pygame.Surface, camera):
        """Desenha o escudo na tela."""
        pass


    def handle_hit(self):
        """Toca o som de impacto ao bloquear um ataque."""
        if self.hit_sfx:
            self.hit_sfx.play()