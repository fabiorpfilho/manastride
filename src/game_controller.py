import pygame
import time
import logging
from level import Level
from menu.menu import Menu
from config import DELTA_TIME
from music_manager import MusicManager

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
        self.music_manager.load_music("menu")

    def run(self):
        while self.running:
            current_time = time.perf_counter()
            delta_time = (current_time - self.last_time)
            self.last_time = current_time

            events = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()

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

            if self.game_ended:
                self.menu.current_menu = 'end'
                action = self.menu.game_end.update(events)
                if action == "Reiniciar":
                    self.logger.info("Reiniciando o jogo")
                    self.game_ended = False
                    self.game_started = False
                    self.menu.current_menu = 'initial'
                    self.music_manager.load_music("menu")
                elif action == "Sair":
                    self.logger.info("Saindo do jogo")
                    self.running = False
                self.menu.draw()
            elif not self.game_started:
                self.menu.current_menu = 'initial'
                start_game, self.running = self.menu.handle_input(events, False, self.running, mouse_pos)
                if start_game:
                    self.logger.info("Iniciando o jogo")
                    self.level = Level(self.screen, self.starter_level)
                    player = self.level.entity_manager.get_player()
                    if player is None:
                        self.logger.error("Nenhum jogador encontrado após carregar o nível inicial")
                        self.running = False
                    else:
                        self.menu.player = player
                        self.current_level_name = self.starter_level
                        self.music_manager.load_music(self.current_level_name)
                        self.game_started = True
                self.menu.draw()
            else:
                if self.paused:
                    self.paused, self.running = self.menu.handle_input(events, self.paused, self.running, mouse_pos)
                else:
                    new_level_data = self.level.update(delta_time)
                    if new_level_data:
                        level_name, player_spawn = new_level_data
                        self.logger.info(f"Carregando novo nível: {level_name}")
                        self.level = Level(self.screen, level_name, player_spawn)
                        player = self.level.entity_manager.get_player()
                        if player is None:
                            self.logger.error(f"Nenhum jogador encontrado ao carregar o nível {level_name}")
                            self.running = False
                        else:
                            self.menu.player = player
                            self.current_level_name = level_name
                            self.music_manager.load_music(self.current_level_name)
                    if self.level.is_completed:
                        self.logger.info(f"Nível {self.current_level_name} concluído - exibindo tela de fim")
                        self.game_ended = True
                self.level.draw()

                if self.paused:
                    self.menu.draw()

            pygame.display.flip()

        pygame.quit()