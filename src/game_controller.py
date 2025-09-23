import pygame
import time
import logging
from level import Level
from menu.menu import Menu
from config import DELTA_TIME
from music_manager import MusicManager

class GameController:
    def __init__(self, width=1600, height=900, title="Teste de Execução"):
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
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_ended:                            self.running = False
                        elif self.game_started:
                            self.paused = not self.paused
                            if not self.paused:
                                self.menu.selected_menu_item = 0
                                self.menu.current_menu = 'main'
                            else:
                                self.menu.current_menu = 'main'
                        else:
                            self.running = False

            if self.game_ended:
                self.menu.current_menu = 'end'
                action = self.menu.game_end.update(events)
                if action == "Reiniciar":
                    self.game_ended = False
                    self.game_started = False
                    self.menu.current_menu = 'initial'
                    self.music_manager.load_music("menu")
                elif action == "Sair":
                    self.running = False
                self.menu.draw()
            elif not self.game_started:
                self.menu.current_menu = 'initial'
                start_game, self.running = self.menu.handle_input(events, False, self.running, mouse_pos)
                if start_game:
                    self.level = Level(self.screen, self.starter_level)
                    self.menu.player = self.level.player
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
                        self.level = Level(self.screen, level_name, player_spawn)
                        self.menu.player = self.level.player
                        self.current_level_name = level_name
                        self.music_manager.load_music(self.current_level_name)
                    if self.level.is_completed:
                        self.game_ended = True
                self.level.draw()

                if self.paused:
                    self.menu.draw()

            pygame.display.flip()

        pygame.quit()