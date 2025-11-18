# collision_manager.py
import pygame
from pygame.math import Vector2
from typing import List, Optional

from colliders.alarm_collider import AlarmCollider
from colliders.attack_box_collider import AttackBoxCollider
from colliders.body_collider import BodyCollider
from colliders.detection_collider import DetectionCollider
from colliders.hurt_box_collider import HurtBoxCollider
from colliders.item_collider import ItemCollider
# (DoorCollider e BarrierCollider provavelmente existem ou serão criados - o BodyCollider já lida com eles via __class__.__name__)


class CollisionManager:
    # --------------------------------------------------------------
    #  SINGLETON (mantido exatamente como você tinha)
    # --------------------------------------------------------------
    _instance: Optional["CollisionManager"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, dynamic_objects=None, static_objects=None, world_width=0):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        self.dynamic_objects = dynamic_objects or []
        self.static_objects = static_objects or []
        self.world_width = world_width

        self.door_triggered: Optional[Tuple[str, Tuple[float, float]]] = None
        self.alarm_triggered = False

    # --------------------------------------------------------------
    #  UPDATE - versão totalmente refatorada para usar as subclasses de Collider
    # --------------------------------------------------------------
    def update(self, dynamic_objects: List, static_objects: Optional[List] = None):
        if static_objects is not None:
            self.static_objects = static_objects
        self.dynamic_objects = dynamic_objects

        # Reset das flags que são por frame
        self.door_triggered = None
        self.alarm_triggered = False

        # Atualiza posição de TODOS os colliders (dynamic + static)
        all_objects = self.dynamic_objects + self.static_objects
        for obj in all_objects:
            if hasattr(obj, "colliders"):
                for collider in obj.colliders:
                    collider.update_position()

        # 1. Colisões físicas (BodyCollider) - dynamic vs static + dynamic vs dynamic
        for dynamic_object in self.dynamic_objects:
            for collider in dynamic_object.colliders:
                if not collider.active or not isinstance(collider, BodyCollider):
                    continue

                # Vs static
                for static in self.static_objects:
                    for s_collider in static.colliders:
                        if s_collider.active and collider.rect.colliderect(s_collider.rect):
                            collider.handle_collision(s_collider, self)

                # Vs outros dynamic bodies (player não atravessa inimigos, projéteis batem em inimigos, etc.)
                for other_object in self.dynamic_objects:
                    if other_object is dynamic_object:
                        continue
                    for o_collider in other_object.colliders:
                        if o_collider.active and isinstance(o_collider, BodyCollider) and collider.rect.colliderect(o_collider.rect):
                            collider.handle_collision(o_collider, self)  # ambos os lados serão chamados porque o loop roda para todos os dynamic

        # 2. Interações dynamic ↔ dynamic (ataque, pickup, detecção, etc.)
        # Usamos loop i/j para garantir que cada par seja processado exatamente uma vez (ambos os sentidos)
        for i in range(len(self.dynamic_objects)):
            for j in range(i + 1, len(self.dynamic_objects)):
                obj1 = self.dynamic_objects[i]
                obj2 = self.dynamic_objects[j]

                for c1 in obj1.colliders:
                    if not c1.active or isinstance(c1, BodyCollider):
                        continue
                    for c2 in obj2.colliders:
                        if not c2.active and c1.rect.colliderect(c2.rect):
                            c1.handle_collision(c2, self)
                            c2.handle_collision(c1, self)

        # 3. Tolerância para on_ground (caso o personagem esteja quase encostando no chão por causa de velocidade alta)
        for dynamic_object in self.dynamic_objects:
            if not hasattr(dynamic_object, "on_ground"):
                continue

            # Se já foi detectado por colisão física, não precisa do fallback
            if getattr(dynamic_object, "on_ground", False):
                continue

            speed_y = getattr(dynamic_object, "speed_vector", Vector2(0, 0)).y
            if speed_y <= 0:  # só aplica quando caindo ou parado
                continue

            for static in self.static_objects:
                for s_collider in static.colliders:
                    if (dynamic_object.rect.bottom >= s_collider.rect.top and
                        dynamic_object.rect.bottom <= s_collider.rect.top + 5 and
                        dynamic_object.rect.left < s_collider.rect.right and
                        dynamic_object.rect.right > s_collider.rect.left):
                        dynamic_object.on_ground = True
                        break
                if dynamic_object.on_ground:
                    break

    # --------------------------------------------------------------
    #  MÉTODO DE FÁBRICA (mantido)
    # --------------------------------------------------------------
    @classmethod
    def get_instance(cls, dynamic_objects=None, static_objects=None, world_width=0) -> "CollisionManager":
        if cls._instance is None:
            cls(dynamic_objects, static_objects, world_width)
        else:
            if dynamic_objects is not None:
                cls._instance.dynamic_objects = dynamic_objects
            if static_objects is not None:
                cls._instance.static_objects = static_objects
            if world_width:
                cls._instance.world_width = world_width
        return cls._instance