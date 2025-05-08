#Classe que será responsável por gerenciar as colisões entre objetos
# collision_manager.py
import pygame

class CollisionManager:
    def __init__(self, dynamic_objects , static_objects, world_width):
        self.dynamic_objects  = dynamic_objects 
        self.static_objects = static_objects
        self.world_width = world_width

    def update(self, dynamic_objects):
        
        objects_to_remove = []
        
        for dynamic_object in dynamic_objects:
            self._handle_horizontal_collisions(dynamic_object, objects_to_remove)
            self._handle_vertical_collisions(dynamic_object, objects_to_remove)
            
        for obj in objects_to_remove:
            if obj in dynamic_objects:
                dynamic_objects.remove(obj)
            obj.marked_for_removal = True

    def _handle_horizontal_collisions(self, dynamic_object, objects_to_remove):
        
        if dynamic_object.position.x + dynamic_object.rect.width < 0 or dynamic_object.position.x > self.world_width:
        # Se for um projétil, remove
            if any(collider.type == "projectile" for collider in dynamic_object.colliders):
                objects_to_remove.append(dynamic_object)
                return  # Não precisa continuar processando esse objeto

        # Limita o objeto dentro da tela
        if dynamic_object.position.x < 0:
            dynamic_object.position.x = 0
            if hasattr(dynamic_object, "speed_vector"):
                dynamic_object.speed_vector.x = 0
        elif dynamic_object.position.x + dynamic_object.rect.width > self.world_width:
            dynamic_object.position.x = self.world_width - dynamic_object.rect.width
            if hasattr(dynamic_object, "speed_vector"):
                dynamic_object.speed_vector.x = 0
                

        # Atualiza a posição do objeto e dos colliders uma vez
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
                            return  # Nem precisa continuar checando, já vai remover
                        
                        collider_offset_x = dynamic_collider.offset.x

                        if dynamic_object.speed_vector.x > 0:
                            # Colisão à direita: alinha a borda direita do collider com a esquerda do static
                            dynamic_object.position.x = static_collider.rect.left - collider_offset_x - dynamic_collider.rect.width
                        elif dynamic_object.speed_vector.x < 0:
                            # Colisão à esquerda: alinha a borda esquerda do collider com a direita do static
                            dynamic_object.position.x = static_collider.rect.right - collider_offset_x

                        dynamic_object.speed_vector.x = 0
                        dynamic_object.rect.topleft = dynamic_object.position

                        # Atualiza os colliders após ajustar a posição
                        for dc in dynamic_object.colliders:
                            dc.rect.topleft = (
                                dynamic_object.rect.x + dc.offset.x,
                                dynamic_object.rect.y + dc.offset.y
                            )
                    
    def _handle_vertical_collisions(self, dynamic_object, objects_to_remove):
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
                        
                        collider_offset_y = dynamic_collider.offset.y  

                        if dynamic_object.speed_vector.y > 0:
                            # Colisão abaixo: alinha a base do collider com o topo do static
                            dynamic_object.position.y = static_collider.rect.top - collider_offset_y - dynamic_collider.rect.height
                            dynamic_object.on_ground = True
                        elif dynamic_object.speed_vector.y < 0:
                            # Colisão acima: alinha o topo do collider com a base do static
                            dynamic_object.position.y = static_collider.rect.bottom - collider_offset_y

                        dynamic_object.speed_vector.y = 0
                        dynamic_object.rect.topleft = dynamic_object.position

                        for dc in dynamic_object.colliders:
                            dc.rect.topleft = (
                                dynamic_object.rect.x + dc.offset.x,
                                dynamic_object.rect.y + dc.offset.y
                            )
                            
                            
# Você empurra do lado que mais invadiu, se um objeto estra entrando 10 no y e 5 no x, você empurra ele 10 de volta no y