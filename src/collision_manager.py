#Classe que será responsável por gerenciar as colisões entre objetos
# collision_manager.py
import pygame

class CollisionManager:
    def __init__(self, dynamic_object, static_objects, screen_width):
        self.dynamic_object = dynamic_object
        self.static_objects = static_objects
        self.screen_width = screen_width

    def update(self):
        self._handle_horizontal_collisions()
        self._handle_vertical_collisions()

    def _handle_horizontal_collisions(self):
        # Limita o objeto dentro da tela
        if self.dynamic_object.position.x < 0:
            self.dynamic_object.position.x = 0
            self.dynamic_object.movement.x = 0
        elif self.dynamic_object.position.x + self.dynamic_object.rect.width > self.screen_width:
            self.dynamic_object.position.x = self.screen_width - self.dynamic_object.rect.width
            self.dynamic_object.movement.x = 0

        # Atualiza a posição do objeto e dos colliders uma vez
        self.dynamic_object.rect.topleft = self.dynamic_object.position
        for dynamic_collider in self.dynamic_object.colliders:
            dynamic_collider.rect.topleft = (
                self.dynamic_object.rect.x + dynamic_collider.offset.x,
                self.dynamic_object.rect.y + dynamic_collider.offset.y
            )

        # Verifica colisões
        for dynamic_collider in self.dynamic_object.colliders:
            for static in self.static_objects:
                for static_collider in static.colliders:
                    if dynamic_collider.rect.colliderect(static_collider.rect):
                        collider_offset_x = dynamic_collider.offset.x

                        if self.dynamic_object.movement.x > 0:
                            # Colisão à direita: alinha a borda direita do collider com a esquerda do static
                            self.dynamic_object.position.x = static_collider.rect.left - collider_offset_x - dynamic_collider.rect.width
                        elif self.dynamic_object.movement.x < 0:
                            # Colisão à esquerda: alinha a borda esquerda do collider com a direita do static
                            self.dynamic_object.position.x = static_collider.rect.right - collider_offset_x

                        self.dynamic_object.movement.x = 0
                        self.dynamic_object.rect.topleft = self.dynamic_object.position

                        # Atualiza os colliders após ajustar a posição
                        for dc in self.dynamic_object.colliders:
                            dc.rect.topleft = (
                                self.dynamic_object.rect.x + dc.offset.x,
                                self.dynamic_object.rect.y + dc.offset.y
                            )
                    
    def _handle_vertical_collisions(self):
        self.dynamic_object.rect.topleft = self.dynamic_object.position
        for dynamic_collider in self.dynamic_object.colliders:
            dynamic_collider.rect.topleft = (
                self.dynamic_object.rect.x + dynamic_collider.offset.x,
                self.dynamic_object.rect.y + dynamic_collider.offset.y
            )

        for dynamic_collider in self.dynamic_object.colliders:
            for static in self.static_objects:
                for static_collider in static.colliders:
                    if dynamic_collider.rect.colliderect(static_collider.rect):
                        collider_offset_y = dynamic_collider.offset.y  

                        if self.dynamic_object.movement.y > 0:
                            # Colisão abaixo: alinha a base do collider com o topo do static
                            self.dynamic_object.position.y = static_collider.rect.top - collider_offset_y - dynamic_collider.rect.height
                            self.dynamic_object.on_ground = True
                        elif self.dynamic_object.movement.y < 0:
                            # Colisão acima: alinha o topo do collider com a base do static
                            self.dynamic_object.position.y = static_collider.rect.bottom - collider_offset_y

                        self.dynamic_object.movement.y = 0
                        self.dynamic_object.rect.topleft = self.dynamic_object.position

                        for dc in self.dynamic_object.colliders:
                            dc.rect.topleft = (
                                self.dynamic_object.rect.x + dc.offset.x,
                                self.dynamic_object.rect.y + dc.offset.y
                            )