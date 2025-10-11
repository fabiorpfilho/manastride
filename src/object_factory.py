import pygame
from pygame.math import Vector2
from objects.static_objects.terrain import Terrain
from objects.static_objects.door import Door
from objects.static_objects.alarm import Alarm
from objects.dynamic_objects.rune import Rune
from objects.dynamic_objects.player import Player
from objects.dynamic_objects.hammer_bot import HammerBot
from xml.etree.ElementTree import Element
from typing import Union

class ObjectFactory:
    def __init__(self, asset_loader, spell_system, player=None):
        self.asset_loader = asset_loader
        self.spell_system = spell_system
        self.player = player
        self.object_map = {
            ("spawn", "player"): self._create_player,
            ("spawn", "hammer_bot"): self._create_hammer_bot,
            ("rune", None): self._create_rune,
            ("door", None): self._create_door,
            ("alarm", None): self._create_alarm,
        }

    def create_object(self, obj: Element, player_spawn=None):
        """Cria um objeto com base nos dados do XML do Tiled, com player_spawn opcional."""
        if isinstance(obj, Element):
            name = obj.get("name")
            type_ = obj.get("type")
        elif isinstance(obj, dict):
            name = obj.get("name")
            type_ = obj.get("type")

        # Ignora criação de jogador se player_spawn for fornecido (será tratado em load_map)
        if type_ == "spawn" and name == "player" and player_spawn is not None:
            return None  # Não cria novo jogador, apenas usa player_spawn no Level

        creator = self.object_map.get((type_, name)) or self.object_map.get((type_, None))
        if creator:
            return creator(obj)
        print(f"Aviso: Tipo de objeto não suportado: {type_}, nome: {name}")
        return None

    def _create_player(self, obj: Element):
        """Cria ou reposiciona o jogador, usando props apenas na criação inicial."""
        position = (float(obj.get("x", 0)), float(obj.get("y", 0)))
        size = (float(obj.get("width", 0)), float(obj.get("height", 0)))
        properties = obj.find("properties")
        props = {}
        if properties is not None:
            for prop in properties.findall("property"):
                props[prop.get("name")] = prop.get("value")

        # Só usa props ou position se criando um novo jogador
        if self.player is None:
            spawn_position = Vector2(position)
            if "player_spawn_x" in props and "player_spawn_y" in props:
                spawn_position = Vector2(float(props["player_spawn_x"]), float(props["player_spawn_y"]))
            self.player = Player(spawn_position, size)
            self.player.spell_system = self.spell_system
            print(f"Player criado em: {spawn_position}")
        return self.player

    def _create_hammer_bot(self, obj: Element):
        """Cria um HammerBot com base no elemento XML."""
        position = (float(obj.get("x", 0)), float(obj.get("y", 0)))
        size = (float(obj.get("width", 0)), float(obj.get("height", 0)))
        return HammerBot(position, size)
    
    def create_wave_enemy(self, obj):
        """Cria um HammerBot a partir dos dados de wave_spawn, considerando can_fall."""
        if obj.get("type") != "wave_spawn" or obj.get("name") != "hammer_bot":
            return None
        
        position = (float(obj.get("x", 0)), float(obj.get("y", 0)))
        size = (float(obj.get("width", 0)), float(obj.get("height", 0)))
        
        # Extract properties
        properties = obj.find("properties")
        can_fall = False
        facing_right = True  # Default value
        if properties is not None:
            for prop in properties.findall("property"):
                if prop.get("name") == "can_fall":
                    can_fall = prop.get("value").lower() == "true"
                    break
                elif prop.get("name") == "facing_right":
                    facing_right = prop.get("value").lower() == "true"
        
        enemy = HammerBot(position, size)
        enemy.can_fall = can_fall  # Define a propriedade can_fall
        enemy.facing_right = facing_right  # Define a direção inicial
        print(f"HammerBot criado em: {position}, can_fall: {can_fall}")
        return enemy

    def _create_rune(self, obj: Union[Element, dict]):
        """Cria uma runa com base no elemento XML ou dicionário."""
        if isinstance(obj, Element):
            name = obj.get("name")
            position = (float(obj.get("x", 0)), float(obj.get("y", 0)))
            size = (float(obj.get("width", 0)), float(obj.get("height", 0)))
            properties = obj.find("properties")
            props = {}
            if properties is not None:
                for prop in properties.findall("property"):
                    props[prop.get("name")] = prop.get("value")
            rune_type = props.get("rune_type", "major")
            effect = props.get("effect", None)
        elif isinstance(obj, dict):
            name = obj.get("name")
            position = obj.get("position", (0, 0))
            size = obj.get("size", (0, 0))
            rune_type = obj.get("rune_type", "major")
            effect = obj.get("effect", None)

        if rune_type == "major" and self.player and any(rune.name == name for rune in self.player.spell_system.runes):
            print(f"Runa '{name}' já coletada, não adicionada.")
            return None

        if rune_type == "minor":
            image = self.asset_loader.load_image(f"assets/runes/asset32x32/minor_rune.png")
        else:
            image = self.asset_loader.load_image(f"assets/runes/asset32x32/{name}.png")
        return Rune(position, size, name, image, rune_type, 10, effect)

    def _create_door(self, obj: Element):
        """Cria uma porta com base no elemento XML."""
        name = obj.get("name")
        position = (float(obj.get("x", 0)), float(obj.get("y", 0)))
        size = (float(obj.get("width", 0)), float(obj.get("height", 0)))
        properties = obj.find("properties")
        props = {}
        if properties is not None:
            for prop in properties.findall("property"):
                props[prop.get("name")] = prop.get("value")

        door_spawn = (float(props.get("player_spawn_x", 100)), float(props.get("player_spawn_y", 300)))
        print(f"Porta {name} com spawn: {door_spawn}")
        return Door(position, size, name, door_spawn)
    def _create_alarm(self, obj: Element):
        """Cria um alarme com base no elemento XML."""
        position = (float(obj.get("x", 0)), float(obj.get("y", 0)))
        size = (float(obj.get("width", 0)), float(obj.get("height", 0)))
        name = obj.get("name")
        return Alarm(position, size, name)

    def create_terrain(self, position, size, image):
        print("Tamanho:", size)
        """Cria um terreno (mantido sem alterações, pois não usa XML diretamente)."""
        return Terrain(position, size, image)

    def update_player_position(self, player, position):
        """Atualiza a posição do jogador existente."""
        player.position = Vector2(position)
        player.sync_position()
        print(f"Player reposicionado em: {player.position}")
        return player