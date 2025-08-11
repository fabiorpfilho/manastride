from spell_system.rune_type import RuneType
from typing import Dict, Optional, Callable
from objects.entity_with_sprite import EntityWithSprite
import math

class Rune(EntityWithSprite):
    def __init__(self, position, size, name: str, image, rune_type, cost: int, effect: Optional[Callable] = None):
        super().__init__(position, size, image)
        self.add_collider((0, 0), (self.size.x, self.size.y), type='item', active=True)
        self.name = name
        self.tag = "rune"
        self.rune_type = RuneType.MAJOR if rune_type == "major" else RuneType.MINOR
        self.cost = cost
        self.effect = effect
        # Levitation variables
        self.base_y = position[1]  # Store initial y-position
        self.levitation_amplitude = 5  # Distance to move up/down (pixels)
        self.levitation_speed = 2  # Speed of oscillation (radians per second)
        self.levitation_timer = 0  # Timer for sine wave
        self.marked_for_removal = False

    def update(self, delta_time: float):
        # Update levitation timer
        self.levitation_timer += delta_time * self.levitation_speed
        # Calculate new y-position using sine wave
        offset_y = math.sin(self.levitation_timer) * self.levitation_amplitude
        self.position.y = self.base_y + offset_y
        # Update rect to reflect new position
        # Update collider position
        self.sync_position()