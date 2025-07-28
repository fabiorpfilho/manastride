import pygame
import json
import xml.etree.ElementTree as ET
import os
from objects.static_objects.terrain import Terrain
from objects.dynamic_objects.player import Player
from objects.dynamic_objects.hammer_bot import HammerBot
from collision_manager import CollisionManager
from camera import Camera
from spell_system.spell_system import SpellSystem
from spell_system.spells.projectile import Projectile
from pygame.math import Vector2
from objects.sprite import Sprite
from objects.animation import Animation
from objects.animation_type import AnimationType
from objects.animation_manager import AnimationManager

class Level:
    def __init__(self, screen, level_name):
        self.screen = screen
        self.all_sprites = []
        self.platforms = []
        self.background = [0, 0, 0]
        self.background_layers = []
        self.tile_size = 24 
        
        self.spell_system = SpellSystem()
        self._setup_spells()

        try:
            tree = ET.parse(f"src/levels/{level_name}.xml")
            self.map_data = tree.getroot()
        except FileNotFoundError:
            print(f"Erro: O arquivo {level_name}.xml não foi encontrado!")
            return
        
        # Configurações do mapa
        self.tile_width = int(self.map_data.get("tilewidth"))
        self.tile_height = int(self.map_data.get("tileheight"))
        self.map_width = int(self.map_data.get("width"))
        self.map_height = int(self.map_data.get("height"))

        # Configurar a câmera com zoom inicial
        world_width = self.map_width * self.tile_width
        world_height = self.map_height * self.tile_height
        self.camera = Camera(screen.get_size(), world_width, world_height, zoom=3.0)
        
        # Carregar o tileset
        self.tileset = self._load_tileset() 
        self._setup_background()
        
        animation_manager = AnimationManager()

        spawn_x, spawn_y = 100, 300 
        self.player = Player(
            position=(spawn_x, spawn_y),
            size=(20, 30),  
            animation_manager=animation_manager
        )

        enemy_animation_manager = AnimationManager()
        self.enemy = HammerBot(
            position=(300, 300),
            size=(22, 31),  
            animation_manager=enemy_animation_manager,
        )
        self.all_sprites.append(self.enemy)

        self.all_sprites.append(self.player)
        self.player.spell_system = self.spell_system 
        
        # Processar a camada de blocos
        self._process_tilemap()
            
        self.dynamic_objects = [self.player, self.enemy]
        self.collision_manager = CollisionManager(
            self.dynamic_objects, self.platforms, world_width)

    def _setup_background(self):
        """Configura as camadas de fundo parallax com superfícies otimizadas."""
        parallax_factors = [
            (0.2, "src/levels/oak_woods_v1.0/background/background_layer_1.png"),
            (0.5, "src/levels/oak_woods_v1.0/background/background_layer_2.png"),
            (0.8, "src/levels/oak_woods_v1.0/background/background_layer_3.png")
        ]

        screen_width, screen_height = self.screen.get_size()
        world_width = self.map_width * self.tile_width
        world_height = self.map_height * self.tile_height

        for factor, path in parallax_factors:
            try:
                image = pygame.image.load(path).convert_alpha()
                # Escalar a imagem para cobrir o tamanho do mundo visível, ajustado pelo zoom e parallax
                scaled_width = int(world_width / self.camera.zoom / factor) + screen_width
                scaled_height = int(world_height / self.camera.zoom / factor) + screen_height
                scaled_image = pygame.transform.scale(image, (scaled_width, scaled_height))
                # Criar superfície mínima para cobrir a tela
                print(f"Scaled image size: {scaled_width}x{scaled_height}")
                layer_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
                layer_surface.blit(scaled_image, (0, 0))
                self.background_layers.append({
                    'surface': layer_surface,
                    'parallax_factor': factor,
                    'offset_x': 0,
                    'offset_y': 0
                })
            except FileNotFoundError:
                print(f"Erro: Não foi possível carregar {path}")
                continue

    def _load_tileset(self):
        """Carrega a imagem do tileset e divide em tiles individuais."""
        tileset = self.map_data.find("tileset")
        image_path = tileset.find("image").get("source")
        tile_width = int(tileset.get("tilewidth"))
        tile_height = int(tileset.get("tileheight"))
        columns = int(tileset.get("columns"))
        tilecount = int(tileset.get("tilecount"))

        tileset_image = pygame.image.load(os.path.join("src/levels", image_path)).convert_alpha()

        tiles = {}
        firstgid = int(tileset.get("firstgid"))

        for gid in range(firstgid, firstgid + tilecount):
            col = (gid - firstgid) % columns
            row = (gid - firstgid) // columns
            x = col * tile_width
            y = row * tile_height
            tile_rect = pygame.Rect(x, y, tile_width, tile_height)
            tile_image = tileset_image.subsurface(tile_rect)
            tiles[gid] = tile_image

        return tiles
        
    def _setup_spells(self):
        ice_spell = Projectile(
            major_rune=self.spell_system.runes[2],
            minor_runes=[self.spell_system.runes[3]]
        )
        fan_spell = Projectile(
            major_rune=self.spell_system.runes[0],
            minor_runes=[self.spell_system.runes[4]]
        )

        self.spell_system.spellbook.append(ice_spell)
        self.spell_system.spellbook.append(fan_spell)

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
                        self.platforms.append(platform)
                        # print(f"Plataforma adicionada: <rect({x}, {y}, {self.tile_width}, {self.tile_height})>")

    def _process_legacy_tiles(self, tiles):
        for item in tiles:
            position = item["position"]
            size = item.get("size", [self.tile_size, self.tile_size])
            if item["type"] == "platform":
                platform = Terrain(position, size)
                self.all_sprites.append(platform)
                self.platforms.append(platform)

    def update(self, delta_time):
        # Limitar delta_time para evitar picos
        # print(f"Delta time: {delta_time}")  # Debug

        self.player.movement_update(delta_time)
        self.enemy.movement_update(delta_time, self.platforms)
        player_pos = [self.player.position.x + self.player.size[0] / 2, 
                      self.player.position.y + self.player.size[1] / 2]
        
        for spell in self.spell_system.spellbook:
            self.dynamic_objects.extend(spell.projectiles)
        # print(f"Antes CollisionManager: HammerBot pos={self.enemy.position}")
        self.collision_manager.update(self.dynamic_objects)
        # print(f"Após CollisionManager: HammerBot pos={self.enemy.position}")
        self.camera.update(self.player.rect)   
        
        # Atualizar os offsets do fundo com base no movimento da câmera
        for layer in self.background_layers:
            layer['offset_x'] = -self.camera.offset.x * layer['parallax_factor']
            layer['offset_y'] = -self.camera.offset.y * layer['parallax_factor']
    
        for spell in self.spell_system.spellbook:
            spell.update(delta_time, player_pos)

    def draw(self):
        # print(f"Desenhando nível com {len(self.all_sprites)} sprites e {len(self.platforms)} plataformas")
        self.screen.fill(self.background)
        
        # Desenha as camadas de fundo com parallax
        screen_width, screen_height = self.screen.get_size()
        # print(f"Screen size: {screen_width}x{screen_height}")
        i = 0
        for layer in self.background_layers:
            surface = layer['surface']
            factor = layer['parallax_factor']
            offset_x = (layer['offset_x'] % surface.get_width()) - surface.get_width()
            offset_y = (layer['offset_y'] % surface.get_height()) - surface.get_height()
            # print(f"Surface width: {surface.get_width()}, Offset: ({offset_x}, {offset_y})")
            # print(f"surface height: {surface.get_height()}")
            # Desenhar cópias suficientes para cobrir a tela
            for x in range(0, screen_width + surface.get_width(), surface.get_width()):
                # print(f"X ({x})")
                for y in range(0, screen_height + surface.get_height(), surface.get_height()):
                    # print(f"Y: {y})")
                    # print(f"Drawing background layer at offset ({offset_x + x}, {offset_y + y}) with factor {factor}")
                    # print(f"Drawing background layer {i} at offset ({offset_x + x}, {offset_y + y}) with factor {factor}")
                    
                    self.screen.blit(surface, (offset_x + x, offset_y + y))
            i += 1

        # Desenha todos os sprites com o offset da câmera e zoom
        for sprite in self.all_sprites:
            offset_rect = self.camera.apply(sprite.rect, sprite == self.player)
            scaled_image = self.camera.apply_surface(sprite.image)
            self.screen.blit(scaled_image, offset_rect)

        # Debug do player e inimigo
        offset_player_rect = self.camera.apply(self.player.rect)
        self.player.draw_colliders_debug(self.screen, self.camera)
        offset_enemy_rect = self.camera.apply(self.enemy.rect)
        self.enemy.draw_colliders_debug(self.screen, self.camera)
        self.enemy.draw_sensors_debug(self.screen, self.camera)

        # Desenha os projéteis com zoom
        for spell in self.spell_system.spellbook:
            spell.draw(self.screen, self.camera)

        # Debug das plataformas
        for platform in self.platforms:
            offset_platform_rect = self.camera.apply(platform.rect)
            platform.draw_colliders_debug(self.screen, self.camera)