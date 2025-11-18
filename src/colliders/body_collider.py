# colliders/body_collider.py
from .collider import Collider

class BodyCollider(Collider):
    def handle_collision(self, other_collider, collision_manager):
        # Só colide com colliders estáticos ou outros bodies
        if not self.active or not other_collider.active:
            return

        if other_collider.__class__.__name__ in ["DoorCollider", "BarrierCollider"]:
            if other_collider.owner.target_map and self.owner.tag == "player":
                collision_manager.door_triggered = (other_collider.owner.target_map, other_collider.owner.player_spawn)
            return  # Não empurra, apenas bloqueia passagem

        if other_collider.__class__.__name__ == "AlarmCollider" and self.owner.tag == "player":
            collision_manager.alarm_triggered = True
            if self.owner.dash_timer > 0:
                self.owner.dash_timer = 0
                self.owner.speed_vector.x = 0
            return

        # Colisão física padrão (empurra o owner)
        intersection = self.rect.clip(other_collider.rect)
        if intersection.width < intersection.height:
            if self.owner.rect.centerx < other_collider.rect.centerx:
                self.owner.position.x -= intersection.width
            else:
                self.owner.position.x += intersection.width
            self.owner.speed_vector.x = 0
        else:
            if self.owner.rect.centery < other_collider.rect.centery:
                self.owner.position.y -= intersection.height
                self.owner.speed_vector.y = 0
                self.owner.on_ground = True
            else:
                self.owner.position.y += intersection.height
                self.owner.speed_vector.y = 0
        self.owner.sync_position()