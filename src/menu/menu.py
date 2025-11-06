import pygame
from menu.desc_section import DescriptionSection
from menu.main_menu import MainMenu
from menu.spell_section import SpellsSection
from menu.rune_section import RunesSection 
from menu.initial_menu import InitialMenu
from menu.instruction_section import InstructionSection
from menu.game_end import GameEnd
from menu.score_list import ScoreList
from menu.credit_menu import CreditMenu

class Menu:
    def __init__(self, screen, width, height, player):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont('arial', 24)
        self.player = player
        self.current_menu = 'initial'
        self.icon_cache = {}
        self.selected_spell = None
        self.selected_rune = None
        self.selected_menu_item = 0
        
        self.main_menu = MainMenu(self)
        self.spells_section = SpellsSection(self)
        self.runes_section = RunesSection(self)
        self.description_section = DescriptionSection(self)
        self.instruction_section = InstructionSection(self)
        self.initial_menu = InitialMenu(self)
        self.game_end = GameEnd(self)
        self.score__list = ScoreList(self)
        self.credits = CreditMenu(self)

    def handle_input(self, events, paused, running, mouse_pos=None):
        """Processa entrada e coordena entre as seções, com manejo centralizado de ESC."""
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()

        # Manejo centralizado de ESC
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.current_menu == 'initial':
                    print("ESC no menu inicial: Saindo do jogo")
                    return False, False  # Sai do jogo
                elif self.current_menu == 'end':
                    print("ESC na tela de fim: Saindo do jogo")
                    return False, False  # Sai do jogo
                elif self.current_menu in ['inventory', 'controls', 'scores', 'credits']:
                    print("ESC em sub-menu: Voltando ao menu principal")
                    self.current_menu = 'main'
                    self.main_menu.selected_item = 0
                    self.spells_section.selected_item = 0
                    self.spells_section.selected_section = 'spells'
                    self.runes_section.selected_item = 0
                    self.selected_spell = None
                    self.selected_rune = None
                    return True, running  # Mantém pausa, continua running
                elif self.current_menu == 'main':
                    print("ESC no menu principal: Retomando o jogo")
                    self.selected_menu_item = 0
                    return False, running  # Despausa o jogo
                else:
                    print("ESC em menu desconhecido: Ignorando")
                    return paused, running

        # Delega para seções específicas (sem duplicar ESC)
        if self.current_menu == 'initial':
            start_game, running = self.initial_menu.handle_input(events, mouse_pos, running, is_initial=True)
            return start_game, running
        elif self.current_menu == 'main':
            paused, running = self.main_menu.handle_input(events, paused, running, mouse_pos)
        elif self.current_menu == 'inventory':
            if self.player is None:
                print("Aviso: Player é None ao tentar acessar o menu de inventário. Retornando ao menu principal.")
                self.current_menu = 'main'
                self.main_menu.selected_item = 0
                return paused, running
            if self.spells_section.selected_section == 'spells':
                paused, running = self.spells_section.handle_input(events, paused, running, mouse_pos)
            else:
                paused, running = self.runes_section.handle_input(events, paused, running, mouse_pos)
        elif self.current_menu == 'controls':
            print("Chamando handle_input para menu de controles")
            _, running = self.initial_menu.handle_input(events, mouse_pos, running, is_initial=False)
            paused = True
        elif self.current_menu == 'scores':
            running = self.score__list.handle_input(events, running, mouse_pos)
            paused = True
        elif self.current_menu == 'credits':
            print("Chamando handle_input para menu de créditos")
            running = self.credits.handle_input(events, mouse_pos, running)
            paused = True
        elif self.current_menu == 'end':
            paused = True

        return paused, running
    def draw(self):
        """Desenha o menu apropriado com base no estado."""
        # --- Carrega o fundo apenas uma vez ---
        if not hasattr(self, "background_image"):
            try:
                self.background_image = pygame.image.load("assets/ui/menu_background.png").convert()
                self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
            except Exception as e:
                print(f"Erro ao carregar background do menu: {e}")
                # fallback em caso de erro
                self.background_image = pygame.Surface((self.width, self.height))
                self.background_image.fill((0, 0, 0))

        # --- Desenha o fundo ---
        if self.current_menu == 'inventory':
            self.screen.fill((0, 0, 0))  # fundo preto puro para o inventário
        else:
            self.screen.blit(self.background_image, (0, 0))

        # leve esmaecimento sobre a imagem
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))

        # --- Continua com o desenho do menu ---
        mouse_pos = pygame.mouse.get_pos()
        if self.current_menu == 'initial':
            self.initial_menu.draw(mouse_pos, is_initial=True)
        elif self.current_menu == 'main':
            self.main_menu.draw(mouse_pos)
        elif self.current_menu == 'inventory':
            if self.player is None:
                print("Aviso: Player é None ao tentar desenhar o menu de inventário. Desenhando menu principal.")
                self.current_menu = 'main'
                self.main_menu.draw(mouse_pos)
                return
            self.spells_section.draw(mouse_pos)
            self.runes_section.draw(mouse_pos)
            self.description_section.draw(mouse_pos)
            self.instruction_section.draw()
            back_text = self.font.render("Voltar (ESC)", True, (255, 255, 255))
            back_rect = back_text.get_rect(center=(self.width // 2, self.height // 2 + 350))
            self.screen.blit(back_text, back_rect)
        elif self.current_menu == 'controls':
            self.initial_menu.draw(mouse_pos, is_initial=False)
        elif self.current_menu == 'scores':
            self.score__list.draw(mouse_pos)
        elif self.current_menu == 'credits':
            self.credits.draw(mouse_pos)
        elif self.current_menu == 'end':
            self.game_end.draw()
