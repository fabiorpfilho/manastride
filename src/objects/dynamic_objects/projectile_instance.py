from objects.entity_with_animation import EntityWithAnimation
import pygame
import math
from typing import List
from config import SPEED
import random

class ProjectileInstance(EntityWithAnimation):
    """Representa um projétil individual disparado na tela."""
    def __init__(self, position: tuple, size: tuple, speed: float, damage: float, direction: float,
                 effects: dict, major_rune_name: str, minor_rune_names: List[str], owner,
                 facing_right: bool, homing: bool = False, hit_sfx: List[pygame.mixer.Sound] = None):
        super().__init__(position=position, size=size, sprite=(255, 0, 0))
        self.name = "Projectile"
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
        self.add_collider((0, 0), (self.size.x, self.size.y), type='body', active=True)
        self.add_collider((0, 0), (self.size.x, self.size.y), type='attack_box', active=True)

        # Animation setup
        self.current_animation = None
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.1  # Seconds per frame, adjustable
        self.use_animation = "Fire" in self.minor_rune_names or self.major_rune_name == "Default"

        if self.use_animation and self.animation_manager:
            # Load fireball animation
            self.animation_manager.load_animations_from_json(
                self.size,
                image_path="assets/spells/fire/Firebolt SpriteSheet.png",
                json_path="assets/spells/fire/Firebolt SpriteSheet.json"
            )
            if not self.animation_manager.animationList:
                print("Erro: Nenhuma animação de fireball carregada")
                self.use_animation = False  # Fallback to circle if animation fails
            else:
                self.set_animation(self.animation_manager.AnimationType.ATTACK1)

    def set_animation(self, animation_type):
        """Set the current animation based on type."""
        if not self.animation_manager:
            print("Aviso: Nenhum AnimationManager fornecido")
            return
        for animation in self.animation_manager.animationList:
            if animation.type == animation_type:
                if self.current_animation != animation:
                    self.current_animation = animation
                    self.current_frame = 0
                    self.animation_timer = 0
                    self.update_image()
                return
        print(f"Aviso: Animação {animation_type} não encontrada")
        self.use_animation = False  # Fallback to circle if animation not found

    def update_animation(self, delta_time: float):
        """Update the animation frame."""
        if not self.use_animation or not self.animation_manager or not self.current_animation:
            return

        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_speed:
            self.animation_timer -= self.animation_speed
            self.current_frame = (self.current_frame + 1) % len(self.current_animation.animation)
            self.update_image()

    def update_image(self):
        """Update the projectile's image based on the current animation frame."""
        if self.current_animation and self.current_animation.animation:
            sprite = self.current_animation.animation[self.current_frame].image
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)
            self.image = sprite
            self.rect = self.image.get_rect(topleft=(self.position.x, self.position.y))
        else:
            self.image.fill(self.sprite)  # Fallback to default sprite

    def update(self, delta_time: float, max_distance: float = 500):
        """Atualiza a posição e a animação do projétil."""
        if self.major_rune_name == "Fan":
            self.position.x += self.dx * (self.speed + SPEED) * delta_time
            self.position.y += self.dy * (self.speed + SPEED) * delta_time
            distance_traveled = math.hypot(self.position.x - self.start_x, self.position.y - self.start_y)
        else:
            self.position.x += self.direction * (self.speed + SPEED) * delta_time
            distance_traveled = abs(self.position.x - self.start_x)

        if distance_traveled > max_distance:
            self.marked_for_removal = True

        # Update animation if applicable
        if self.use_animation:
            self.update_animation(delta_time)

    def draw(self, surface, camera):
        """Desenha o projétil na tela."""
        screen_pos = camera.apply(pygame.Rect(self.position.x, self.position.y, 0, 0)).center

        if self.use_animation and self.image:
            # Draw animated sprite
            screen_rect = camera.apply(self.rect)
            surface.blit(self.image, screen_rect.topleft)
        else:
            # Fallback to original drawing method
            color = (255, 0, 0)  # Default: red
            if "Ice" in self.minor_rune_names:
                color = (0, 200, 255)  # Ice: blue
            elif "Fire" in self.minor_rune_names:
                color = (255, 100, 0)  # Fire: orange

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