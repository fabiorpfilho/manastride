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
from asset_loader import AssetLoader

class Level:
    def __init__(self, screen, level_name):
        self.screen = screen
        self.all_sprites = []
        self.platforms = []
        self.background = [0, 0, 0]
        self.background_layers = []
        self.tile_size = 24 
        
        self.spell_system = SpellSystem()
        self.asset_loader = AssetLoader()

        self.map_data = self.asset_loader.load_map_data(level_name)
        if self.map_data is None:
            return

        
        # Configurações do mapa
        self.tile_width = int(self.map_data.get("tilewidth"))
        self.tile_height = int(self.map_data.get("tileheight"))
        self.map_width = int(self.map_data.get("width"))
        self.map_height = int(self.map_data.get("height"))

        # Configurar a câmera com zoom inicial
        world_width = self.map_width * self.tile_width
        world_height = self.map_height * self.tile_height
        self.camera = Camera(screen.get_size(), world_width,
                             world_height, zoom=3.0)

        
        # Carregar o tileset
        self.tileset = self.asset_loader.load_tileset(self.map_data)
        self.background_layers = self.asset_loader.load_background_layers(
            screen_size=self.screen.get_size(),
            world_size=(world_width, world_height),
            camera_zoom=self.camera.zoom
        )
        
        self.player = Player((100, 300), (20, 30),)
        self.enemy = HammerBot((300, 300), (22, 31))
        
        self.all_sprites += [self.player, self.enemy]
        self.player.spell_system = self.spell_system 
        
        # Processar a camada de blocos
        self._process_tilemap()
            
        self.dynamic_objects = [self.player, self.enemy]
        self.collision_manager = CollisionManager(self.dynamic_objects, self.platforms, world_width)


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

    def draw(self):
        self.screen.fill(self.background)
        # Desenha as camadas de fundo com parallax
        screen_width, screen_height = self.screen.get_size()
        
        i = 0
        for layer in self.background_layers:
            surface = layer['surface']
            offset_x = (layer['offset_x'] %
                        surface.get_width()) - surface.get_width()
            offset_y = (layer['offset_y'] %
                        surface.get_height()) - surface.get_height()
            
            
            # Desenhar cópias suficientes para cobrir a tela
            for x in range(0, screen_width + surface.get_width(), surface.get_width()):
                
                for y in range(0, screen_height + surface.get_height(), surface.get_height()):
                    self.screen.blit(surface, (offset_x + x, offset_y + y))
            i += 1


        # Desenha todos os sprites com o offset da câmera e zoom
        for sprite in self.all_sprites:
            offset_rect = self.camera.apply(sprite.rect, sprite == self.player)
            scaled_image = self.camera.apply_surface(sprite.image)
            self.screen.blit(scaled_image, offset_rect)
        # print(f"Lista de spell no draw: {self.spell_system.spellbook}")
        for spell in self.spell_system.spellbook:
            spell.draw(self.screen, self.camera)

        self.player.draw_colliders_debug(self.screen, self.camera)
        self.enemy.draw_colliders_debug(self.screen, self.camera)
        self.enemy.draw_sensors_debug(self.screen, self.camera)
        # for platform in self.platforms:
        #     platform.draw_colliders_debug(self.screen, self.camera)
                # Debug do player e inimigo

    def update(self, delta_time):
        # Limitar delta_time para evitar picos
        # print(f"Delta time: {delta_time}")  # Debug

        self.player.movement_update(delta_time)
        self.enemy.movement_update(delta_time, self.platforms)
        player_pos = [self.player.position.x + self.player.size[0] / 2, 
                      self.player.position.y + self.player.size[1] / 2]

        for spell in self.spell_system.spellbook:
            self.dynamic_objects.extend(spell.projectiles)
            print(f"Lista de spell no update: {spell.projectiles}")
        print(f"Dynamic objects: {self.dynamic_objects}")
        self.collision_manager.update(self.dynamic_objects)
        self.camera.update(self.player.rect)   
        
        # Atualizar os offsets do fundo com base no movimento da câmera
        for layer in self.background_layers:
            layer['offset_x'] = -self.camera.offset.x * layer['parallax_factor']
            layer['offset_y'] = -self.camera.offset.y * layer['parallax_factor']
    
        for spell in self.spell_system.spellbook:
            spell.update(delta_time, player_pos)
