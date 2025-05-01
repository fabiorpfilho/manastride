# level.py
import pygame
import json
from objects.static_objects.terrain import Terrain
from objects.dynamic_objects.player import Player
from collision_manager import CollisionManager
from camera import Camera
from spells.spell_system import SpellSystem
from spells.rune import Rune
from spells.rune_type import RuneType
from spells.spell import Spell
from spells.spell_effect_type import SpellEffectType

class Level:
    def __init__(self, screen, level_name):
        self.screen = screen
        self.all_sprites = []
        self.platforms = []
        self.background_color = [0, 0, 0]
        self.tile_size = 32 
        
        self.spell_system = SpellSystem()
        self._setup_spells()

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
        self.all_sprites.append(self.player)
        self.player.spell_system = self.spell_system 


        if "tilemap" in level_data:
            tilemap = level_data["tilemap"]

            world_width = max(len(row)
                              for row in tilemap["data"]) * self.tile_size
            world_height = len(tilemap["data"]) * self.tile_size
            self.camera = Camera(screen.get_size(), world_width, world_height)
     
            self._process_tilemap(tilemap)
        elif "tiles" in level_data:
            self._process_legacy_tiles(level_data["tiles"])
            
        self.dynamic_objects = [self.player]  
        self.collision_manager = CollisionManager(
            self.dynamic_objects, self.platforms, world_width)
        
    def _setup_spells(self):
        fireball_rune = Rune(name="Fireball", rune_type=RuneType.COMMAND, value=None, cost=2)
        dano_rune1 = Rune(name="Dano1", rune_type=RuneType.MODIFIER, value={"damage": 5}, cost=1)
        dano_rune2 = Rune(name="Dano2", rune_type=RuneType.MODIFIER, value={
                         "damage":15}, cost=1)
        loop_rune = Rune(name="Loop", rune_type=RuneType.LOOP, value={"iterations": 3}, cost=3)

        self.spell_system.add_rune(fireball_rune)
        self.spell_system.add_rune(dano_rune1)
        self.spell_system.add_rune(dano_rune2)
        self.spell_system.add_rune(loop_rune)

        fireball_spell = Spell(
            name="Bola de fogo",
            runes=[fireball_rune, dano_rune2],
            effect_type=SpellEffectType.PROJECTILE
        )

        saraivada_spell = Spell(
            name="Saraivada de Fogo",
            runes=[loop_rune, fireball_rune, dano_rune1],
            effect_type=SpellEffectType.PROJECTILE
        )

        self.spell_system.spellbook.append(fireball_spell)  # Index 0 (key '1')
        self.spell_system.spellbook.append(
            saraivada_spell)  # Index 1 (key '2')

    def _process_tilemap(self, tilemap):
        legend = tilemap["legend"]
        screen_width, screen_height = self.screen.get_size()

        for row_idx, row in enumerate(tilemap["data"]):
            y = row_idx * self.tile_size

            if row_idx == len(tilemap["data"]) - 1:
                platform = Terrain(position=(0, y), size=(min(len(row) * self.tile_size, self.tile_size)))
                self.all_sprites.append(platform)
                self.platforms.append(platform)
                continue

            col_idx = 0
            while col_idx < len(row):
                char = row[col_idx]

                if char in legend and legend[char]:
                    tile_info = legend[char]
                    x = col_idx * self.tile_size

                    if tile_info["type"] == "platform":
                        sequence_length = 1
                        for next_char in row[col_idx+1:]:
                            if next_char == char:
                                sequence_length += 1
                            else:
                                break

                        platform = Terrain(position=(x, y), size=(self.tile_size * sequence_length, self.tile_size))
                        self.all_sprites.append(platform)
                        self.platforms.append(platform)

                        col_idx += sequence_length
                        continue
                col_idx += 1

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
        player_pos = [self.player.position.x + self.player.size[0] /
                      2, self.player.position.y + self.player.size[1] / 2]

        for spell in self.spell_system.spellbook:
            self.dynamic_objects.extend(spell.projectiles)
        self.collision_manager.update(self.dynamic_objects)
        self.camera.update(self.player.rect)    
    
        for spell in self.spell_system.spellbook:
            spell.update_projectiles(delta_time, player_pos)


    def draw(self):
        self.screen.fill(self.background_color)

        # Desenha todos os sprites com o offset da câmera
        for sprite in self.all_sprites:
            offset_rect = self.camera.apply(sprite.rect)
            self.screen.blit(sprite.image, offset_rect)

        # Debug do player com o offset da câmera
        self.player.draw_colliders_debug(self.screen, self.camera.offset)
        
        for spell in self.spell_system.spellbook:
            spell.draw_projectiles(self.screen, self.camera)

        # Debug das plataformas com o offset da câmera
        for platform in self.platforms:
            platform.draw_colliders_debug(self.screen, self.camera.offset)
