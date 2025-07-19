import pygame
import json
import xml.etree.ElementTree as ET
import os
from objects.static_objects.terrain import Terrain
from objects.dynamic_objects.player import Player
from collision_manager import CollisionManager
from camera import Camera
from spell_system.spell_system import SpellSystem
from spell_system.spells.projectile import Projectile
from pygame.math import Vector2

class Level:
    def __init__(self, screen, level_name):
        self.screen = screen
        self.all_sprites = []
        self.platforms = []
        self.background_color = [0, 0, 0]
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

        # Configurar a câmera com zoom inicial (exemplo: 2.0 para blocos de 32px parecerem maiores)
        world_width = self.map_width * self.tile_width
        world_height = self.map_height * self.tile_height
        self.camera = Camera(screen.get_size(), world_width, world_height, zoom=2.0)
        
        # Carregar o tileset
        self.tileset = self._load_tileset() 

        spawn_x, spawn_y = 100, 300  # Ajuste conforme necessário
        self.player = Player(position=(spawn_x, spawn_y), size=(20, 20))
        self.all_sprites.append(self.player)
        self.player.spell_system = self.spell_system 
        
        # Processar a camada de blocos
        self._process_tilemap()
            
        self.dynamic_objects = [self.player]  
        self.collision_manager = CollisionManager(
            self.dynamic_objects, self.platforms, world_width)

    def _load_tileset(self):
        """Carrega a imagem do tileset e divide em tiles individuais."""
        tileset = self.map_data.find("tileset")
        image_path = tileset.find("image").get("source")
        tile_width = int(tileset.get("tilewidth"))
        tile_height = int(tileset.get("tileheight"))
        columns = int(tileset.get("columns"))
        tilecount = int(tileset.get("tilecount"))

        # Carregar a imagem do tileset
        tileset_image = pygame.image.load(os.path.join("src/levels", image_path)).convert_alpha()

        # Dicionário para armazenar os tiles
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

        self.spell_system.spellbook.append(ice_spell)  # Index 0 (key '1')
        self.spell_system.spellbook.append(fan_spell)  # Index 1 (key '2')

    def _process_tilemap(self):
        """Processa a camada de blocos do mapa Tiled."""
        layer = self.map_data.find("layer")
        data = layer.find("data").text.strip()

        # Dividir os dados em linhas e filtrar linhas vazias
        rows = [row for row in data.splitlines() if row.strip()]

        # Converter os dados CSV em uma matriz 2D
        tilemap = []
        for row in rows:
            # Dividir a linha em elementos e tratar strings vazias
            tiles = [int(tile) if tile.strip() else 0 for tile in row.split(",")]
            tilemap.append(tiles)

        # Processar a matriz de tiles
        for row_idx, row in enumerate(tilemap):
            for col_idx, gid in enumerate(row):
                if gid != 0:  # Ignorar tiles vazios
                    x = col_idx * self.tile_width
                    y = row_idx * self.tile_height
                    if gid in self.tileset:
                        # Criar um objeto Terrain para cada tile
                        platform = Terrain(
                            position=(x, y),
                            size=(self.tile_width, self.tile_height),
                            image=self.tileset[gid]
                        )
                        self.all_sprites.append(platform)
                        self.platforms.append(platform)
                        
    def _process_legacy_tiles(self, tiles):
        for item in tiles:
            position = item["position"]
            size = item.get("size", [self.tile_size, self.tile_size])
            if item["type"] == "platform":
                platform = Terrain(position, size)
                self.all_sprites.append(platform)
                self.platforms.append(platform)

    def update(self, delta_time):
        self.player.movement_update(delta_time)
        self.dynamic_objects = [self.player]
        player_pos = [self.player.position.x + self.player.size[0] / 2, 
                      self.player.position.y + self.player.size[1] / 2]
        
        for spell in self.spell_system.spellbook:
            self.dynamic_objects.extend(spell.projectiles)
        self.collision_manager.update(self.dynamic_objects)
        self.camera.update(self.player.rect)    
    
        for spell in self.spell_system.spellbook:
            spell.update(delta_time, player_pos)

    def draw(self):
        self.screen.fill(self.background_color)

        # Desenha todos os sprites com o offset da câmera e zoom
        for sprite in self.all_sprites:
            offset_rect = self.camera.apply(sprite.rect)
            scaled_image = self.camera.apply_surface(sprite.image)
            self.screen.blit(scaled_image, offset_rect)

        # Debug do player com o offset da câmera
        offset_player_rect = self.camera.apply(self.player.rect)
        self.player.draw_colliders_debug(self.screen, Vector2(0, 0))  # Debug já considera o offset aplicado

        # Desenha os projéteis com zoom
        for spell in self.spell_system.spellbook:
            spell.draw(self.screen, self.camera)

        # Debug das plataformas com o offset da câmera
        for platform in self.platforms:
            offset_platform_rect = self.camera.apply(platform.rect)
            platform.draw_colliders_debug(self.screen, self.camera)  # Debug já considera o offset aplicado