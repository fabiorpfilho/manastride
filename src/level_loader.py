import pygame
import json
from objects.static_objects.terrain import Terrain

class LevelLoader:
    def __init__(self, screen, player, level_name):
        self.screen = screen
        self.player = player
        self.platforms = pygame.sprite.Group()
        # self.enemies = pygame.sprite.Group()
        # self.objects = pygame.sprite.Group()
        
        try:
            with open(f"levels/{level_name}.json", "r") as file:
                level_data = json.load(file)
        except FileNotFoundError:
            print(f"Erro: O arquivo levels/{level_name}.json não foi encontrado!")
            return

        self.background_color = level_data.get("background_color", [0, 0, 0])
        self.tile_size = level_data.get("tile_size", 32)

        player.rect.x, player.rect.y = level_data.get("player_spawn", [50, 400])

        for item in level_data["tiles"]:
            x, y = item["position"]

            if item["type"] == "platform":
                platform = Terrain((x, y), (self.tile_size, self.tile_size))
                self.platforms.add(platform)

            # elif item["type"] == "enemy":
            #     enemy = Character((x, y), (self.tile_size, self.tile_size), sprite=(255, 0, 0))
            #     self.enemies.add(enemy)

            # elif item["type"] == "object":
            #     obj = pygame.sprite.Sprite() 
            #     obj.image = pygame.Surface((self.tile_size, self.tile_size))
            #     obj.image.fill((50, 200, 50))
            #     obj.rect = obj.image.get_rect(topleft=(x, y))
            #     self.objects.add(obj)

    def update(self):
        # self.enemies.update()
        # self.objects.update()
        self.player.movement_update(self.platforms, self.screen.get_width()) 

    def draw(self):
        """Desenha os elementos da fase"""
        self.screen.fill(self.background_color)
        
        self.platforms.draw(self.screen)
        # self.enemies.draw(self.screen)
        # self.objects.draw(self.screen)
        
        self.player.draw(self.screen)
