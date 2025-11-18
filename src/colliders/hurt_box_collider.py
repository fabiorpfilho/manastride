# colliders/hurt_box_collider.py
from .collider import Collider
from .attack_box_collider import AttackBoxCollider
class HurtBoxCollider(Collider):
    def handle_collision(self, other_collider, collision_manager):
        if not self.active or not other_collider.active:
            return
        if isinstance(other_collider, AttackBoxCollider):
            owner = other_collider.owner
            if hasattr(owner, "already_hit_targets") and self.owner in owner.already_hit_targets:
                return
            if hasattr(owner, "already_hit_targets"):
                owner.already_hit_targets.add(self.owner)
            self.owner.handle_damage(owner.damage, owner.facing_right)
            if owner.tag == "projectile":
                owner.marked_for_removal = True