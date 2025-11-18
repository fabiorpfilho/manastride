# colliders/alarm_collider.py
from .collider import Collider
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from objects.dynamic_objects.player import Player

class AlarmCollider(Collider):
    def handle_collision(self, other_collider, collision_manager):
        if isinstance(other_collider.owner, Player):
            collision_manager.alarm_triggered = True
            if other_collider.owner.dash_timer > 0:
                other_collider.owner.dash_timer = 0
                other_collider.owner.speed_vector.x = 0