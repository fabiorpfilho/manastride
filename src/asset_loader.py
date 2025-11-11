# asset_loader.py
import os
import pygame
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Optional


class AssetLoader:
    # Caminho base padrão – pode ser sobrescrito por parâmetro
    _DEFAULT_BASE_PATH = "assets/maps"

    # ------------------------------------------------------------------ #
    #  MÉTODOS ESTÁTICOS
    # ------------------------------------------------------------------ #
    @staticmethod
    def load_map_data(level_name: str, base_path: str = _DEFAULT_BASE_PATH) -> Optional[ET.Element]:
        """Carrega e retorna o XML do mapa."""
        file_path = os.path.join(base_path, f"{level_name}.xml")
        try:
            tree = ET.parse(file_path)
            return tree.getroot()
        except FileNotFoundError:
            print(f"[AssetLoader] Erro: Arquivo não encontrado → {file_path}")
            return None
        except ET.ParseError as e:
            print(f"[AssetLoader] Erro ao parsear XML: {file_path} → {e}")
            return None

    @staticmethod
    def load_tileset(
        map_data: ET.Element,
        base_path: str = _DEFAULT_BASE_PATH
    ) -> Dict[int, pygame.Surface]:
        """Carrega o tileset e retorna dicionário {gid: surface}."""
        tileset = map_data.find("tileset")
        if not tileset:
            print("[AssetLoader] Tileset não encontrado no mapa.")
            return {}

        image_path = tileset.find("image").get("source")
        tile_width = int(tileset.get("tilewidth"))
        tile_height = int(tileset.get("tileheight"))
        columns = int(tileset.get("columns"))
        tilecount = int(tileset.get("tilecount"))
        firstgid = int(tileset.get("firstgid"))

        full_image_path = os.path.join(base_path, image_path)
        try:
            tileset_image = pygame.image.load(full_image_path).convert_alpha()
        except FileNotFoundError:
            print(f"[AssetLoader] Tileset não encontrado: {full_image_path}")
            return {}

        tiles = {}
        for gid_offset in range(tilecount):
            gid = firstgid + gid_offset
            col = gid_offset % columns
            row = gid_offset // columns
            x = col * tile_width
            y = row * tile_height
            rect = pygame.Rect(x, y, tile_width, tile_height)
            tile_surface = tileset_image.subsurface(rect)
            tiles[gid] = tile_surface

        return tiles

    @staticmethod
    def load_background_layers(
        screen_size: Tuple[int, int],
        world_size: Tuple[int, int],
        camera_zoom: float,
        base_path: str = _DEFAULT_BASE_PATH
    ) -> List[Dict]:
        """Carrega camadas de parallax."""
        parallax_configs = [
            (0.2, f"{base_path}/oak_woods_v1.0/background/background_layer_1.png"),
            (0.5, f"{base_path}/oak_woods_v1.0/background/background_layer_2.png"),
            (0.8, f"{base_path}/oak_woods_v1.0/background/background_layer_3.png"),
        ]

        screen_w, screen_h = screen_size
        world_w, world_h = world_size
        layers = []

        for factor, path in parallax_configs:
            try:
                image = pygame.image.load(path).convert_alpha()
                # Ajusta ao mundo + tela para evitar bordas
                scaled_w = int(world_w / camera_zoom / factor) + screen_w
                scaled_h = int(world_h / camera_zoom / factor) + screen_h
                scaled = pygame.transform.scale(image, (scaled_w, scaled_h))

                layer = {
                    'surface': scaled,
                    'parallax_factor': factor,
                    'offset_x': 0,
                    'offset_y': 0
                }
                layers.append(layer)
            except FileNotFoundError:
                print(f"[AssetLoader] Background não encontrado: {path}")

        return layers

    @staticmethod
    def load_image(path: str) -> pygame.Surface:
        """Carrega uma imagem genérica."""
        full_path = os.path.join(path)
        try:
            return pygame.image.load(full_path).convert_alpha()
        except FileNotFoundError:
            print(f"[AssetLoader] Imagem não encontrada: {full_path}")
            return pygame.Surface((32, 32), pygame.SRCALPHA)  # fallback