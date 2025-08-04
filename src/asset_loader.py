# asset_loader.py
import os
import pygame
import xml.etree.ElementTree as ET


class AssetLoader:
    def __init__(self, base_path="assets/maps"):
        self.base_path = base_path

    def load_map_data(self, level_name):
        """Carrega e retorna o XML do mapa."""
        try:
            tree = ET.parse(os.path.join(self.base_path, f"{level_name}.xml"))
            return tree.getroot()
        except FileNotFoundError:
            print(f"Erro: O arquivo {level_name}.xml não foi encontrado!")
            return None

    def load_tileset(self, map_data):
        """Carrega a imagem do tileset e divide em tiles individuais."""
        tileset = map_data.find("tileset")
        image_path = tileset.find("image").get("source")
        tile_width = int(tileset.get("tilewidth"))
        tile_height = int(tileset.get("tileheight"))
        columns = int(tileset.get("columns"))
        tilecount = int(tileset.get("tilecount"))

        tileset_image = pygame.image.load(os.path.join(
            self.base_path, image_path)).convert_alpha()

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

    def load_background_layers(self, screen_size, world_size, camera_zoom):
        """Carrega e retorna as superfícies de fundo com parallax."""
        parallax_factors = [
            (0.2, f"{self.base_path}/oak_woods_v1.0/background/background_layer_1.png"),
            (0.5, f"{self.base_path}/oak_woods_v1.0/background/background_layer_2.png"),
            (0.8, f"{self.base_path}/oak_woods_v1.0/background/background_layer_3.png")
        ]

        screen_width, screen_height = screen_size
        world_width, world_height = world_size

        background_layers = []

        for factor, path in parallax_factors:
            try:
                image = pygame.image.load(path).convert_alpha()
                scaled_width = int(
                    world_width / camera_zoom / factor) + screen_width
                scaled_height = int(
                    world_height / camera_zoom / factor) + screen_height
                scaled_image = pygame.transform.scale(
                    image, (scaled_width, scaled_height))
                layer_surface = pygame.Surface(
                    (scaled_width, scaled_height), pygame.SRCALPHA)
                layer_surface.blit(scaled_image, (0, 0))

                background_layers.append({
                    'surface': layer_surface,
                    'parallax_factor': factor,
                    'offset_x': 0,
                    'offset_y': 0
                })
            except FileNotFoundError:
                print(f"Erro: Não foi possível carregar {path}")
                continue

        return background_layers

    def load_image(self, path):
        """Carrega uma imagem de um caminho específico e retorna a superfície do Pygame."""
        full_path = os.path.join(path)
        try:
            return pygame.image.load(full_path).convert_alpha()
        except FileNotFoundError:
            print(f"Erro: Imagem não encontrada em {full_path}")
            return pygame.Surface((0, 0), pygame.SRCALPHA)  # Retorna uma superfície vazia
