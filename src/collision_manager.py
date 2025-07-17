# collision_manager.py
import pygame

class CollisionManager:
    def __init__(self, dynamic_objects, static_objects, world_width):
        self.dynamic_objects = dynamic_objects
        self.static_objects = static_objects
        self.world_width = world_width

    def update(self, dynamic_objects):
        objects_to_remove = []

        for dynamic_object in dynamic_objects:
            self._handle_collisions(dynamic_object, objects_to_remove)

        for obj in objects_to_remove:
            if obj in dynamic_objects:
                dynamic_objects.remove(obj)
            obj.marked_for_removal = True

    def _handle_collisions(self, dynamic_object, objects_to_remove):
        # Verifica limites da tela
        if dynamic_object.position.x + dynamic_object.rect.width < 0 or dynamic_object.position.x > self.world_width:
            if any(collider.type == "projectile" for collider in dynamic_object.colliders):
                objects_to_remove.append(dynamic_object)
                return

        if dynamic_object.position.x < 0:
            dynamic_object.position.x = 0
            if hasattr(dynamic_object, "speed_vector"):
                dynamic_object.speed_vector.x = 0
        elif dynamic_object.position.x + dynamic_object.rect.width > self.world_width:
            dynamic_object.position.x = self.world_width - dynamic_object.rect.width
            if hasattr(dynamic_object, "speed_vector"):
                dynamic_object.speed_vector.x = 0

        # Atualiza posição do rect principal
        dynamic_object.rect.topleft = dynamic_object.position
        for dynamic_collider in dynamic_object.colliders:
            dynamic_collider.rect.topleft = (
                dynamic_object.rect.x + dynamic_collider.offset.x,
                dynamic_object.rect.y + dynamic_collider.offset.y
            )

        for dynamic_collider in dynamic_object.colliders:
            for static in self.static_objects:
                for static_collider in static.colliders:
                    if dynamic_collider.rect.colliderect(static_collider.rect):

                        if dynamic_collider.type == "projectile":
                            objects_to_remove.append(dynamic_object)
                            return

                        # Calcula a interseção real
                        intersection = dynamic_collider.rect.clip(static_collider.rect)
                        overlap_x = intersection.width
                        overlap_y = intersection.height

                        # Decide se empurra em X ou Y (o maior)
                        if overlap_y > overlap_x:
                            # Corrige em X
                            if dynamic_object.rect.centerx < static_collider.rect.centerx:
                                # Vindo da esquerda
                                dynamic_object.position.x -= overlap_x + dynamic_collider.offset.x
                            else:
                                # Vindo da direita
                                dynamic_object.position.x += overlap_x + dynamic_collider.offset.x
                            dynamic_object.speed_vector.x = 0
                        else:
                            # Corrige em Y
                            if dynamic_object.rect.centery < static_collider.rect.centery:
                                # Vindo de cima
                                dynamic_object.position.y -= overlap_y + dynamic_collider.offset.y
                                dynamic_object.on_ground = True
                            else:
                                # Vindo de baixo
                                dynamic_object.position.y += overlap_y + dynamic_collider.offset.y
                            dynamic_object.speed_vector.y = 0

                        # Atualiza posições após ajuste
                        dynamic_object.rect.topleft = dynamic_object.position
                        for dc in dynamic_object.colliders:
                            dc.rect.topleft = (
                                dynamic_object.rect.x + dc.offset.x,
                                dynamic_object.rect.y + dc.offset.y
                            )

# Você empurra do lado que mais invadiu, se um objeto estra entrando 10 no y e 5 no x, você empurra ele 10 de volta no y