import pygame
import json
import xml.etree.ElementTree as ET
import os
import logging
from objects.dynamic_objects.rune import Rune
from objects.dynamic_objects.player import Player
from objects.dynamic_objects.hammer_bot import HammerBot
from objects.dynamic_objects.drone import Drone
from collision_manager import CollisionManager
from camera import Camera
from spell_system.spell_system import SpellSystem
from pygame.math import Vector2
from asset_loader import AssetLoader
from ui.score import Score
from ui.status_bar import StatusBar
from ui.hotbar import HotBar
from object_factory import ObjectFactory
from entity_manager import EntityManager

class Level:
    def __init__(self, screen, level_name, player=None, player_spawn=None, total_score=0, persistent_dead_ids=None, minor_rune_drop_state=None):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)
        self.screen = screen
        self.all_sprites = []
        self.asset_loader = AssetLoader()
        if player and hasattr(player, 'spell_system') and player.spell_system:
            self.spell_system = player.spell_system
        else:
            self.spell_system = SpellSystem()
        print("Minor rune drop state on level init:", minor_rune_drop_state)
        self.entity_manager = EntityManager(
            self.spell_system,
            ObjectFactory(self.asset_loader, self.spell_system, player),
            minor_rune_drop_state=minor_rune_drop_state  # Pass the state
        )
        self.static_objects = []
        self.background = [0, 0, 0]
        self.background_layers = []
        self.tile_size = 24
        self.score = 0
        self.total_score = total_score
        self.level_name = level_name
        self.status_bar = StatusBar(self.screen, self.asset_loader)
        self.score_ui = Score(self.screen, self.asset_loader)
        self.hotbar = HotBar(self.screen, self.asset_loader)
        self.is_completed = False
        self.current_spawn = player_spawn
        self.persistent_dead_ids = persistent_dead_ids
        self.current_dead_ids = []

        self.load_map(level_name, player, player_spawn)

    def load_map(self, level_name, player=None, player_spawn=None):
        print(f"Carregando mapa: {level_name} com spawn em {player_spawn}")
        self.all_sprites = []
        self.static_objects = []
        self.current_map = level_name
        self.level_name = level_name
        self.map_data = self.asset_loader.load_map_data(level_name)
        if self.map_data is None:
            self.logger.error("Falha ao carregar dados do mapa")
            return
        
        self.tile_width = int(self.map_data.get("tilewidth"))
        self.tile_height = int(self.map_data.get("tileheight"))
        self.map_width = int(self.map_data.get("width"))
        self.map_height = int(self.map_data.get("height"))

        world_width = self.map_width * self.tile_width
        world_height = self.map_height * self.tile_height

        if not hasattr(self, 'camera'):
            self.camera = Camera(self.screen.get_size(), world_width, world_height, zoom=4.0)
        else:
            self.camera.world_width = world_width
            self.camera.world_height = world_height
        
        self.tileset = self.asset_loader.load_tileset(self.map_data)
        self.background_layers = self.asset_loader.load_background_layers(
            screen_size=self.screen.get_size(),
            world_size=(world_width, world_height),
            camera_zoom=self.camera.zoom
        )
        
        # Process tilemap
        self._process_tilemap()
        
        # Verify terrain creation
        if not self.static_objects:
            self.logger.warning("Nenhum terreno foi criado. Verifique o tilemap.")
            
        
        self.entity_manager.entities = [player] if player else []
        # Só processa objetos após o tilemap estar concluído
        self._process_objects(player_spawn)
        player = self.entity_manager.get_player()

        if player and player_spawn is not None:
            self.entity_manager.object_factory.update_player_position(self.entity_manager.get_player(), player_spawn)
        self.current_spawn = Vector2(player.position)
        self.all_sprites = self.entity_manager.entities + self.static_objects
        self.collision_manager = CollisionManager(self.entity_manager.entities, self.static_objects, world_width)

    def _process_tilemap(self):
        """Processa a camada de blocos do mapa Tiled usando ObjectFactory para terrenos."""
        layer = self.map_data.find("layer")
        if layer is None:
            self.logger.error("Nenhuma camada de tilemap encontrada")
            return

        data = layer.find("data").text.strip()
        rows = [row for row in data.splitlines() if row.strip()]
        tilemap = []
        for row in rows:
            tiles = [int(tile) if tile.strip() else 0 for tile in row.split(",")]
            tilemap.append(tiles)

        for row_idx, row in enumerate(tilemap):
            for col_idx, gid in enumerate(row):
                if gid != 0:
                    x = col_idx * self.tile_width
                    y = row_idx * self.tile_height
                    if gid in self.tileset:
                        terrain = self.entity_manager.object_factory.create_terrain(
                            position=(x, y),
                            size=(self.tile_width, self.tile_height),
                            image=self.tileset[gid]
                        )
                        self.all_sprites.append(terrain)
                        self.static_objects.append(terrain)

    def _process_objects(self, player_spawn=None):
        """Processa a camada de objetos do mapa usando ObjectFactory."""
        object_group = self.map_data.find("objectgroup[@name='objects']")
        if object_group is None:
            self.logger.error("Nenhuma camada de objetos 'objects' encontrada no mapa")
            return

        for obj in object_group.findall("object"):
            id_ = obj.get("id")
            if obj.get("type") == "spawn" and (obj.get("name") == "hammer_bot" or obj.get("name") == "drone_bot") and id_ in self.persistent_dead_ids:
                continue
            new_obj = self.entity_manager.object_factory.create_object(obj, player_spawn)
            if new_obj:
                if isinstance(new_obj, (Player, HammerBot, Rune, Drone)):
                    is_enemy = isinstance(new_obj, (HammerBot, Drone))
                    self.entity_manager.add_entity(new_obj, is_enemy=is_enemy)
                    self.all_sprites.append(new_obj)
                else:  # Portas e outros estáticos
                    self.static_objects.append(new_obj)
                    self.all_sprites.append(new_obj)

    def draw(self):
        self.screen.fill(self.background)
        screen_width, screen_height = self.screen.get_size()
        for layer in self.background_layers:
            surface = layer['surface']
            offset_x = (layer['offset_x'] % surface.get_width()) - surface.get_width()
            offset_y = (layer['offset_y'] % surface.get_height()) - surface.get_height()
            for x in range(0, screen_width + surface.get_width(), surface.get_width()):
                for y in range(0, screen_height + surface.get_height(), surface.get_height()):
                    self.screen.blit(surface, (offset_x + x, offset_y + y))

        for sprite in self.all_sprites:
            offset_rect = self.camera.apply(sprite.rect)
            scaled_image = self.camera.apply_surface(sprite.image)
            self.screen.blit(scaled_image, offset_rect)

        for spell in self.spell_system.spellbook:
            spell.draw(self.screen, self.camera)
            
        player = self.entity_manager.get_player()
        if player:
            self.status_bar.draw(player)
            self.hotbar.draw(player)

        self.score_ui.draw(self.total_score + self.score)

        for obj in self.entity_manager.entities:
            obj.draw_colliders_debug(self.screen, self.camera)

    def update(self, delta_time):
        player = self.entity_manager.get_player()
        if player and player.health <= 0:
            self.reset()

        self.entity_manager.update(
            delta_time,
            self.static_objects,
            lambda points: setattr(self, 'score', self.score + points),
            self.all_sprites,
            lambda id_: self.current_dead_ids.append(id_),
            self.current_dead_ids
        )

        self.collision_manager.update(self.entity_manager.entities)
        
        
        if self.collision_manager.door_triggered:
            self.logger.info(f"Door triggered: {self.collision_manager.door_triggered}")
            target_map, player_spawn = self.collision_manager.door_triggered
            self.collision_manager.door_triggered = None
            return (target_map, player_spawn, player, self.entity_manager.minor_rune_drop_state)
        
        self.camera.update(self.entity_manager.get_player())

        for layer in self.background_layers:
            layer['offset_x'] = -self.camera.offset.x * layer['parallax_factor']
            layer['offset_y'] = -self.camera.offset.y * layer['parallax_factor']

    def reset(self):
        player = self.entity_manager.get_player()
        self.entity_manager.entities = [player] if player else []
        self.load_map(self.current_map, player, self.current_spawn)
        if player:
            player.health = player.max_health
            player.mana = player.max_mana
        self.score = 0