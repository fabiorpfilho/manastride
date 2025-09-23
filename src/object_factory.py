import pygame
from pygame.math import Vector2
from objects.static_objects.terrain import Terrain
from objects.static_objects.door import Door
from objects.dynamic_objects.rune import Rune
from objects.dynamic_objects.player import Player
from objects.dynamic_objects.hammer_bot import HammerBot
from xml.etree.ElementTree import Element

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
        }

    def create_object(self, obj: Element, player_spawn=None):
        """Cria um objeto com base nos dados do XML do Tiled, com player_spawn opcional."""
        name = obj.get("name")
        type_ = obj.get("type")
        position = (float(obj.get("x", 0)), float(obj.get("y", 0)))
        size = (float(obj.get("width", 0)), float(obj.get("height", 0)))

        properties = obj.find("properties")
        props = {}
        if properties is not None:
            for prop in properties.findall("property"):
                props[prop.get("name")] = prop.get("value")

        # Ignora criação de jogador se player_spawn for fornecido (será tratado em load_map)
        if type_ == "spawn" and name == "player" and player_spawn is not None:
            return None  # Não cria novo jogador, apenas usa player_spawn no Level

        creator = self.object_map.get((type_, name)) or self.object_map.get((type_, None))
        if creator:
            return creator(position, size, name, props, player_spawn)
        print(f"Aviso: Tipo de objeto não suportado: {type_}, nome: {name}")
        return None

    def _create_player(self, position, size, name, props, player_spawn=None):
        """Cria ou reposiciona o jogador, usando player_spawn ou props apenas na criação inicial."""
        # Só usa props ou position se criando um novo jogador
        if self.player is None:
            spawn_position = Vector2(position)
            if "player_spawn_x" in props and "player_spawn_y" in props:
                spawn_position = Vector2(float(props["player_spawn_x"]), float(props["player_spawn_y"]))
            self.player = Player(spawn_position, size)
            self.player.spell_system = self.spell_system
            print(f"Player criado em: {spawn_position}")
        return self.player

    def _create_hammer_bot(self, position, size, name, props, player_spawn=None):
        return HammerBot(position, size)

    def _create_rune(self, position, size, name, props, player_spawn=None):
        if self.player and any(rune.name == name for rune in self.player.spell_system.runes):
            print(f"Runa '{name}' já coletada, não adicionada.")
            return None
        image = self.asset_loader.load_image(f"assets/runes/asset32x32/{name}.png")
        return Rune(position, size, name, image, "major", 10)

    def _create_door(self, position, size, name, props, player_spawn=None):
        door_spawn = (float(props.get("player_spawn_x", 100)), float(props.get("player_spawn_y", 300)))
        print(f"Porta {name} com spawn: {door_spawn}")
        return Door(position, size, name, door_spawn)

    def create_terrain(self, position, size, image):
        return Terrain(position, size, image)

    def update_player_position(self, player, position):
        """Atualiza a posição do jogador existente."""
        player.position = Vector2(position)
        player.sync_position()
        print(f"Player reposicionado em: {player.position}")
        return player