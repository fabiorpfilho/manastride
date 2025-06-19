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
        # Verifica se o objeto está fora dos limites do mundo
        if dynamic_object.position.x + dynamic_object.rect.width < 0 or dynamic_object.position.x > self.world_width:
            if any(collider.type == "projectile" for collider in dynamic_object.colliders):
                objects_to_remove.append(dynamic_object)
                return

        # Limita o objeto dentro da tela
        if dynamic_object.position.x < 0:
            dynamic_object.position.x = 0
            if hasattr(dynamic_object, "speed_vector"):
                dynamic_object.speed_vector.x = 0
        elif dynamic_object.position.x + dynamic_object.rect.width > self.world_width:
            dynamic_object.position.x = self.world_width - dynamic_object.rect.width
            if hasattr(dynamic_object, "speed_vector"):
                dynamic_object.speed_vector.x = 0

        # Atualiza a posição do objeto e dos colliders
        dynamic_object.rect.topleft = dynamic_object.position
        for dynamic_collider in dynamic_object.colliders:
            dynamic_collider.rect.topleft = (
                dynamic_object.rect.x + dynamic_collider.offset.x,
                dynamic_object.rect.y + dynamic_collider.offset.y
            )

        # Verifica colisões
        for dynamic_collider in dynamic_object.colliders:
            for static in self.static_objects:
                for static_collider in static.colliders:
                    if dynamic_collider.rect.colliderect(static_collider.rect):
                        if dynamic_collider.type == "projectile":
                            objects_to_remove.append(dynamic_object)
                            return

                        # Calcula a sobreposição nos eixos X e Y
                        overlap_left = dynamic_collider.rect.right - static_collider.rect.left
                        overlap_right = static_collider.rect.right - dynamic_collider.rect.left
                        overlap_top = dynamic_collider.rect.bottom - static_collider.rect.top
                        overlap_bottom = static_collider.rect.bottom - dynamic_collider.rect.top

                        # Garante que as sobreposições sejam positivas
                        overlaps = {
                            "left": overlap_left if overlap_left > 0 else float('inf'),
                            "right": overlap_right if overlap_right > 0 else float('inf'),
                            "top": overlap_top if overlap_top > 0 else float('inf'),
                            "bottom": overlap_bottom if overlap_bottom > 0 else float('inf')
                        }
                        print(f"dynamic_object.speed_vector.x: {dynamic_object.speed_vector.x}")
                        # Determina o lado da colisão com base na direção do movimento
                        if dynamic_object.facing_right == True and overlaps["right"] < float('inf'):
                            self._resolve_right_collision(dynamic_object, dynamic_collider, static_collider)
                        elif dynamic_object.facing_right == False and overlaps["left"] < float('inf'):
                            self._resolve_left_collision(dynamic_object, dynamic_collider, static_collider)
                        elif dynamic_object.speed_vector.y > 0 and overlaps["bottom"] < float('inf'):
                            self._resolve_bottom_collision(dynamic_object, dynamic_collider, static_collider)
                        elif dynamic_object.speed_vector.y < 0 and overlaps["top"] < float('inf'):
                            self._resolve_top_collision(dynamic_object, dynamic_collider, static_collider)

                        # Atualiza a posição do objeto e dos colliders após a resolução
                        dynamic_object.rect.topleft = dynamic_object.position
                        for dc in dynamic_object.colliders:
                            dc.rect.topleft = (
                                dynamic_object.rect.x + dc.offset.x,
                                dynamic_object.rect.y + dc.offset.y
                            )

    def _resolve_right_collision(self, dynamic_object, dynamic_collider, static_collider):
        print("Colisão à direita")
        collider_offset_x = dynamic_collider.offset.x
        dynamic_object.position.x = static_collider.rect.left - collider_offset_x - dynamic_collider.rect.width
        dynamic_object.speed_vector.x = 0

    def _resolve_left_collision(self, dynamic_object, dynamic_collider, static_collider):
        print("Colisão à esquerda")
        collider_offset_x = dynamic_collider.offset.x
        dynamic_object.position.x = static_collider.rect.right - collider_offset_x
        dynamic_object.speed_vector.x = 0

    def _resolve_bottom_collision(self, dynamic_object, dynamic_collider, static_collider):
        # print("Colisão abaixo")
        collider_offset_y = dynamic_collider.offset.y
        dynamic_object.position.y = static_collider.rect.top - collider_offset_y - dynamic_collider.rect.height
        dynamic_object.speed_vector.y = 0
        dynamic_object.on_ground = True

    def _resolve_top_collision(self, dynamic_object, dynamic_collider, static_collider):
        print("Colisão acima")
        collider_offset_y = dynamic_collider.offset.y
        dynamic_object.position.y = static_collider.rect.bottom - collider_offset_y
        dynamic_object.speed_vector.y = 0