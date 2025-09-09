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
        self.paused = False  # Estado de pausa
        self.game_started = False  # Estado para controlar se o jogo começou
        self.last_time = time.perf_counter()
        self.menu = Menu(self.screen, self.width, self.height, None)  # Inicializa sem player até o jogo começar
        self.current_level_name = None  # Rastreia o nível atual para carregar música
        self._load_music("menu")  # Carrega a música do menu inicial

    def _load_music(self, level_name):
        """Carrega e toca a música do nível especificado ou do menu."""
        # Caminho principal baseado no nome do level ou menu
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
                return  # Se nem a padrão carregar, apenas sai

        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

    def run(self):
        while self.running:
            current_time = time.perf_counter()
            delta_time = (current_time - self.last_time)
            self.last_time = current_time

            # Coleta eventos uma vez
            events = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_started:
                            print("Tecla ESC pressionada - alternando pausa")
                            self.paused = not self.paused  # Alterna o estado de pausa
                            if not self.paused:
                                print("Jogo retomado")
                                self.menu.selected_menu_item = 0
                                self.menu.current_menu = 'main'  # Garante menu principal ao resumir
                            else:
                                self.menu.current_menu = 'main'  # Garante menu principal ao pausar
                        else:
                            print("Tecla ESC pressionada no menu inicial - saindo do jogo")
                            self.running = False

            if not self.game_started:
                # Mostra o menu inicial
                self.menu.current_menu = 'initial'
                start_game, self.running = self.menu.handle_input(events, False, self.running, mouse_pos)
                if start_game:
                    # Inicia o jogo ao selecionar "Start Game"
                    print("Iniciando o jogo")
                    self.level = Level(self.screen, self.starter_level)
                    self.menu.player = self.level.player  # Atualiza o player no menu
                    self.current_level_name = self.starter_level
                    self._load_music(self.current_level_name)  # Carrega a música do nível inicial
                    self.game_started = True
                self.menu.draw()
            else:
                if self.paused:
                    # Passa os eventos e estados para o menu processar
                    self.paused, self.running = self.menu.handle_input(events, self.paused, self.running, mouse_pos)
                else:
                    new_level_data = self.level.update(delta_time)  # Atualiza o jogo
                    if new_level_data:  # Verifica se há um novo nível a carregar
                        level_name, player_spawn = new_level_data
                        print(f"Carregando novo nível: {level_name}")
                        self.level = Level(self.screen, level_name, player_spawn)
                        self.menu.player = self.level.player  # Atualiza o player no menu
                        self.current_level_name = level_name
                        self._load_music(self.current_level_name)  # Carrega a música do novo nível
                self.level.draw()  # Sempre desenha o nível para manter o estado visual

                if self.paused:
                    self.menu.draw()  # Desenha o menu de pausa

            pygame.display.flip()

        pygame.quit()