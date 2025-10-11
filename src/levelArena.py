from level import Level
import random
from objects.dynamic_objects.hammer_bot import HammerBot
from objects.static_objects.terrain import Terrain
from objects.static_objects.door import Door
from objects.dynamic_objects.player import Player
from objects.dynamic_objects.rune import Rune
from pygame.math import Vector2
import pygame

class LevelArena(Level):
    def __init__(self, screen, level_name, player, player_spawn=None):
        self.arena_activated = False  # Tracks if the arena is activated
        self.wave_spawns = []  # List to store wave_spawn data
        self.arena_timer = 0.0  # Timer to track time since activation
        self.current_wave = 0  # Track the current wave number (0 means no wave spawned yet)
        self.max_waves = 3  # Maximum number of waves
        self.wave_active = False  # Tracks if a wave is currently active
        super().__init__(screen, level_name, player, player_spawn)
        
    def _process_objects(self, player_spawn=None):
        print("Processando objetos no levelArena:")
        """Processa a camada de objetos do mapa, salvando wave_spawns para criação posterior."""
        object_group = self.map_data.find("objectgroup[@name='objects']")
        if object_group is None:
            self.logger.error("Nenhuma camada de objetos 'objects' encontrada no mapa")
            return

        for obj in object_group.findall("object"):
            if obj.get("type") == "wave_spawn":
                # Save wave_spawn data instead of creating enemies immediately
                print("Salvando wave_spawn:", obj)
                self.wave_spawns.append(obj)
                self.logger.info(f"Dados de wave_spawn salvos: {obj}")
                continue  # Skip immediate creation
            obj_data = self.entity_manager.object_factory.create_object(obj, player_spawn)
            if obj_data:
                # Process other objects normally
                if isinstance(obj_data, (Player, HammerBot, Rune)):
                    is_enemy = isinstance(obj_data, HammerBot)
                    self.entity_manager.add_entity(obj_data, is_enemy=is_enemy)
                    self.all_sprites.append(obj_data)
                else:  # Doors, alarms, and other static objects
                    self.static_objects.append(obj_data)
                    self.all_sprites.append(obj_data)

    def update(self, delta_time):
        # Handle arena activation and first wave
        if self.arena_activated and self.current_wave == 0:
            self.arena_timer += delta_time
            if self.arena_timer >= 5.0:  # 5 seconds after activation
                self.logger.info("Timer de 5 segundos atingido, spawnando primeira onda")
                self.spawn_wave()
                self.current_wave = 1
                self.wave_active = True

        # Check if the player collided with the 'arena_start' rectangle
        if self.collision_manager.alarm_triggered and not self.arena_activated:
            self.logger.info("Arena ativada! Desativando porta e criando terreno verde.")
            self._activate_arena()
            self.arena_activated = True
        
        # Check if the current wave is cleared and spawn the next wave if needed
        if self.wave_active and self.current_wave < self.max_waves:
            # Check if all enemies are defeated
            enemies = [enemy for enemy in self.entity_manager.enemies]
            if not enemies:  # No enemies left
                self.logger.info(f"Onda {self.current_wave} concluída!")
                self.wave_active = False
                self.arena_timer = 0.0  # Reset timer for the next wave
                self.current_wave += 1
                if self.current_wave <= self.max_waves:
                    self.logger.info(f"Preparando para spawnar onda {self.current_wave}")
                    self.arena_timer += delta_time  # Start counting for the next wave
                    if self.arena_timer >= 5.0:  # 5-second delay before spawning next wave
                        self.spawn_wave()
                        self.wave_active = True
                        self.logger.info(f"Onda {self.current_wave} spawnada")
                else:
                    self.logger.info("Todas as ondas (3) concluídas!")
        
        return super().update(delta_time)

    def _activate_arena(self):
        """Desativa a porta para level_2 e substitui por um terreno verde."""
        door = None
        # Find and deactivate the door to level_2
        for obj in self.static_objects:
            if isinstance(obj, Door):
                obj.colliders[0].active = False  # Disable collision
                door = obj
                print("Door found:", door)
                if door:
                    self.logger.info("Desativando porta para level_2")
                    # Remove the door from sprites and static objects
                    size = (24, 48)  # Size of the green terrain
                    # Create a green terrain at the door's position
                    green_surface = pygame.Surface(size)
                    green_surface.fill((0, 255, 0))  # Green color
                    terrain = Terrain(
                        position=door.position,
                        size=(size),
                        image=green_surface
                    )
                    
                    # Add the terrain to the lists
                    self.static_objects.append(terrain)
                    self.all_sprites.append(terrain)
                    self.logger.info("Terreno verde adicionado no lugar da porta")

    def spawn_wave(self):
        """Spawna uma onda de inimigos usando os dados de wave_spawns."""
        print("Wave spawns:", self.wave_spawns)
        for spawn_data in self.wave_spawns:
            enemy = self.entity_manager.object_factory.create_wave_enemy(spawn_data)
            if enemy:
                self.entity_manager.add_entity(enemy, is_enemy=True)
                self.all_sprites.append(enemy)
                # Extract position and can_fall for logging
                position = (float(spawn_data.get("x", 0)), float(spawn_data.get("y", 0)))
                properties = spawn_data.find("properties")
                can_fall = False
                if properties is not None:
                    for prop in properties.findall("property"):
                        if prop.get("name") == "can_fall":
                            can_fall = prop.get("value").lower() == "true"
                            break
                self.logger.info(f"Inimigo criado na onda {self.current_wave}: {position}, can_fall: {can_fall}")