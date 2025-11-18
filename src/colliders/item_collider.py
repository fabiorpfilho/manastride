# colliders/item_collider.py
from .collider import Collider
from objects.dynamic_objects.player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from objects.dynamic_objects.player import Player

class ItemCollider(Collider):
    def handle_collision(self, other_collider, collision_manager):
        if not self.active:
            return
        if isinstance(other_collider.owner, Player):
            other_collider.owner.handle_pickup(self.owner)
            self.owner.marked_for_removal = True