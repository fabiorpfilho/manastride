import pygame
import json
import xml.etree.ElementTree as ET
import os
from objects.static_objects.terrain import Terrain
from objects.static_objects.door import Door
from objects.static_objects.rune import Rune
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
        self.player = None
        self.enemies = []
        self.dynamic_objects = []
        self.static_objects = []
        self.background = [0, 0, 0]
        self.background_layers = []
        self.tile_size = 24 
        self.score = 0  # Initialize score
        self.font = pygame.font.SysFont('arial', 24)  # Font for score display
        
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
                             world_height, zoom=4.0)

        
        # Carregar o tileset
        self.tileset = self.asset_loader.load_tileset(self.map_data)
        self.background_layers = self.asset_loader.load_background_layers(
            screen_size=self.screen.get_size(),
            world_size=(world_width, world_height),
            camera_zoom=self.camera.zoom
        )
        
        
        # Processar a camada de blocos
        
        self._process_objects()  # Novo método para spawnar objetos do mapa

        self.all_sprites += self.dynamic_objects


        
        self._process_tilemap()
            
        self.collision_manager = CollisionManager(self.dynamic_objects, self.static_objects, world_width)

    def _process_objects(self):
        """Processa a camada de objetos do mapa (player, inimigos, runas, portas etc)."""
        object_group = self.map_data.find("objectgroup[@name='objects']")
        if object_group is None:
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

            if type_ == "spawn":
                if name == "player":
                    self.player = Player(position, size)
                    self.player.spell_system = self.spell_system
                    self.dynamic_objects.append(self.player)
                elif name == "hammer_bot":
                    enemy = HammerBot(position, size)
                    self.enemies.append(enemy)
                    self.dynamic_objects.append(enemy)
            elif type_ == "rune":
                image = self.asset_loader.load_image(f"assets/runes/asset32x32/{name}.png")
                rune = Rune(position, size, name, image, "major", 10)
                self.static_objects.append(rune)  # ou outra lista se quiser isolar portas
                self.all_sprites.append(rune)  # apenas para debug, se desejar
                print(f"Rune '{name}' at {position} - ainda não implementado")
            elif type_ == "door":
                door = Door(position, size, name)
                self.static_objects.append(door)  # ou outra lista se quiser isolar portas
                self.all_sprites.append(door)  # apenas para debug, se desejar

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
            offset_rect = self.camera.apply(sprite.rect)
            scaled_image = self.camera.apply_surface(sprite.image)
            self.screen.blit(scaled_image, offset_rect)
        # print(f"Lista de spell no draw: {self.spell_system.spellbook}")
        for spell in self.spell_system.spellbook:
            spell.draw(self.screen, self.camera)

        self.player.draw_colliders_debug(self.screen, self.camera)
        
        for enemy in self.enemies:
            enemy.draw_colliders_debug(self.screen, self.camera)
            enemy.draw_sensors_debug(self.screen, self.camera)
            
            
        score_text = self.font.render(f'Pontuação: {self.score}', True, (255, 255, 255))
        score_rect = score_text.get_rect(topright=(screen_width - 10, 10))
        self.screen.blit(score_text, score_rect)

        # for platform in self.static_objects:
        #     platform.draw_colliders_debug(self.screen, self.camera)
                # Debug do player e inimigo

    def update(self, delta_time):
        if self.player.health <= 0:
            self.reset()
        # Limitar delta_time para evitar picos
        # print(f"Delta time: {delta_time}")  # Debug

        self.player.update(delta_time)
        # Atualizar inimigos
        for enemy in self.enemies[:]:  # cópia da lista para remover com segurança
            if enemy.marked_for_removal:
                self.score += 100  
                self.dynamic_objects.remove(enemy)
                self.all_sprites.remove(enemy)
                self.enemies.remove(enemy)
            else:
                enemy.update(delta_time, self.static_objects)

                
        player_pos = [self.player.position.x + self.player.size[0] / 2, 
                      self.player.position.y + self.player.size[1] / 2]

        for spell in self.spell_system.spellbook:
            spell.update(delta_time, player_pos)
            for proj in spell.projectiles:
                proj.sync_position(proj.direction)
                if proj not in self.dynamic_objects:
                    self.dynamic_objects.append(proj)

        #     print(f"Lista de spell no update: {spell.projectiles}")
        # print(f"Dynamic objects: {self.dynamic_objects}")
        self.collision_manager.update(self.dynamic_objects)
        
        if self.collision_manager.door_triggered:
            new_map = self.collision_manager.door_triggered
            self._load_new_map(new_map)
            return  # parar o update aqui pois o mapa foi trocado
        self.camera.update(self.player)   
        
        # Atualizar os offsets do fundo com base no movimento da câmera
        for layer in self.background_layers:
            layer['offset_x'] = -self.camera.offset.x * layer['parallax_factor']
            layer['offset_y'] = -self.camera.offset.y * layer['parallax_factor']


    def reset(self):
        # Resetar o jogador
        self.player = Player((100, 300), (20, 30))
        self.player.spell_system = self.spell_system

        # Resetar o inimigo
        self.enemies = [HammerBot((300, 300), (22, 31))]
        self.dynamic_objects = [self.player] + self.enemies
        self.all_sprites = self.static_objects + self.dynamic_objects

        self.score = 0
        # Limpar feitiços ativos
        self.spell_system.spellbook.clear()

        # Limpar objetos dinâmicos

        # Resetar lista de sprites

        # Resetar câmera
        self.camera.target = self.player
        self.camera.offset = Vector2(0, 0)

        # Resetar colisores
        self.collision_manager = CollisionManager(self.dynamic_objects, self.static_objects, self.map_width * self.tile_width)

    def _load_new_map(self, level_name):
        print(f"Trocando para o mapa: {level_name}")

        # Salvar dados importantes
        saved_score = self.score
        saved_spellbook = self.spell_system.spellbook.copy()
        # Salvar estado do player
        saved_health = self.player.health

        # Recarrega tudo (vai sobrescrever self.player)
        self.__init__(self.screen, level_name)

        # Restaurar dados
        self.score = saved_score
        self.spell_system.spellbook = saved_spellbook

        # Restaurar estado do novo player
        if self.player:
            self.player.health = saved_health
            self.player.sync_position()
