# level.py
import pygame
import json
from objects.static_objects.terrain import Terrain
from objects.dynamic_objects.player import Player
from collision_manager import CollisionManager

class Level:
    def __init__(self, screen, level_name):
        self.screen = screen
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.background_color = [0, 0, 0]
        self.tile_size = 32 

        try:
            with open(f"src/levels/{level_name}.json", "r") as file:
                level_data = json.load(file)
        except FileNotFoundError:
            print(f"Erro: O arquivo {level_name}.json não foi encontrado!")
            return

        self.background_color = level_data.get("background_color", [0, 0, 0])
        self.tile_size = level_data.get("tile_size", 32)

        spawn_x, spawn_y = level_data.get("player_spawn", [100, 300])
        self.player = Player(position=(spawn_x, spawn_y), size=(50, 50))
        self.all_sprites.add(self.player)

        self.collision_manager = CollisionManager(self.player, self.platforms, self.screen.get_width())

        if "tilemap" in level_data:
            self._process_tilemap(level_data["tilemap"])
        elif "tiles" in level_data:
            self._process_legacy_tiles(level_data["tiles"])

    def _process_tilemap(self, tilemap):
        legend = tilemap["legend"]
        screen_width, screen_height = self.screen.get_size()

        for row_idx, row in enumerate(tilemap["data"]):
            y = row_idx * self.tile_size
            if y > screen_height:  
                continue

            if row_idx == len(tilemap["data"]) - 1:
                platform = Terrain(position=(0, y), size=(min(len(row) * self.tile_size, screen_width), self.tile_size))
                self.all_sprites.add(platform)
                self.platforms.add(platform)
                continue

            col_idx = 0
            while col_idx < len(row):
                char = row[col_idx]

                if char in legend and legend[char]:
                    tile_info = legend[char]
                    x = col_idx * self.tile_size

                    if x > screen_width:
                        col_idx += 1
                        continue

                    if tile_info["type"] == "platform":
                        sequence_length = 1
                        for next_char in row[col_idx+1:]:
                            if next_char == char:
                                sequence_length += 1
                            else:
                                break

                        max_length = (screen_width - x) // self.tile_size
                        sequence_length = min(sequence_length, max_length)

                        if sequence_length > 0:
                            platform = Terrain(position=(x, y), size=(self.tile_size * sequence_length, self.tile_size))
                            self.all_sprites.add(platform)
                            self.platforms.add(platform)

                        col_idx += sequence_length
                        continue
                col_idx += 1

    def _process_legacy_tiles(self, tiles):
        for item in tiles:
            position = item["position"]
            size = item.get("size", [self.tile_size, self.tile_size])
            if item["type"] == "platform":
                platform = Terrain(position, size)
                self.all_sprites.add(platform)
                self.platforms.add(platform)

    def update(self, delta_time):
        self.player.movement_update(delta_time)
        self.collision_manager.update()

    def draw(self): 
        self.screen.fill(self.background_color)
        self.all_sprites.draw(self.screen)
        self.player.draw_colliders_debug(self.screen)  # debug visualização
        for platform in self.platforms:
            platform.draw_colliders_debug(self.screen)
