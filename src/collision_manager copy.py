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
        if hasattr(dynamic_object, "facing_right") and hasattr(dynamic_object, "spriteOffset"):
            dynamic_object.rect.centerx = dynamic_object.position.x + dynamic_object.spriteOffset[0]
            dynamic_object.rect.centery = dynamic_object.position.y + dynamic_object.spriteOffset[1]
        else:
            dynamic_object.rect.centerx = dynamic_object.position.x
            dynamic_object.rect.centery = dynamic_object.position.y + dynamic_object.spriteOffset[1] + 10000
        for dynamic_collider in dynamic_object.colliders:
            dynamic_collider.rect.topleft = (
                dynamic_object.rect.x + dynamic_collider.offset.x,
                dynamic_object.rect.y + dynamic_collider.offset.y
            )

        # Inicialmente, assumimos que o jogador não está no chão até que uma colisão confirme
        ground_collision_detected = False

        for dynamic_collider in dynamic_object.colliders:
            for static in self.static_objects:
                for static_collider in static.colliders:
                    if dynamic_collider.rect.colliderect(static_collider.rect):

                        if dynamic_collider.type == "projectile":
                            objects_to_remove.append(dynamic_object)
                            return

                        # Calcula a interseção real
                        intersection = dynamic_collider.rect.clip(static_collider.rect)
                        largura_invasao = intersection.width
                        altura_invasao = intersection.height

                        # Decide se empurra em X ou Y (o maior)
                        if altura_invasao > largura_invasao:
                            # Corrige em X
                            if dynamic_object.rect.centerx < static_collider.rect.centerx:
                                dynamic_object.position.x -= largura_invasao + dynamic_collider.offset.x
                            else:
                                dynamic_object.position.x += largura_invasao + dynamic_collider.offset.x
                            dynamic_object.speed_vector.x = 0
                        else:
                            # Corrige em Y
                            if dynamic_object.rect.centery < static_collider.rect.centery:
                                # Vindo de cima (pousando na plataforma)
                                dynamic_object.position.y -= altura_invasao + dynamic_collider.offset.y
                                dynamic_object.speed_vector.y = 0
                                ground_collision_detected = True
                            else:
                                # Vindo de baixo (batendo a cabeça)
                                dynamic_object.position.y += altura_invasao + dynamic_collider.offset.y
                                dynamic_object.speed_vector.y = 0

                        # Atualiza posições após ajuste
                        if hasattr(dynamic_object, "facing_right") and hasattr(dynamic_object, "spriteOffset"):
                            dynamic_object.rect.centerx = dynamic_object.position.x + dynamic_object.spriteOffset[0]
                            dynamic_object.rect.centery = dynamic_object.position.y + dynamic_object.spriteOffset[1]
                        else:
                            dynamic_object.rect.centerx = dynamic_object.position.x
                            dynamic_object.rect.centery = dynamic_object.position.y + dynamic_object.spriteOffset[1] + 10000
                        for dc in dynamic_object.colliders:
                            dc.rect.topleft = (
                                dynamic_object.rect.x + dc.offset.x,
                                dynamic_object.rect.y + dc.offset.y
                            )

        # Atualiza on_ground apenas se soubermos a situação do jogador
        if ground_collision_detected:
            dynamic_object.on_ground = True
        elif hasattr(dynamic_object, "speed_vector") and dynamic_object.speed_vector.y > 0:  # Jogador está se movendo para baixo
            # Verifica se o jogador está fora de uma plataforma
            on_platform = False
            for static in self.static_objects:
                for static_collider in static.colliders:
                    # Verifica se o pé do jogador está alinhado com o topo da plataforma
                    if (dynamic_object.rect.bottom >= static_collider.rect.top and
                        dynamic_object.rect.bottom <= static_collider.rect.top + 5 and  # Pequena margem
                        dynamic_object.rect.left < static_collider.rect.right and
                        dynamic_object.rect.right > static_collider.rect.left):
                        on_platform = True
                        break
                if on_platform:
                    break
            dynamic_object.on_ground = on_platform
