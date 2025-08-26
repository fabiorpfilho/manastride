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
        pygame.display.set_caption(title)

        self.level = Level(self.screen, "level_1")
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False  # Estado de pausa
        self.last_time = time.perf_counter()
        self.menu = Menu(self.screen, self.width, self.height, self.level.player)

    def run(self):
        while self.running:
            current_time = time.perf_counter()
            delta_time = (current_time - self.last_time)
            self.last_time = current_time

            # Coleta eventos uma vez para evitar múltiplas chamadas
            events = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused  # Alterna o estado de pausa
                        if not self.paused:
                            self.menu.selected_menu_item = 0  # Reseta a seleção ao sair do menu

            if self.paused:
                # Passa os eventos e estados para o menu processar
                self.paused, self.running = self.menu.handle_input(events, self.paused, self.running)

            if not self.paused:
                self.level.update(delta_time)  # Atualiza o jogo apenas se não estiver pausado
            self.level.draw()  # Sempre desenha o nível para manter o estado visual

            if self.paused:
                self.menu.draw()  # Desenha o menu de pausa

            pygame.display.flip()

        pygame.quit()
