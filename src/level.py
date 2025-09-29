import xml.etree.ElementTree as ET
import random
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
from object_factory import ObjectFactory

class Level:
    def __init__(self, screen, level_name):
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
        self.level_name = level_name
        self.status_bar = StatusBar(self.screen, self.asset_loader)
        self.score_ui = Score(self.screen, self.asset_loader)
        self.hotbar = HotBar(self.screen, self.asset_loader)
        self.is_completed = False
        self.object_factory = ObjectFactory(self.asset_loader, self.spell_system, self.player)
        self.current_spawn = None
        self.minor_rune_effects = [
            {"power": 5},  # Aumenta o poder
            {"cost": -10},  # Reduz o custo
            {"cooldown": -5},  # Reduz a recarga
            {"power": 15, "cost": 10},  # Aumenta o poder, mas aumenta o custo
            {"cooldown": 10, "cost": -8},  # Aumenta a recarga, mas reduz o custo
            {"power": 10, "cooldown": 8},  # Aumenta o poder, mas aumenta a recarga
            {"power": -5, "cooldown": -10},  # Reduz o poder, mas reduz a recarga
            {"cost": -5, "cooldown": -5, "power": -8}  # Reduz custo e recarga, mas reduz o poder
        ]
        # Listas para rastrear efeitos usados
        self.available_effects = self.minor_rune_effects.copy()
        self.used_effects = []

        self.load_map(level_name)

    def load_map(self, level_name, player_spawn=None):
        self.level_name = level_name
        self.current_spawn = player_spawn
        self.map_data = self.asset_loader.load_map_data(level_name)
        if self.map_data is None:
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
        
        self.all_sprites = []
        self.enemies = []
        self.dynamic_objects = [self.player] if self.player else []
        self.static_objects = []
        
        self._process_objects(player_spawn)

        if self.player and player_spawn is not None:
            self.object_factory.update_player_position(self.player, player_spawn)
        self.all_sprites += self.dynamic_objects + self.static_objects
        
        self._process_tilemap()
            
        self.collision_manager = CollisionManager(self.dynamic_objects, self.static_objects, world_width)

    def _process_objects(self, player_spawn=None):
        """Processa a camada de objetos do mapa usando ObjectFactory."""
        object_group = self.map_data.find("objectgroup[@name='objects']")
        if object_group is None:
            print("Erro: Nenhuma camada de objetos 'objects' encontrada no mapa")
            return

        for obj in object_group.findall("object"):
            new_obj = self.object_factory.create_object(obj, player_spawn)
            if new_obj:
                if isinstance(new_obj, (Player, HammerBot, Rune)):
                    if isinstance(new_obj, Player):
                        print("New object: ", new_obj.position)
                        self.player = new_obj
                    elif isinstance(new_obj, HammerBot):
                        self.enemies.append(new_obj)
                    self.dynamic_objects.append(new_obj)
                else:  # Portas e outros estáticos
                    self.static_objects.append(new_obj)

    def _process_tilemap(self):
        """Processa a camada de blocos do mapa Tiled usando ObjectFactory para terrenos."""
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
                        terrain = self.object_factory.create_terrain(
                            position=(x, y),
                            size=(self.tile_width, self.tile_height),
                            image=self.tileset[gid]
                        )
                        self.all_sprites.append(terrain)
                        self.static_objects.append(terrain)

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
            # self.load_map(self.level_name, self.current_spawn)
            self.reset()

        for obj in self.dynamic_objects[:]:
            if isinstance(obj, HammerBot):
                if obj.marked_for_removal:
                    self.score += 100
                    self.generate_minor_rune(obj)
                    self.dynamic_objects.remove(obj)
                    self.enemies.remove(obj)
                else:
                    obj.update(delta_time, self.static_objects)
            elif hasattr(obj, "marked_for_removal"):
                if obj.marked_for_removal:
                    self.dynamic_objects.remove(obj)
                    self.all_sprites.remove(obj)
            elif isinstance(obj, Player):
                obj.update(delta_time)
            elif isinstance(obj, Rune):
                    obj.update(delta_time)

    
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
        
        if self.level_name == "level_2":
            if self.collision_manager.door_triggered:
                target_map, player_spawn = self.collision_manager.door_triggered
                if target_map == "level_3":
                    print("Level_2 completed: Transition to level_3 detected")
                    self.is_completed = True
                    return None
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
            

            
    def generate_minor_rune(self, obj):
        """Gera uma runa menor com um efeito aleatório, evitando repetição até que todos sejam usados."""
        if not self.available_effects:
            # Se todos os efeitos foram usados, reinicia a lista
            self.available_effects = self.used_effects.copy()
            self.used_effects = []
        effect = random.choice(self.available_effects)
        self.available_effects.remove(effect)
        self.used_effects.append(effect)
        minor_rune = self.object_factory.create_object({
            'position': (obj.position.x + (obj.size[0] / 2), obj.position.y),
            'size': (11, 15),
            'name': 'Runa menor',
            'type': 'rune',
            'rune_type': 'minor',
            'effect': effect
        })
        if minor_rune:  # Verifica se a runa foi criada com sucesso
            self.dynamic_objects.append(minor_rune)
            self.all_sprites.append(minor_rune)

    def reset(self):
        self.player.health = 100
        self.player.mana = 100
        self.player.position = Vector2(100, 300)
        self.player.sync_position()
        self.enemies = [self.object_factory.create_object({
            'type': 'spawn',
            'name': 'hammer_bot',
            'position': (300, 300),
            'size': (22, 31)
        })]
        self.dynamic_objects = [self.player] + self.enemies
        self.all_sprites = self.static_objects + self.dynamic_objects
        self.score = 0
        self.camera.target = self.player
        self.camera.offset = Vector2(0, 0)
        self.collision_manager = CollisionManager(self.dynamic_objects, self.static_objects, self.map_width * self.tile_width)