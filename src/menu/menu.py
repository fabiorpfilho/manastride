import pygame
from menu.desc_section import DescriptionSection
from menu.main_menu import MainMenu
from menu.spell_section import SpellsSection
from menu.rune_section import RunesSection 

class Menu:
    def __init__(self, screen, width, height, player):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont('arial', 24)
        self.player = player
        self.current_menu = 'main'
        self.icon_cache = {}
        self.selected_spell = None  # Index of selected spell (0, 1, or 2)
        self.selected_rune = None   # Index of selected rune
        
        # Initialize section classes
        self.main_menu = MainMenu(self)
        self.spells_section = SpellsSection(self)
        self.runes_section = RunesSection(self)
        self.description_section = DescriptionSection(self)

    def handle_input(self, events, paused, running):
        """Processa entrada e coordena entre as seções."""
        mouse_pos = pygame.mouse.get_pos()
        
        if self.current_menu == 'main':
            paused, running = self.main_menu.handle_input(events, paused, running, mouse_pos)
        elif self.current_menu == 'inventory':
            # Handle input for spells or runes based on selected section
            if self.spells_section.selected_section == 'spells':
                paused, running = self.spells_section.handle_input(events, paused, running, mouse_pos)
            else:
                paused, running = self.runes_section.handle_input(events, paused, running, mouse_pos)
            # Handle ESC to return to main menu
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.current_menu = 'main'
                    self.main_menu.selected_item = 0
                    self.spells_section.selected_item = 0
                    self.spells_section.selected_section = 'spells'
                    self.runes_section.selected_item = 0
                    self.selected_spell = None
                    self.selected_rune = None

        return paused, running

    def draw(self):
        """Desenha o menu apropriado com base no estado."""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 255) if self.current_menu == 'inventory' else (0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        mouse_pos = pygame.mouse.get_pos()
        if self.current_menu == 'main':
            self.main_menu.draw(mouse_pos)
        elif self.current_menu == 'inventory':
            self.spells_section.draw(mouse_pos)
            self.runes_section.draw(mouse_pos)
            self.description_section.draw(mouse_pos)
            # Draw "Voltar (ESC)" text
            back_text = self.font.render("Voltar (ESC)", True, (255, 255, 255))
            back_rect = back_text.get_rect(center=(self.width // 2, self.height // 2 + 350))
            self.screen.blit(back_text, back_rect)
