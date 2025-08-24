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
        
        self.spell_system = SpellSystem()
        self.asset_loader = AssetLoader()

        self.status_bar = StatusBar(self.screen, self.asset_loader)
        self.score_ui = Score(self.screen, self.asset_loader)
        self.hotbar = HotBar(self.screen, self.asset_loader)

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
        # self._load_music(level_name)
            
        self.collision_manager = CollisionManager(self.dynamic_objects, self.static_objects, world_width)

    def _load_music(self, level_name):
        # Caminho principal baseado no nome do level
        music_path = f"assets/audio/soundtrack/{level_name}_theme.ogg"
        fallback_path = "assets/audio/soundtrack/level_1_theme.ogg"

        try:
            pygame.mixer.music.load(music_path)
            # print(f"🎵 Música carregada: {music_path}")
        except Exception as e:
            # print(f"⚠️ Erro ao carregar '{music_path}': {e}")
            try:
                pygame.mixer.music.load(fallback_path)
                print(f"🎵 Música padrão carregada: {fallback_path}")
            except Exception as fallback_error:
                print(f"❌ Erro ao carregar música padrão '{fallback_path}': {fallback_error}")
                return  # Se nem a padrão carregar, apenas sai

        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

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

            # Inicializa as variáveis de spawn do jogador como None
            player_spawn_x = None
            player_spawn_y = None

            # Busca as propriedades dentro do elemento <properties>
            properties = obj.find("properties")
            if properties is not None:
                for prop in properties.findall("property"):
                    if prop.get("name") == "player_spawn_x":
                        # Substitui vírgula por ponto e converte para float
                        player_spawn_x = float(prop.get("value"))
                    elif prop.get("name") == "player_spawn_y":
                        # Substitui vírgula por ponto e converte para float
                        player_spawn_y = float(prop.get("value"))

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
                self.dynamic_objects.append(rune)
                print(f"Runa '{name}' adicionada na posição {position}")
            elif type_ == "door":
                # Verifica se as propriedades de spawn foram encontradas
                if player_spawn_x is not None and player_spawn_y is not None:
                    player_spawn = (player_spawn_x, player_spawn_y)
                    print(f"Player spawn: {player_spawn}")
                    door = Door(position, size, name, player_spawn)
                    self.static_objects.append(door)
                    self.all_sprites.append(door)  # apenas para debug, se desejar
                else:
                    print(f"Erro: Propriedades player_spawn_x e player_spawn_y não encontradas para a porta {name}")
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
        for layer in self.background_layers:
            surface = layer['surface']
            offset_x = (layer['offset_x'] % surface.get_width()) - surface.get_width()
            offset_y = (layer['offset_y'] % surface.get_height()) - surface.get_height()
            # Desenhar cópias suficientes para cobrir a tela
            for x in range(0, screen_width + surface.get_width(), surface.get_width()):
                for y in range(0, screen_height + surface.get_height(), surface.get_height()):
                    self.screen.blit(surface, (offset_x + x, offset_y + y))

        # Desenha todos os sprites com o offset da câmera e zoom
        for sprite in self.all_sprites:
            # if isinstance(sprite, Rune):  # Verifica se é um sprite válido
            #     print(f"Desenhando sprite: {sprite.tag} na posição {sprite.position}")
            offset_rect = self.camera.apply(sprite.rect)
            scaled_image = self.camera.apply_surface(sprite.image)
            self.screen.blit(scaled_image, offset_rect)

        # Desenha os feitiços
        for spell in self.player.spell_system.spellbook:
            spell.draw(self.screen, self.camera)
            
        if self.player:
            self.status_bar.draw(self.player)
            self.hotbar.draw()

        self.score_ui.draw(self.score)

        # Desenha colisores de debug
        for obj in self.dynamic_objects:  # Cópia para remoção segura
              obj.draw_colliders_debug(self.screen, self.camera)


    def update(self, delta_time):
        if self.player.health <= 0:
            self.reset()

        # Atualizar objetos dinâmicos
        for obj in self.dynamic_objects[:]:  # Cópia para remoção segura
            if isinstance(obj, HammerBot):
                if obj.marked_for_removal:
                    self.score += 100
                    self.dynamic_objects.remove(obj)
                    self.all_sprites.remove(obj)
                    self.enemies.remove(obj)
                else:
                    obj.update(delta_time, self.static_objects)
            elif isinstance(obj, (Player)):
                obj.update(delta_time)
            elif isinstance(obj, Rune, ):
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
        
        projectiles = self.player.spell_system.spellbook[0]
        if projectiles:  
            projectiles.update(delta_time, player_pos)
            for proj in projectiles.projectiles:
                proj.sync_position()
                if proj not in self.dynamic_objects:
                    self.dynamic_objects.append(proj)
                    self.all_sprites.append(proj)
                    
        shields = self.player.spell_system.spellbook[2]
        if shields:  
            shields.update(delta_time)
            for shield in shields.shields:
                shield.sync_position()
                if shield not in self.dynamic_objects:
                    self.dynamic_objects.append(shield)
                    self.all_sprites.append(shield)


        self.collision_manager.update(self.dynamic_objects)
        
        if self.collision_manager.door_triggered:

            print(f"Door triggered: {self.collision_manager.door_triggered}")
            door_triggered = self.collision_manager.door_triggered
            target_map = door_triggered.target_map
            player_spawn = door_triggered.player_spawn
            # self._load_new_map(target_map, player_spawn)
            return
        self.camera.update(self.player)   

        
        
        # Atualizar os offsets do fundo com base no movimento da câmera
        for layer in self.background_layers:
            layer['offset_x'] = -self.camera.offset.x * layer['parallax_factor']
            layer['offset_y'] = -self.camera.offset.y * layer['parallax_factor']

    def reset(self):
        # Resetar o jogador
        # self.player = Player((100, 300), (20, 30))
        self.player.health = 100
        self.player.mana = 100
        self.player.position = (100, 300)

        # Resetar o inimigo
        self.enemies = [HammerBot((300, 300), (22, 31))]
        self.dynamic_objects = [self.player] + self.enemies
        self.all_sprites = self.static_objects + self.dynamic_objects

        self.score = 0

        # Resetar câmera
        self.camera.target = self.player
        self.camera.offset = Vector2(0, 0)

        # Resetar colisores
        self.collision_manager = CollisionManager(self.dynamic_objects, self.static_objects, self.map_width * self.tile_width)

    def _load_new_map(self, level_name, player_spawn):
        print(f"Trocando para o mapa: {level_name}")

        # Salvar dados importantes
        saved_score = self.score
        saved_spellbook = self.player.spell_system.spellbook.copy()
        # Salvar estado do player
        saved_health = self.player.health
        saved_mana = self.player.mana

        # Recarrega tudo (vai sobrescrever self.player)
        self.__init__(self.screen, level_name)

        # Restaurar dados
        self.score = saved_score

        # Restaurar estado do novo player
        if self.player:
            self.player.health = saved_health
            self.player.mana = saved_mana
            self.player.spell_system.spellbook = saved_spellbook
            self.player.sync_position()
