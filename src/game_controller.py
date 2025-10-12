import pygame
import time
import logging
import json
from datetime import datetime
from level import Level
from levelArena import LevelArena
from menu.menu import Menu
from config import DELTA_TIME
from music_manager import MusicManager
from collections import defaultdict

class GameController:
    def __init__(self, width=1600, height=900, title="Teste de Execução"):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.starter_level = "starter"
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.game_started = False
        self.game_ended = False
        self.last_time = time.perf_counter()
        self.music_manager = MusicManager()
        self.menu = Menu(self.screen, self.width, self.height, None)
        self.current_level_name = None
        self.player_name = None
        self.player_score = 0
        self.total_score = 0
        self.player = None  # Store the player instance
        self.arena_music_loaded = False  # Flag para rastrear se a música da arena já foi carregada
        self.dead_enemies_by_level = defaultdict(list)
        self.music_manager.load_music("backgroundmusic.ogg")

        self.minor_rune_drop_state = {
            "first_drop": True,  # Primeiro inimigo sempre dropa
            "streak": 0,         # Contador de inimigos derrotados sem drop
            "base_chance": 0.2,  # Chance base após o primeiro (ajuste se quiser)
            "increment": 0.1     # Aumento por streak (ajuste se quiser)
        }
    def save_score(self):
        """Salva o nome e a pontuação do jogador em scores.json."""
        score_entry = {
            "name": self.player_name,
            "score": self.player_score,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        try:
            try:
                with open("scores.json", "r") as file:
                    scores = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                scores = []
            
            scores.append(score_entry)
            with open("scores.json", "w") as file:
                json.dump(scores, file, indent=4)
            self.logger.info(f"Pontuação salva: {score_entry}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar pontuação: {e}")

    def handle_events(self, events):
        """Handle input events like quitting and pausing."""
        for event in events:
            if event.type == pygame.QUIT:
                self.logger.info("Evento QUIT recebido - saindo do jogo")
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_ended:
                        self.logger.info("Tecla ESC pressionada na tela de fim - saindo do jogo")
                        self.running = False
                    elif self.game_started:
                        self.logger.info("Tecla ESC pressionada - alternando pausa")
                        self.paused = not self.paused
                        if not self.paused:
                            self.logger.info("Jogo retomado")
                            self.menu.selected_menu_item = 0
                            self.menu.current_menu = 'main'
                        else:
                            self.menu.current_menu = 'main'
                    else:
                        self.logger.info("Tecla ESC pressionada no menu inicial - saindo do jogo")
                        self.running = False

    def process_main_menu(self, events, mouse_pos):
        """Handle the main menu state before the game starts."""
        self.menu.current_menu = 'initial'
        start_game, self.running = self.menu.handle_input(events, False, self.running, mouse_pos)
        if start_game:
            self.logger.info("Iniciando o jogo")
            self.load_level(self.starter_level)
            self.player = self.level.entity_manager.get_player()
            if self.player is None:
                self.logger.error("Nenhum jogador encontrado após carregar o nível inicial")
                self.running = False
            else:
                self.menu.player = self.player
                self.current_level_name = self.starter_level
                self.music_manager.load_music(self.current_level_name)
                self.game_started = True
        self.menu.draw()

    def process_game_end(self, events):
        """Handle the game end state (end screen)."""
        self.menu.current_menu = 'end'
        action, player_name = self.menu.game_end.update(events)
        if action:
            self.player_name = player_name if player_name else "Anônimo"
            self.player_score = self.total_score + (self.level.score if hasattr(self.level, 'score') else 0)
            self.logger.info(f"Dados do jogador capturados - Nome: {self.player_name}, Pontuação: {self.player_score}")
            self.save_score()
            if action == "Reiniciar":
                self.logger.info("Reiniciando o jogo")
                self.game_ended = False
                self.game_started = False
                self.player = None  # Reset player for new game
                self.total_score = 0
                self.dead_enemies_by_level = defaultdict(list)
                self.arena_music_loaded = False  # Reset flag da música da arena
                self.menu.current_menu = 'initial'
                self.music_manager.load_music("backgroundmusic.ogg")
            elif action == "Sair":
                self.logger.info("Saindo do jogo")
                self.running = False
        self.menu.draw()

    def process_gameplay(self, events, delta_time, mouse_pos):
        """Handle gameplay state, including paused and unpaused modes."""
        if self.paused:
            self.paused, self.running = self.menu.handle_input(events, self.paused, self.running, mouse_pos)
            if self.paused:
                self.menu.draw()
        else:
            new_level_data = self.level.update(delta_time)
            if new_level_data:
                level_name, player_spawn, player, minor_rune_drop_state = new_level_data
                print("Minor rune drop state on level change:", minor_rune_drop_state)
                self.total_score += self.level.score
                self.dead_enemies_by_level[self.current_level_name].extend(self.level.current_dead_ids)
                self.logger.info(f"Carregando novo nível: {level_name}")
                self.load_level(level_name, player, player_spawn, self.total_score, minor_rune_drop_state)
                self.player = self.level.entity_manager.get_player()
                if self.player is None:
                    self.logger.error(f"Nenhum jogador encontrado ao carregar o nível {level_name}")
                    self.running = False
                else:
                    self.menu.player = self.player
                    self.current_level_name = level_name
                    self.music_manager.load_music(self.current_level_name)
                    self.arena_music_loaded = False  # Reset flag ao carregar novo nível
            # Verificar ativação da arena e carregar música específica
            if isinstance(self.level, LevelArena) and self.level.arena_activated and not self.arena_music_loaded:
                self.logger.info("Arena ativada - carregando música da arena")
                self.music_manager.load_music("arena.mp3")  # Substitua "arena" pelo nome da música desejada
                self.arena_music_loaded = True
            if self.level.is_completed:
                self.logger.info(f"Nível {self.current_level_name} concluído - exibindo tela de fim")
                self.game_ended = True
            self.level.draw()

    def load_level(self, level_name, player=None, player_spawn=None, total_score=0, minor_rune_drop_state=None):  
        """Load a new level with the specified name and optional player spawn point."""
        persistent_dead_ids = self.dead_enemies_by_level.get(level_name, [])
        if level_name == "level_3":
            self.level = LevelArena(self.screen, level_name, player, player_spawn, total_score, persistent_dead_ids, minor_rune_drop_state)
        else:
            self.level = Level(self.screen, level_name, player, player_spawn, total_score, persistent_dead_ids, minor_rune_drop_state)

    def run(self):
        """Main game loop."""
        while self.running:
            current_time = time.perf_counter()
            delta_time = (current_time - self.last_time)
            self.last_time = current_time

            events = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()

            self.handle_events(events)

            if self.game_ended:
                self.process_game_end(events)
            elif not self.game_started:
                self.process_main_menu(events, mouse_pos)
            else:
                self.process_gameplay(events, delta_time, mouse_pos)

            pygame.display.flip()

        pygame.quit()