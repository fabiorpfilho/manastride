from objects.entity_with_animation import EntityWithAnimation
import pygame
import math
from typing import List
import pygame
from config import SPEED
import math
import random

class ProjectileInstance(EntityWithAnimation):
    """Representa um projétil individual disparado na tela."""
    def __init__(self, position: tuple, size: tuple, speed: float, damage: float, direction: float,
                 effects: dict, major_rune_name: str, minor_rune_names: List[str], owner,
                 facing_right: bool, homing: bool = False, hit_sfx: List[pygame.mixer.Sound] = None):
        super().__init__(position=position, size=size, sprite=(255, 0, 0))
        self.name="Projectile"
        self.tag = "projectile"
        self.position = pygame.Vector2(position)
        self.size = pygame.Vector2(size)
        self.speed = speed
        self.damage = damage
        self.direction = direction
        self.effects = effects
        self.major_rune_name = major_rune_name
        self.minor_rune_names = minor_rune_names
        self.owner = owner
        self.facing_right = facing_right
        self.homing = homing
        self.hit_sfx = hit_sfx or []
        self.start_x = position[0]
        self.start_y = position[1]
        self.marked_for_removal = False
        self.dx = math.cos(direction) if major_rune_name == "Fan" else 0
        self.dy = -math.sin(direction) if major_rune_name == "Fan" else 0
        self.already_hit_targets = set()
        self.add_collider((0, 0), (self.size.x, self.size.y),
                          type='body', active=True)
        self.add_collider((0, 0), (self.size.x, self.size.y),
                          type='attack_box', active=True)

    def update(self, delta_time: float, max_distance: float = 500):
        """Atualiza a posição do projétil."""
        if self.major_rune_name == "Fan":
            self.position.x += self.dx * (self.speed + SPEED) * delta_time
            self.position.y += self.dy * (self.speed + SPEED) * delta_time
            distance_traveled = math.hypot(self.position.x - self.start_x, self.position.y - self.start_y)
        else:
            self.position.x += self.direction * (self.speed + SPEED) * delta_time
            distance_traveled = abs(self.position.x - self.start_x)

        if distance_traveled > max_distance:
            self.marked_for_removal = True

    def draw(self, surface, camera):
        """Desenha o projétil na tela."""
        screen_pos = camera.apply(pygame.Rect(self.position.x, self.position.y, 0, 0)).center
        color = (255, 0, 0)  # Padrão: vermelho
        if "Ice" in self.minor_rune_names:
            color = (0, 200, 255)  # Ice: azul
        elif "Fire" in self.minor_rune_names:
            color = (255, 100, 0)  # Fire: laranja

        if self.major_rune_name == "Fan":
            pygame.draw.circle(surface, color, screen_pos, 3 * camera.zoom)
        elif self.major_rune_name == "Multiple":
            pygame.draw.circle(surface, color, screen_pos, 3 * camera.zoom)
        elif self.major_rune_name == "Homing":
            points = [
                (screen_pos[0], screen_pos[1] - 5),
                (screen_pos[0] - 5, screen_pos[1] + 5),
                (screen_pos[0] + 5, screen_pos[1] + 5)
            ]
            pygame.draw.polygon(surface, color, points)
        else:
            pygame.draw.circle(surface, color, screen_pos, 5 * camera.zoom)
            
    def handle_hit(self):
        """Toca o som de colisão."""
        random.choice(self.hit_sfx).play()