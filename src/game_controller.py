import pygame
import time
from level import Level
from menu.menu import Menu
from config import DELTA_TIME

class GameController:
    def __init__(self, width=1600, height=900, title="Teste de Execução"):
        pygame.init()
        pygame.mixer.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.starter_level = "starter"
        pygame.display.set_caption(title)

        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.game_started = False
        self.game_ended = False  # Estado para controlar a tela de fim de jogo
        self.last_time = time.perf_counter()
        self.menu = Menu(self.screen, self.width, self.height, None)
        self.current_level_name = None
        self._load_music("menu")

    def _load_music(self, level_name):
        """Carrega e toca a música do nível especificado ou do menu."""
        music_path = f"assets/audio/soundtrack/{level_name}_theme.ogg"
        fallback_path = "assets/audio/soundtrack/level_1_theme.ogg"

        try:
            pygame.mixer.music.load(music_path)
            print(f"🎵 Música carregada: {music_path}")
        except Exception as e:
            print(f"⚠️ Erro ao carregar '{music_path}': {e}")
            try:
                pygame.mixer.music.load(fallback_path)
                print(f"🎵 Música padrão carregada: {fallback_path}")
            except Exception as fallback_error:
                print(f"❌ Erro ao carregar música padrão '{fallback_path}': {fallback_error}")
                return

        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

    def run(self):
        while self.running:
            current_time = time.perf_counter()
            delta_time = (current_time - self.last_time)
            self.last_time = current_time

            events = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_ended:
                            print("Tecla ESC pressionada na tela de fim - saindo do jogo")
                            self.running = False
                        elif self.game_started:
                            print("Tecla ESC pressionada - alternando pausa")
                            self.paused = not self.paused
                            if not self.paused:
                                print("Jogo retomado")
                                self.menu.selected_menu_item = 0
                                self.menu.current_menu = 'main'
                            else:
                                self.menu.current_menu = 'main'
                        else:
                            print("Tecla ESC pressionada no menu inicial - saindo do jogo")
                            self.running = False

            if self.game_ended:
                self.menu.current_menu = 'end'
                action = self.menu.game_end.update(events)
                if action == "Reiniciar":
                    print("Reiniciando o jogo")
                    self.game_ended = False
                    self.game_started = False
                    self.menu.current_menu = 'initial'
                    self._load_music("menu")
                elif action == "Sair":
                    print("Saindo do jogo")
                    self.running = False
                self.menu.draw()
            elif not self.game_started:
                self.menu.current_menu = 'initial'
                start_game, self.running = self.menu.handle_input(events, False, self.running, mouse_pos)
                if start_game:
                    print("Iniciando o jogo")
                    self.level = Level(self.screen, self.starter_level)
                    self.menu.player = self.level.player
                    self.current_level_name = self.starter_level
                    self._load_music(self.current_level_name)
                    self.game_started = True
                self.menu.draw()
            else:
                if self.paused:
                    self.paused, self.running = self.menu.handle_input(events, self.paused, self.running, mouse_pos)
                else:
                    new_level_data = self.level.update(delta_time)
                    if new_level_data:
                        level_name, player_spawn = new_level_data
                        print(f"Carregando novo nível: {level_name}")
                        self.level = Level(self.screen, level_name, player_spawn)
                        self.menu.player = self.level.player
                        self.current_level_name = level_name
                        self._load_music(self.current_level_name)
                    # Simula fim de jogo para teste (pode ser removido ou ajustado)
                    if self.level.is_completed:  # Supondo que Level tenha um atributo is_completed
                        self.game_ended = True
                self.level.draw()

                if self.paused:
                    self.menu.draw()

            pygame.display.flip()

        pygame.quit()