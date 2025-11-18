# colliders/attack_box_collider.py
from .collider import Collider
from .hurt_box_collider import HurtBoxCollider

class AttackBoxCollider(Collider):
    def handle_collision(self, other_collider, collision_manager):
        if not self.active or not other_collider.active:
            return
        if isinstance(other_collider, HurtBoxCollider):
            other_collider.handle_collision(self, collision_manager)  # Delega para hurtbox