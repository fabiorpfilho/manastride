import pygame

class CollisionManager:
    def __init__(self, dynamic_objects, static_objects, world_width):
        self.dynamic_objects = dynamic_objects
        self.static_objects = static_objects
        self.world_width = world_width
        self.door_triggered = None 


    def update(self, dynamic_objects):
        objects_to_remove = []
        self.dynamic_objects = dynamic_objects

        for dynamic_object in self.dynamic_objects:
            self._handle_collisions(dynamic_object, objects_to_remove)

        for obj in objects_to_remove:
            obj.marked_for_removal = True
            objects_to_remove.remove(obj)
            

    def _handle_collisions(self, dynamic_object, objects_to_remove):
        for dynamic_collider in dynamic_object.colliders:
            if not dynamic_collider.active:
                continue

            self._handle_collider_collisions(dynamic_object, dynamic_collider, objects_to_remove)

    def _handle_collider_collisions(self, dynamic_object, dynamic_collider, objects_to_remove):
        if dynamic_collider.type in ("body"):
            self._handle_body_collision(dynamic_object, dynamic_collider, objects_to_remove)
        elif dynamic_collider.type == "hurt_box":
            self._handle_hurt_collision(dynamic_object, dynamic_collider)
        elif dynamic_collider.type == "item":
            self._handle_item_collision(dynamic_object, dynamic_collider)

    def _handle_body_collision(self, dynamic_object, dynamic_collider, objects_to_remove):
        ground_collision_detected = False
        for static in self.static_objects:
            for static_collider in static.colliders:
                if dynamic_collider.rect.colliderect(static_collider.rect):
                    if static_collider.type == "barrier" and dynamic_object.tag == "player":
                        continue
                    if static_collider.type == "door" and dynamic_object.tag == "player":
                        self.door_triggered = (static.target_map, static.player_spawn)
                        continue
                    

                    if dynamic_object.tag == "projectile":
                        print(f"Projétil {dynamic_object.name} colidiu com {static}!")
                        objects_to_remove.append(dynamic_object)
                        return

                    intersection = dynamic_collider.rect.clip(static_collider.rect)
                    largura_invasao = intersection.width
                    altura_invasao = intersection.height

                    if largura_invasao < altura_invasao:
                        if dynamic_object.rect.centerx < static_collider.rect.centerx:
                            dynamic_object.position.x -= largura_invasao + dynamic_collider.offset[0]
                            if "npc" in dynamic_object.tag:
                                if not (static_collider.type == "barrier" and dynamic_object.tag == "enemy_npc"):
                                    dynamic_object.facing_right = False
                        else:
                            dynamic_object.position.x += largura_invasao + dynamic_collider.offset[0]
                            if "npc" in dynamic_object.tag:
                                if not (static_collider.type == "barrier" and dynamic_object.tag == "enemy_npc"):
                                    dynamic_object.facing_right = True
                        dynamic_object.speed_vector.x = 0
                    else:
                        if dynamic_object.rect.centery < static_collider.rect.centery:
                            dynamic_object.position.y -= altura_invasao + dynamic_collider.offset[1]
                            dynamic_object.speed_vector.y = 0
                            ground_collision_detected = True
                        else:
                            dynamic_object.position.y += altura_invasao + dynamic_collider.offset[1]
                            dynamic_object.speed_vector.y = 0

                    dynamic_object.sync_position()


        self._detect_is_on_ground(ground_collision_detected, dynamic_object)

    def _handle_hurt_collision(self, dynamic_object, hurt_collider):
        for other_object in self.dynamic_objects:

            if other_object is dynamic_object:
                continue
            
            if dynamic_object.tag == "enemy_npc" and other_object.tag == "enemy_npc":
                continue

            if other_object.tag == "projectile" and other_object.owner == dynamic_object:
                return
            for other_collider in other_object.colliders:

                if (
                    other_collider.type == "attack_box"
                    and hurt_collider.rect.colliderect(other_collider.rect)
                    and other_collider.active
                ):

                    # Só cause dano se o alvo ainda não foi atingido neste ataque
                    if hasattr(other_object, "already_hit_targets"):
                        if dynamic_object in other_object.already_hit_targets:
                            continue
                        other_object.already_hit_targets.add(dynamic_object)
                        if other_object.tag == "player" or other_object.tag == "projectile":
                            other_object.handle_hit()

                    dynamic_object.handle_damage(other_object.damage, other_object.facing_right)
                    if other_object.tag == "projectile":
                        other_object.marked_for_removal = True
                    return
                
    def _handle_item_collision(self, dynamic_object, item_collider):
        for other_object in self.dynamic_objects:
            if other_object is dynamic_object:
                continue
            if other_object.tag == "player" and item_collider.rect.colliderect(other_object.rect):
                print(f"Jogador colidiu com a runa {dynamic_object.name}!")
                other_object.handle_pickup(dynamic_object)
                dynamic_object.marked_for_removal = True
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
