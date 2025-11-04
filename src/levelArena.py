from level import Level
import random
from objects.dynamic_objects.hammer_bot import HammerBot
from objects.dynamic_objects.drone import Drone
from objects.static_objects.terrain import Terrain
from objects.static_objects.door import Door
from objects.dynamic_objects.player import Player
from objects.dynamic_objects.rune import Rune
from pygame.math import Vector2
import pygame
from config import SPEED

class LevelArena(Level):
    def __init__(self, screen, level_name, player, player_spawn=None, total_score=0, persistent_dead_ids=[], minor_rune_drop_state=None):
        self.arena_activated = False  # Tracks if the arena is activated
        self.wave_spawns = []  # List to store wave_spawn data
        self.current_wave = 0  # Track the current wave number (0 means no wave spawned yet)
        self.max_waves = 3  # Maximum number of waves
        self.wave_active = False  # Tracks if a wave is currently active
        self.pending_spawns = []  # List to store enemies to be spawned sequentially
        self.spawn_timer = 0.0  # Timer to control spawn intervals
        self.spawn_interval = 1.0  # Interval between enemy spawns (in seconds)
        super().__init__(screen, level_name, player, player_spawn, total_score, persistent_dead_ids, minor_rune_drop_state)
        
    def load_map(self, level_name, player=None, player_spawn=None):
        print(f"Carregando mapa LevelArena: {level_name} com spawn em {player_spawn}")
        self.wave_spawns = []
        self.current_wave = 0
        self.wave_active = False
        self.pending_spawns = []
        self.spawn_timer = 0.0
        self.arena_activated = False
        super().load_map(level_name, player, player_spawn)
        
        # CORREÇÃO: Limpa inimigos fantasmas do entity_manager
        if hasattr(self.entity_manager, 'enemies'):
            self.entity_manager.enemies = []
        
        # Opcional: limpa current_dead_ids se usado para tracking
        self.current_dead_ids = []
        
    def _process_objects(self, player_spawn=None):
        print("Processando objetos no levelArena:")
        """Processa a camada de objetos do mapa, salvando wave_spawns para criação posterior."""
        object_group = self.map_data.find("objectgroup[@name='objects']")
        if object_group is None:
            self.logger.error("Nenhuma camada de objetos 'objects' encontrada no mapa")
            return

        for obj in object_group.findall("object"):
            id_ = obj.get("id")
            if obj.get("type") == "spawn" and obj.get("name") == "hammer_bot" and id_ in self.persistent_dead_ids:
                continue
            if obj.get("type") == "wave_spawn":
                # Save wave_spawn data instead of creating enemies immediately
                print("Salvando wave_spawn:", obj)
                self.wave_spawns.append(obj)
                self.logger.info(f"Dados de wave_spawn salvos: {obj}")
                continue  # Skip immediate creation
            obj_data = self.entity_manager.object_factory.create_object(obj, player_spawn)
            if obj_data:
                # Process other objects normally
                if isinstance(obj_data, (Player, HammerBot, Drone, Rune)):
                    is_enemy = isinstance(obj_data, (HammerBot, Drone))
                    self.entity_manager.add_entity(obj_data, is_enemy=is_enemy)
                    self.all_sprites.append(obj_data)
                else:  # Doors, alarms, and other static objects
                    self.static_objects.append(obj_data)
                    self.all_sprites.append(obj_data)

    def update(self, delta_time):
        # Update static objects (for animations)
        for obj in self.static_objects:
            if hasattr(obj, 'update'):
                obj.update(delta_time)

        # Handle arena activation and first wave
        if self.collision_manager.alarm_triggered and not self.arena_activated:
            self.logger.info("Arena ativada! Desativando porta e criando terreno com campo de força.")
            self._activate_arena()
            self.arena_activated = True
            self.current_wave = 1
            self.wave_active = True
            self.spawn_timer = 0.0
            # Selecionar apenas um spawn para a primeira onda
            # self.pending_spawns = [self.wave_spawns[0]] if self.wave_spawns else []
            self.pending_spawns = random.sample(self.wave_spawns, len(self.wave_spawns))
            self.logger.info(f"Primeira onda iniciada com {len(self.pending_spawns)} inimigo para spawnar")  # Shuff

        # Handle sequential enemy spawning
        if self.wave_active and self.current_wave <= self.max_waves:
            if self.pending_spawns:
                self.spawn_timer += delta_time
                if self.spawn_timer >= self.spawn_interval:
                    self.spawn_next_enemy()
                    self.spawn_timer = 0.0  # Reset timer for next spawn
            else:
                # Check if all enemies in the current wave are defeated
                enemies = [enemy for enemy in self.entity_manager.enemies]
                if not enemies:  # No enemies left
                    self.logger.info(f"Onda {self.current_wave} concluída!")
                    self.wave_active = False
                    self.current_wave += 1
                    if self.current_wave <= self.max_waves:
                        self.logger.info(f"Preparando para spawnar onda {self.current_wave}")
                        self.pending_spawns = random.sample(self.wave_spawns, len(self.wave_spawns))  # Shuffle spawns for next wave
                        self.spawn_timer = 0.0
                        self.wave_active = True
                        self.logger.info(f"Onda {self.current_wave} iniciada com {len(self.pending_spawns)} inimigo para spawnar")
                    else:
                        self.is_completed = True
                        self.logger.info("Todas as ondas (3) concluídas!")
        
        return super().update(delta_time)

    def create_forcefield_texture(self, size):
        """Cria uma textura de campo de força com bordas escuras e energia pulsante."""
        w, h = size
        surface = pygame.Surface((w, h), pygame.SRCALPHA)

        # Cores principais
        color_top = pygame.Color("#4a3052")    # Roxo profundo
        color_mid = pygame.Color("#a32858")    # Magenta vibrante
        color_energy = pygame.Color("#abdd64") # Verde-limão (energia)
        color_dark = pygame.Color("#1f102a")   # Fundo roxo escuro (plano de fundo)

        # Gradiente de fundo (roxo → magenta, sem verde)
        for y in range(h):
            t = y / h
            r = int(color_top.r * (1 - t) + color_mid.r * t)
            g = int(color_top.g * (1 - t) + color_mid.g * t)
            b = int(color_top.b * (1 - t) + color_mid.b * t)
            pygame.draw.line(surface, (r, g, b, 220), (0, y), (w, y))

        # Ondas de energia horizontais
        for i in range(0, h, 6):
            if i % 12 == 0:
                pygame.draw.line(surface, (color_energy.r, color_energy.g, color_energy.b, 120), (0, i), (w, i))
            else:
                pygame.draw.line(surface, (color_dark.r, color_dark.g, color_dark.b, 180), (0, i), (w, i))

        # --- FUNDO ESCURO PARA O BRILHO CIRCULAR ---
        # Cria uma camada central sólida para que os círculos tenham base roxa
        center_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.circle(
            center_surface,
            (color_dark.r, color_dark.g, color_dark.b, 255),
            (w // 2, h // 2),
            min(w, h) // 2 - 2
        )
        surface.blit(center_surface, (0, 0))

        # --- EFEITO DE BRILHO CIRCULAR ---
        for i in range(4):
            radius = min(w, h) // 2 - i * 3
            pygame.draw.circle(
                surface,
                (color_energy.r, color_energy.g, color_energy.b, 50 - i * 10),
                (w // 2, h // 2),
                radius,
                width=2
            )

        # Ruído energético translúcido (faíscas de energia)
        noise = pygame.Surface((w, h), pygame.SRCALPHA)
        for _ in range(w * h // 25):
            x = random.randint(0, w - 1)
            y = random.randint(0, h - 1)
            alpha = random.randint(15, 60)
            noise.set_at((x, y), (color_energy.r, color_energy.g, color_energy.b, alpha))
        surface.blit(noise, (0, 0), special_flags=pygame.BLEND_ADD)

        return surface

    def _activate_arena(self):
        """Desativa a porta para level_2 e substitui por um terreno com textura de campo de força."""
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
                    self.static_objects.remove(door)
                    self.all_sprites.remove(door)
                    size = (24, 48)  # Size of the force field terrain
                    position = door.position
                    # Create a force field texture
                    force_field_surface = self.create_forcefield_texture(size)
                    
                    if door.target_map == "end":
                        door_width = obj.size[0] if hasattr(obj, 'size') else 16
                        position = Vector2(obj.position.x + door_width - size[0], obj.position.y)
                    
                    terrain = Terrain(
                        position,
                        size,
                        image=force_field_surface
                    )
                    terrain.is_growing = True  # Start the growth animation
                    terrain.grow_height = 0  # Start with zero height
                    terrain.base_image = force_field_surface  # Store base image
                    terrain.image = pygame.transform.scale(force_field_surface, (size[0], 0))  # Initial image with zero height
                    terrain.rect = terrain.image.get_rect(bottomleft=(position.x, position.y + size[1]))
                    terrain.colliders[0].size = Vector2(size)  # Initial collider size
                    terrain.colliders[0].rect = pygame.Rect(position.x, position.y + size[1], size[0], 0)
                    
                    # Add the terrain to the lists
                    self.static_objects.append(terrain)
                    self.all_sprites.append(terrain)
                    sound = pygame.mixer.Sound("assets/audio/soundEffects/door/boss-jump.wav")
                    sound.set_volume(0.1)  # 0.0 = mudo, 1.0 = volume total
                    sound.play()
                    self.logger.info("Terreno de campo de força adicionado com animação de crescimento no lugar da porta")

    def spawn_wave(self):
        """Prepara uma onda de inimigos para spawn sequencial."""
        self.logger.info(f"Preparando onda {self.current_wave} para spawn sequencial")
        # Shuffle the wave_spawns list and store it in pending_spawns
        self.pending_spawns = random.sample(self.wave_spawns, len(self.wave_spawns))
        self.spawn_timer = 0.0
        self.logger.info(f"{len(self.pending_spawns)} inimigos preparados para spawn na onda {self.current_wave}")


    def spawn_next_enemy(self):
        """Spawna o próximo inimigo da lista de pending_spawns com modificadores de vida e velocidade."""
        if self.pending_spawns:
            spawn_data = self.pending_spawns.pop(0)  # Remove and get the first spawn
            
            # Definir modificadores com base na onda atual
            base_max_health = 40  # Valor padrão de max_health
            base_speed = SPEED - 120  # Valor padrão de speed (SPEED - 120)
            
            if self.current_wave == 1:
                custom_max_health = base_max_health  # Wave 1: sem modificador
                custom_speed = base_speed
            elif self.current_wave == 2:
                custom_max_health = base_max_health * 1.5  # Wave 2: +50% de vida
                custom_speed = base_speed * 1.4  # Wave 2: +20% de velocidade
            elif self.current_wave == 3:
                custom_max_health = base_max_health * 2.0  # Wave 3: +100% de vida
                custom_speed = base_speed * 1.6  # Wave 3: +40% de velocidade
            
            # Criar inimigo com os valores modificados
            enemy = self.entity_manager.object_factory.create_wave_enemy(
                spawn_data, custom_max_health=custom_max_health, custom_speed=custom_speed
            )
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
                self.logger.info(f"Inimigo criado na onda {self.current_wave}: {position}, can_fall: {can_fall}, "
                               f"max_health: {custom_max_health}, speed: {custom_speed}")
                
    def reset(self):
        player = self.entity_manager.get_player()
        spawn_point = self.current_spawn if self.current_map != "level_3" else Vector2(32.83, 255.67)
        print(f"Resetando LevelArena com spawn em {spawn_point}")

        # CHAMA O load_map DO LEVELARENA (não do pai!)
        self.load_map(self.current_map, player, spawn_point)

        if player:
            player.health = player.max_health
            player.mana = player.max_mana
        self.score = 0
    