import pygame

class CollisionManager:
    def __init__(self, dynamic_objects, static_objects, world_width):
        self.dynamic_objects = dynamic_objects
        self.static_objects = static_objects
        self.world_width = world_width

    def update(self, dynamic_objects):
        objects_to_remove = []
        self.dynamic_objects = dynamic_objects

        for dynamic_object in self.dynamic_objects:
            self._handle_collisions(dynamic_object, objects_to_remove)

        for obj in objects_to_remove:
            if obj in self.dynamic_objects:
                self.dynamic_objects.remove(obj)
            obj.marked_for_removal = True

    def _handle_collisions(self, dynamic_object, objects_to_remove):
        # Atualiza posição do rect principal e dos colliders
        dynamic_object.rect.topleft = dynamic_object.position
        for dynamic_collider in dynamic_object.colliders:
            dynamic_collider.rect.topleft = (
                dynamic_object.rect.x + dynamic_collider.offset.x,
                dynamic_object.rect.y + dynamic_collider.offset.y
            )

        for dynamic_collider in dynamic_object.colliders:
            self._handle_collider_collisions(dynamic_object, dynamic_collider, objects_to_remove)

    def _handle_collider_collisions(self, dynamic_object, dynamic_collider, objects_to_remove):
        if dynamic_collider.type in ("body"):
            self._handle_body_collision(dynamic_object, dynamic_collider, objects_to_remove)
        elif dynamic_collider.type == "hurt_box":
            self._handle_hurt_collision(dynamic_object, dynamic_collider)

    def _handle_body_collision(self, dynamic_object, dynamic_collider, objects_to_remove):
        ground_collision_detected = False
        for static in self.static_objects:
            for static_collider in static.colliders:
                if dynamic_collider.rect.colliderect(static_collider.rect):

                    if dynamic_object.tag == "projectile":
                        objects_to_remove.append(dynamic_object)
                        return

                    intersection = dynamic_collider.rect.clip(static_collider.rect)
                    largura_invasao = intersection.width
                    altura_invasao = intersection.height

                    if largura_invasao < altura_invasao:
                        if dynamic_object.rect.centerx < static_collider.rect.centerx:
                            dynamic_object.position.x -= largura_invasao + dynamic_collider.offset.x
                            if "npc" in dynamic_object.tag:
                                dynamic_object.facing_right = False
                        else:
                            dynamic_object.position.x += largura_invasao + dynamic_collider.offset.x
                            if "npc" in dynamic_object.tag:
                                dynamic_object.facing_right = True
                        dynamic_object.speed_vector.x = 0
                    else:
                        if dynamic_object.rect.centery < static_collider.rect.centery:
                            dynamic_object.position.y -= altura_invasao + dynamic_collider.offset.y
                            dynamic_object.speed_vector.y = 0
                            ground_collision_detected = True
                        else:
                            dynamic_object.position.y += altura_invasao + dynamic_collider.offset.y
                            dynamic_object.speed_vector.y = 0

                    dynamic_object.rect.topleft = dynamic_object.position
                    for dc in dynamic_object.colliders:
                        dc.rect.topleft = (
                            dynamic_object.rect.x + dc.offset.x,
                            dynamic_object.rect.y + dc.offset.y
                        )

        self._detect_is_on_ground(ground_collision_detected, dynamic_object)

    def _handle_hurt_collision(self, dynamic_object, hurt_collider):
        for other_object in self.dynamic_objects:
            if other_object is dynamic_object:
                continue

            for other_collider in other_object.colliders:
                if other_collider.type == "attack_box" and hurt_collider.rect.colliderect(other_collider.rect):
                    dynamic_object.handle_damage(other_object.damage)
                    return

    def _detect_is_on_ground(self, ground_collision_detected, dynamic_object):
        if ground_collision_detected:
            dynamic_object.on_ground = True
        elif hasattr(dynamic_object, "speed_vector") and dynamic_object.speed_vector.y > 0:
            on_platform = False
            for static in self.static_objects:
                for static_collider in static.colliders:
                    if (dynamic_object.rect.bottom >= static_collider.rect.top and
                        dynamic_object.rect.bottom <= static_collider.rect.top + 5 and
                        dynamic_object.rect.left < static_collider.rect.right and
                        dynamic_object.rect.right > static_collider.rect.left):
                        on_platform = True
                        break
                if on_platform:
                    break
            dynamic_object.on_ground = on_platform
