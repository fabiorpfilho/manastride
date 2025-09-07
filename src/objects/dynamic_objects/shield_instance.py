from objects.entity_with_sprite import EntityWithSprite
import pygame
import math
from typing import Optional, List
import random

class ShieldInstance(EntityWithSprite):
    def __init__(self, position: tuple, health: float, owner, duration: float, hit_sfx: List[pygame.mixer.Sound] = None, is_multiple: bool = False):
        super().__init__(position=position, size=(29, 16), image=(0, 255, 255))  # Cor ciano como fallback
        self.tag = "shield"
        self.health = health
        self.owner = owner
        self.hit_sfx = hit_sfx or []
        self.marked_for_removal = False
        self.levitation_amplitude = 5  # Distância de levitação
        self.levitation_speed = 2  # Velocidade de oscilação
        self.levitation_timer = 0
        self.time_remaining = duration  # Tempo restante do escudo
        self.is_multiple = is_multiple
        
        # Ajuste de offset baseado no tipo de escudo
        self.offset_x = -4 if not is_multiple else -2  # Centraliza 21x7 em 29x16 horizontalmente
        self.base_y_offset = -10 if not is_multiple else -12  # Centraliza 7x7 em 16 verticalmente a partir de -10
        self.base_y = owner.position.y + self.base_y_offset

        # Estado para detectar transição chão ↔ ar
        self.last_on_ground = True  

        # Carrega a imagem do escudo com base no tipo e estado
        self.sprite_states = {
            3: "assets/spells/multiple_shield1.png",
            2: "assets/spells/multiple_shield2.png",
            1: "assets/spells/multiple_shield3.png"
        }
        self.image = self.asset_loader.load_image("assets/spells/shield.png" if not is_multiple else self.sprite_states.get(health, "assets/spells/multiple_shield1.png"))
        self.image = self.image.convert_alpha()  # Garante suporte a alpha

    def update(self, delta_time: float, owner_shield_health, on_ground: bool):
        """Atualiza a posição, levitação e timer do escudo."""
        if owner_shield_health <= 0 and not self.is_multiple:
            self.marked_for_removal = True
            return

        if not self.owner:
            return

        # Sempre segue o X do dono, com offset ajustado
        self.position.x = self.owner.position.x + self.offset_x

        # Atualiza timer da levitação
        self.levitation_timer += delta_time * self.levitation_speed
        offset_y = math.sin(self.levitation_timer) * self.levitation_amplitude

        # Detecta quando player acabou de pousar
        if on_ground and not self.last_on_ground:
            self.base_y = self.owner.position.y + self.base_y_offset

        if on_ground:
            # Oscila em torno de base_y fixo
            self.position.y = self.base_y + offset_y
        else:
            # No ar → segue Y do player
            self.position.y = self.owner.position.y + self.base_y_offset + offset_y

        # Atualiza o timer de duração
        self.time_remaining -= delta_time
        if self.time_remaining <= 0:
            self.marked_for_removal = True

        # Configura piscar quando o tempo restante for baixo (menos de 2 segundos)
        if self.time_remaining <= 2.0:
            blink_interval = 0.2  # Intervalo de 0.2 segundos para piscar
            blink_timer = (pygame.time.get_ticks() // int(blink_interval * 1000)) % 2  # Alterna entre 0 e 1
            self.image.set_alpha(0 if blink_timer else 255)  # 0 = invisível, 255 = visível
        else:
            self.image.set_alpha(255)  # Visível normalmente fora do período de piscar

        # Atualiza estado anterior
        self.last_on_ground = on_ground

        # Atualiza colisores
        self.sync_position()

    def handle_damage(self):
        print("Shield hit!")
        """Gerencia o impacto do escudo com base no tipo."""
        if self.is_multiple:
            # random.choice(self.hit_sfx).play()
            self.health -= 1  # Decrementa uma vida, absorvendo o dano completamente
            if self.health > 0:
                self.image = self.asset_loader.load_image(self.sprite_states.get(self.health, "assets/spells/multiple_shield3.png"))
                self.image = self.image.convert_alpha()
            else:
                self.marked_for_removal = True  # Remove após o terceiro hit