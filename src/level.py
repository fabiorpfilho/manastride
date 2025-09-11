import pygame
import json
import xml.etree.ElementTree as ET
import os
from objects.static_objects.terrain import Terrain
from objects.static_objects.door import Door
from objects.dynamic_objects.rune import Rune
from objects.dynamic_objects.player import Player
from objects.dynamic_objects.hammer_bot import HammerBot
from collision_manager import CollisionManager
from camera import Camera
from spell_system.spell_system import SpellSystem
from pygame.math import Vector2
from asset_loader import AssetLoader
from ui.score import Score
from ui.status_bar import StatusBar
from ui.hotbar import HotBar

class Level:
    def __init__(self, screen, level_name, player_spawn=None):
        self.screen = screen
        self.all_sprites = []
        self.player = None
        self.enemies = []
        self.dynamic_objects = []
        self.static_objects = []
        self.background = [0, 0, 0]
        self.background_layers = []
        self.tile_size = 24 
        self.score = 0
        self.spell_system = SpellSystem()
        self.asset_loader = AssetLoader()
        self.level_name = level_name  # Store the current level name
        self.status_bar = StatusBar(self.screen, self.asset_loader)
        self.score_ui = Score(self.screen, self.asset_loader)
        self.hotbar = HotBar(self.screen, self.asset_loader)
        self.is_completed = False
    

        self.load_map(level_name, player_spawn)

    def load_map(self, level_name, player_spawn=None):
        self.actual_map = level_name
        self.level_name = level_name  # Update level_name on load
        self.map_data = self.asset_loader.load_map_data(level_name)
        if self.map_data is None:
            return
        
        # Configurações do mapa
        self.tile_width = int(self.map_data.get("tilewidth"))
        self.tile_height = int(self.map_data.get("tileheight"))
        self.map_width = int(self.map_data.get("width"))
        self.map_height = int(self.map_data.get("height"))

        world_width = self.map_width * self.tile_width
        world_height = self.map_height * self.tile_height

        # Atualizar a câmera com novas dimensões do mundo
        if not hasattr(self, 'camera'):
            self.camera = Camera(self.screen.get_size(), world_width, world_height, zoom=4.0)
        else:
            self.camera.world_width = world_width
            self.camera.world_height = world_height
        
        # Carregar o tileset
        self.tileset = self.asset_loader.load_tileset(self.map_data)
        self.background_layers = self.asset_loader.load_background_layers(
            screen_size=self.screen.get_size(),
            world_size=(world_width, world_height),
            camera_zoom=self.camera.zoom
        )
        
        # Limpar objetos existentes (mantendo o player se já existir)
        self.all_sprites = []
        self.enemies = []
        if self.player:
            self.dynamic_objects = [self.player]
        else:
            self.dynamic_objects = []
        self.static_objects = []
        
        # Processar a camada de blocos
        self._process_objects(player_spawn)
        self.all_sprites += self.dynamic_objects
        
        self._process_tilemap()
            
        self.collision_manager = CollisionManager(self.dynamic_objects, self.static_objects, world_width)

    def _process_objects(self, player_spawn=None):
        """Processa a camada de objetos do mapa (player, inimigos, runas, portas etc)."""
        object_group = self.map_data.find("objectgroup[@name='objects']")
        if object_group is None:
            print("Erro: Nenhuma camada de objetos 'objects' encontrada no mapa")
            return

        for obj in object_group.findall("object"):
            name = obj.get("name")
            type_ = obj.get("type")
            x = float(obj.get("x", 0))
            y = float(obj.get("y", 0))
            height = float(obj.get("height", 0))
            width = float(obj.get("width", 0))
            position = (x, y)
            size = (width, height)

            # Inicializa as variáveis de spawn do jogador como None
            player_spawn_x = None
            player_spawn_y = None

            # Busca as propriedades dentro do elemento <properties>
            properties = obj.find("properties")
            if properties is not None:
                for prop in properties.findall("property"):
                    if prop.get("name") == "player_spawn_x":
                        player_spawn_x = float(prop.get("value"))
                    elif prop.get("name") == "player_spawn_y":
                        player_spawn_y = float(prop.get("value"))

            if type_ == "spawn":
                if name == "player":
                    spawn_position = player_spawn if player_spawn is not None else position
                    spawn_position = pygame.math.Vector2(spawn_position)
                    self.player_spawn = spawn_position
                    
                    if self.player is None:
                        self.player = Player(spawn_position, size)
                        self.player.spell_system = self.spell_system
                        self.dynamic_objects.append(self.player)
                    else:
                        self.player.position = spawn_position
                        self.player.sync_position()
                    print(f"Player positioned at: {spawn_position}")
                elif name == "hammer_bot":
                    enemy = HammerBot(position, size)
                    self.enemies.append(enemy)
                    self.dynamic_objects.append(enemy)
            elif type_ == "rune":
                # Check if the rune is already in the player's inventory
                if self.player and any(rune.name == name for rune in self.player.spell_system.runes):
                    print(f"Runa '{name}' já coletada, não será adicionada ao mapa.")
                    continue  # Skip adding the rune if it's already collected
                image = self.asset_loader.load_image(f"assets/runes/asset32x32/{name}.png")
                rune = Rune(position, size, name, image, "major", 10)
                self.dynamic_objects.append(rune)
                print(f"Runa '{name}' adicionada na posição {position}")
            elif type_ == "door":
                if player_spawn_x is not None and player_spawn_y is not None:
                    door_spawn = (player_spawn_x, player_spawn_y)
                    print(f"Player spawn for door {name}: {door_spawn}")
                    door = Door(position, size, name, door_spawn)
                    self.static_objects.append(door)
                    self.all_sprites.append(door)
                else:
                    print(f"Aviso: Propriedades player_spawn_x e player_spawn_y não encontradas para a porta {name}. Usando spawn padrão.")
                    default_spawn = (100, 300)
                    door = Door(position, size, name, default_spawn)
                    self.static_objects.append(door)
                    self.all_sprites.append(door)
    def _process_tilemap(self):
        """Processa a camada de blocos do mapa Tiled."""
        layer = self.map_data.find("layer")
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
                        platform = Terrain(
                            position=(x, y),
                            size=(self.tile_width, self.tile_height),
                            image=self.tileset[gid]
                        )
                        self.all_sprites.append(platform)
                        self.static_objects.append(platform)

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

        for spell in self.player.spell_system.spellbook:
            spell.draw(self.screen, self.camera)
            
        if self.player:
            self.status_bar.draw(self.player)
            self.hotbar.draw(self.player)

        self.score_ui.draw(self.score)

        for obj in self.dynamic_objects:
            obj.draw_colliders_debug(self.screen, self.camera)

    def update(self, delta_time):
        if self.player.health <= 0:
            self.reset()

        for obj in self.dynamic_objects[:]:
            if isinstance(obj, HammerBot):
                if obj.marked_for_removal:
                    self.score += 100
                    self.dynamic_objects.remove(obj)
                    self.all_sprites.remove(obj)
                    self.enemies.remove(obj)
                else:
                    obj.update(delta_time, self.static_objects)
            elif isinstance(obj, Player):
                obj.update(delta_time)
            elif isinstance(obj, Rune):
                if obj.marked_for_removal:
                    self.dynamic_objects.remove(obj)
                    self.all_sprites.remove(obj)
                else:
                    obj.update(delta_time)
            elif hasattr(obj, "marked_for_removal"):
                if obj.marked_for_removal:
                    self.dynamic_objects.remove(obj)
                    self.all_sprites.remove(obj)
    
        player_pos = [self.player.position.x + self.player.size[0] / 2, 
                      self.player.position.y + self.player.size[1] / 2]
        
        self.player.spell_system.update(delta_time, player_pos)

        for spell in self.player.spell_system.spellbook:
            if not spell:
                continue
            if hasattr(spell, "projectiles"):
                for proj in spell.projectiles:
                    if proj not in self.dynamic_objects:
                        self.dynamic_objects.append(proj)
                        self.all_sprites.append(proj)
            if hasattr(spell, "shields"):
                for shield in spell.shields:
                    if spell.major_rune and spell.major_rune.name == "fan" and shield not in self.static_objects:
                        self.static_objects.append(shield)
                        self.all_sprites.append(shield)
                    elif shield not in self.dynamic_objects:
                        self.dynamic_objects.append(shield)
                        self.all_sprites.append(shield)

        self.collision_manager.update(self.dynamic_objects)
        
        # Check for game completion conditions in level_2
        if self.level_name == "level_2":
            # Condition 1: Transition to level_3
            if self.collision_manager.door_triggered:
                target_map, player_spawn = self.collision_manager.door_triggered
                if target_map == "level_3":
                    print("Level_2 completed: Transition to level_3 detected")
                    self.is_completed = True
                    return None  # Prevent level transition
            # Condition 2: No more HammerBot enemies
            if not any(isinstance(obj, HammerBot) for obj in self.dynamic_objects):
                print("Level_2 completed: No more HammerBot enemies")
                self.is_completed = True
                return None
        
        if self.collision_manager.door_triggered:
            print(f"Door triggered: {self.collision_manager.door_triggered}")
            door_triggered = self.collision_manager.door_triggered
            target_map, player_spawn = door_triggered
            self.load_map(target_map, player_spawn)
            return
        
        self.camera.update(self.player)   

        for layer in self.background_layers:
            layer['offset_x'] = -self.camera.offset.x * layer['parallax_factor']
            layer['offset_y'] = -self.camera.offset.y * layer['parallax_factor']

    def reset(self):
            self.player.health = 100
            self.player.mana = 100
            self.player.position = pygame.math.Vector2(100, 300)
            self.player.sync_position()
            self.enemies = [HammerBot((300, 300), (22, 31))]
            self.dynamic_objects = [self.player] + self.enemies
            self.all_sprites = self.static_objects + self.dynamic_objects
            self.score = 0
            self.camera.target = self.player
            self.camera.offset = Vector2(0, 0)
            self.collision_manager = CollisionManager(self.dynamic_objects, self.static_objects, self.map_width * self.tile_width)