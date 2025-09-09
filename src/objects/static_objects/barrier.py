from objects.entity_with_animation import EntityWithAnimation
import pygame
from typing import List

class Barrier(EntityWithAnimation):
    def __init__(self, position, size, duration: float, owner, facing_right: bool):
        super().__init__(position, size, sprite=(255, 0, 0))
        self.name = "Barrier"
        self.tag = "barrier"
        self.time_remaining = duration  # Duração em segundos
        self.owner = owner  # Entidade que criou a barreira
        self.facing_right = facing_right  # Orientação da barreira
        self.marked_for_removal = False  # Indicador de remoção
        self.add_collider((0, 0), (self.size.x, self.size.y), type='barrier', active=True)

        # Animation setup
        self.current_animation = None
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.2  # Seconds per frame
        self.use_animation = True

        # Load barrier animation frames
        self.animation_frames = [
            pygame.image.load("assets/spells/barrier1.png").convert_alpha(),
            pygame.image.load("assets/spells/barrier2.png").convert_alpha(),
            pygame.image.load("assets/spells/barrier3.png").convert_alpha()
        ]

        # Set initial image
        self.update_image()  # Chama update_image para configurar a imagem inicial com flip

    def update_animation(self, delta_time: float):
        """Update the animation frame."""
        if not self.use_animation or not self.animation_frames:
            return

        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_speed:
            self.animation_timer -= self.animation_speed
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.update_image()

    def update_image(self):
        """Update the barrier's image based on the current animation frame."""
        self.image = self.animation_frames[self.current_frame]
        # Flip the image based on facing_right
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(bottomleft=(self.position.x, self.position.y))

    def update(self, delta_time: float, *args, **kwargs):
        """Update the barrier's animation and duration."""
        if self.use_animation:
            self.update_animation(delta_time)

        # Diminui o tempo restante e marca para remoção se expirar
        self.time_remaining -= delta_time
        if self.time_remaining <= 0:
            self.marked_for_removal = True

    def draw(self, surface, camera):
        """Draw the barrier on the screen."""
        if self.use_animation and self.image:
            screen_rect = camera.apply(self.rect)
            surface.blit(self.image, screen_rect.topleft)
        else:
            # Fallback to a transparent rect if animation fails
            pygame.draw.rect(surface, (0, 0, 0, 0), camera.apply(self.rect))