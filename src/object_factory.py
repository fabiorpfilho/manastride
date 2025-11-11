# object_factory.py
import pygame
from pygame.math import Vector2
from objects.static_objects.terrain import Terrain
from objects.static_objects.door import Door
from objects.static_objects.alarm import Alarm
from objects.dynamic_objects.rune import Rune
from objects.dynamic_objects.player import Player
from objects.dynamic_objects.hammer_bot import HammerBot
from objects.dynamic_objects.drone import Drone
from xml.etree.ElementTree import Element
from typing import Union, Optional, Dict, Any
from asset_loader import AssetLoader

class ObjectFactory:
    # Mapeamento estático – não depende de instância
    _object_map = {
        ("spawn", "player"): "_create_player",
        ("spawn", "hammer_bot"): "_create_hammer_bot",
        ("spawn", "drone_bot"): "_create_drone_bot",
        ("rune", None): "_create_rune",
        ("door", None): "_create_door",
        ("alarm", None): "_create_alarm",
    }

    # ------------------------------------------------------------------ #
    #  MÉTODOS ESTÁTICOS
    # ------------------------------------------------------------------ #
    @staticmethod
    def create_object(
        obj: Union[Element, Dict[str, Any]],
        player_spawn: Optional[tuple] = None,
    ) -> Optional[Any]:
        """Cria um objeto a partir de XML ou dict."""
        name = obj.get("name") if isinstance(obj, dict) else obj.get("name")
        type_ = obj.get("type") if isinstance(obj, dict) else obj.get("type")

        # Ignora criação de player quando já temos spawn definido
        if type_ == "spawn" and name == "player" and player_spawn is not None:
            return None

        creator_name = ObjectFactory._object_map.get((type_, name)) or ObjectFactory._object_map.get((type_, None))
        if creator_name:
            creator = getattr(ObjectFactory, creator_name)
            return creator(obj)
        print(f"[ObjectFactory] Tipo não suportado: {type_}/{name}")
        return None

    @staticmethod
    def _create_player(
        obj: Union[Element, Dict[str, Any]],
    ) -> Player:
        """Cria ou devolve o player já existente."""
        pos = (float(obj.get("x", 0)), float(obj.get("y", 0)))
        size = (float(obj.get("width", 0)), float(obj.get("height", 0)))

        # Props customizadas (player_spawn_x/y)
        props = {}
        if isinstance(obj, Element):
            properties = obj.find("properties")
            if properties:
                for p in properties.findall("property"):
                    props[p.get("name")] = p.get("value")

        spawn_pos = Vector2(pos)
        if "player_spawn_x" in props and "player_spawn_y" in props:
            spawn_pos = Vector2(float(props["player_spawn_x"]), float(props["player_spawn_y"]))

        player = Player(spawn_pos, size)
        print(f"[ObjectFactory] Player criado em {spawn_pos}")
        return player


    @staticmethod
    def _create_hammer_bot(obj: Union[Element, Dict[str, Any]], *_) -> HammerBot:
        pos = (float(obj.get("x", 0)), float(obj.get("y", 0)))
        size = (float(obj.get("width", 0)), float(obj.get("height", 0)))
        id_ = obj.get("id")
        return HammerBot(pos, size, id=id_)

    @staticmethod
    def _create_drone_bot(obj: Union[Element, Dict[str, Any]], *_) -> Drone:
        pos = (float(obj.get("x", 0)), float(obj.get("y", 0)))
        size = (float(obj.get("width", 0)), float(obj.get("height", 0)))
        id_ = obj.get("id")
        return Drone(pos, size, id=id_)

    @staticmethod
    def _create_rune(
        obj: Union[Element, Dict[str, Any]],
    ) -> Optional[Rune]:
        if isinstance(obj, Element):
            name = obj.get("name")
            pos = (float(obj.get("x", 0)), float(obj.get("y", 0)))
            size = (float(obj.get("width", 0)), float(obj.get("height", 0)))
            props = {}
            properties = obj.find("properties")
            if properties:
                for p in properties.findall("property"):
                    props[p.get("name")] = p.get("value")
            rune_type = props.get("rune_type", "major")
            effect = props.get("effect")
        else:  # dict
            name = obj.get("name")
            pos = obj.get("position", (0, 0))
            size = obj.get("size", (0, 0))
            rune_type = obj.get("rune_type", "major")
            effect = obj.get("effect")

        # Bloqueia runas major já coletadas (opcional)
        # if rune_type == "major" and existing_player:
        #     if any(r.name == name for r in existing_player.spell_system.runes):
        #         return None

        img_path = (
            f"assets/runes/asset32x32/minor_rune.png"
            if rune_type == "minor"
            else f"assets/runes/asset32x32/{name}.png"
        )
        image = AssetLoader.load_image(img_path)
        return Rune(pos, size, name, image, rune_type, 10, effect)

    @staticmethod
    def _create_door(obj: Element, *_) -> Door:
        name = obj.get("name")
        pos = (float(obj.get("x", 0)), float(obj.get("y", 0)))
        size = (float(obj.get("width", 0)), float(obj.get("height", 0)))
        props = {}
        properties = obj.find("properties")
        if properties:
            for p in properties.findall("property"):
                props[p.get("name")] = p.get("value")
        door_spawn = (
            float(props.get("player_spawn_x", 100)),
            float(props.get("player_spawn_y", 300)),
        )
        return Door(pos, size, name, door_spawn)

    @staticmethod
    def _create_alarm(obj: Element, *_) -> Alarm:
        pos = (float(obj.get("x", 0)), float(obj.get("y", 0)))
        size = (float(obj.get("width", 0)), float(obj.get("height", 0)))
        name = obj.get("name")
        return Alarm(pos, size, name)

    @staticmethod
    def create_wave_enemy(
        obj: Union[Element, Dict[str, Any]],
        custom_max_health: Optional[int] = None,
        custom_speed: Optional[float] = None,
    ) -> Optional[Any]:
        """Usado por EnemyWave – cria HammerBot ou Drone com propriedades de wave."""
        if obj.get("type") != "wave_spawn":
            return None

        name = obj.get("name")
        pos = (float(obj.get("x", 0)), float(obj.get("y", 0)))
        size = (float(obj.get("width", 0)), float(obj.get("height", 0)))
        id_ = obj.get("id")

        # propriedades customizadas
        can_fall = False
        facing_right = False
        if isinstance(obj, Element):
            props_elem = obj.find("properties")
            if props_elem:
                for p in props_elem.findall("property"):
                    if p.get("name") == "can_fall":
                        can_fall = p.get("value").lower() == "true"
                    if p.get("name") == "facing_right":
                        facing_right = p.get("value").lower() == "true"

        if name == "hammer_bot":
            enemy = HammerBot(pos, size, custom_max_health=custom_max_health,
                              custom_speed=custom_speed, id=id_)
            enemy.can_fall = can_fall
            enemy.facing_right = facing_right
        elif name == "drone_bot":
            enemy = Drone(pos, size, custom_max_health=custom_max_health,
                          custom_speed=custom_speed, id=id_)
            enemy.facing_right = facing_right
        else:
            print(f"[ObjectFactory] wave_enemy desconhecido: {name}")
            return None

        return enemy

    @staticmethod
    def create_terrain(position: tuple, size: tuple, image: pygame.Surface) -> Terrain:
        return Terrain(position, size, image)
