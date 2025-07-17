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
        # Verifica se o objeto saiu dos limites da tela
        if dynamic_object.position.x + dynamic_object.rect.width < 0 or dynamic_object.position.x > self.world_width:
            if any(collider.type == "projectile" for collider in dynamic_object.colliders):
                objects_to_remove.append(dynamic_object)
                return
            # Limita dentro da tela
            dynamic_object.position.x = max(0, min(dynamic_object.position.x, self.world_width - dynamic_object.rect.width))
            dynamic_object.speed_vector.x = 0

        # Calcula a posição futura com base na velocidade
        future_position = pygame.Vector2(dynamic_object.position.x + dynamic_object.speed_vector.x,
                                         dynamic_object.position.y + dynamic_object.speed_vector.y)

        # Atualiza o rect para a posição atual (antes da resolução)
        dynamic_object.rect.topleft = dynamic_object.position
        for dynamic_collider in dynamic_object.colliders:
            dynamic_collider.rect.topleft = (
                dynamic_object.rect.x + dynamic_collider.offset.x,
                dynamic_object.rect.y + dynamic_collider.offset.y
            )

        # Lista para armazenar todas as colisões e suas profundidades
        collisions = []

        # Verifica colisões com todos os objetos estáticos
        for dynamic_collider in dynamic_object.colliders:
            for static in self.static_objects:
                for static_collider in static.colliders:
                    if dynamic_collider.rect.colliderect(static_collider.rect):
                        # Calcula a profundidade de penetração nos eixos X e Y
                        overlap_x, overlap_y = self._calculate_overlap(dynamic_collider.rect, static_collider.rect,
                                                                      dynamic_object.speed_vector)
                        collisions.append({
                            'static_collider': static_collider,
                            'dynamic_collider': dynamic_collider,
                            'overlap_x': overlap_x,
                            'overlap_y': overlap_y
                        })

        # Se houver colisões, resolve com base na menor profundidade
        if collisions:
            for collision in collisions:
                dynamic_collider = collision['dynamic_collider']
                static_collider = collision['static_collider']
                overlap_x = collision['overlap_x']
                overlap_y = collision['overlap_y']

                if dynamic_collider.type == "projectile":
                    objects_to_remove.append(dynamic_object)
                    return

                # Escolhe o eixo com menor profundidade de penetração
                if abs(overlap_x) < abs(overlap_y) and overlap_x != 0:
                    # Resolver colisão horizontal
                    collider_offset_x = dynamic_collider.offset.x
                    if dynamic_object.speed_vector.x > 0:
                        dynamic_object.position.x = static_collider.rect.left - collider_offset_x - dynamic_collider.rect.width
                    elif dynamic_object.speed_vector.x < 0:
                        dynamic_object.position.x = static_collider.rect.right - collider_offset_x
                    dynamic_object.speed_vector.x = 0
                elif overlap_y != 0:
                    # Resolver colisão vertical
                    collider_offset_y = dynamic_collider.offset.y
                    if dynamic_object.speed_vector.y > 0:
                        dynamic_object.position.y = static_collider.rect.top - collider_offset_y - dynamic_collider.rect.height
                        dynamic_object.on_ground = True
                    elif dynamic_object.speed_vector.y < 0:
                        dynamic_object.position.y = static_collider.rect.bottom - collider_offset_y
                    dynamic_object.speed_vector.y = 0

        # Atualiza a posição final do rect e dos colliders
        dynamic_object.rect.topleft = dynamic_object.position
        for dynamic_collider in dynamic_object.colliders:
            dynamic_collider.rect.topleft = (
                dynamic_object.rect.x + dynamic_collider.offset.x,
                dynamic_object.rect.y + dynamic_collider.offset.y
            )

    def _calculate_overlap(self, dynamic_rect, static_rect, speed_vector):
        """Calcula a profundidade de penetração nos eixos X e Y."""
        overlap_x = 0
        overlap_y = 0

        if speed_vector.x > 0:
            overlap_x = static_rect.left - dynamic_rect.right
        elif speed_vector.x < 0:
            overlap_x = static_rect.right - dynamic_rect.left

        if speed_vector.y > 0:
            overlap_y = static_rect.top - dynamic_rect.bottom
        elif speed_vector.y < 0:
            overlap_y = static_rect.bottom - dynamic_rect.top

        return overlap_x, overlap_y