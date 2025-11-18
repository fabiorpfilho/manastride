# colliders/detection_collider.py
from typing import TYPE_CHECKING

from .collider import Collider

# Só importa durante type checking (não causa import circular em runtime!)
if TYPE_CHECKING:
    from objects.dynamic_objects.player import Player
    from objects.dynamic_objects.hammer_bot import HammerBot
    from objects.dynamic_objects.drone import Drone

class DetectionCollider(Collider):
    def handle_collision(self, other_collider: Collider, collision_manager) -> None:
        owner = self.owner
        other_owner = other_collider.owner

        # Verifica se ESTE objeto é um inimigo (HammerBot, Drone, ou qualquer novo)
        if not any(isinstance(owner, enemy_type) 
                   for enemy_type in (HammerBot, Drone)):
            return

        # Verifica se o outro é exatamente o Player
        if not isinstance(other_owner, Player):
            return

        # Colisão detectada → jogador visto!
        if self.rect.colliderect(other_collider.rect):
            owner.player_target = other_owner
            owner.player_detected = True
            # print(f"{type(owner).__name__} detectou o Player!")