import pygame
import json
from datetime import datetime
from config import HIGHLIGHT_COLOR, BUTTON_COLOR

class ScoreList:
    def __init__(self, menu):
        self.menu = menu
        self.width = menu.width
        self.height = menu.height
        self.title_font = pygame.font.SysFont('arial', 72, bold=True)  # Fonte grande e em negrito para o título
        self.scores_font = pygame.font.SysFont('arial', 28)  # Fonte para lista de pontuações
        self.button_font = pygame.font.SysFont('arial', 36, bold=True)  # Fonte para botão Voltar
        self.pagination_font = pygame.font.SysFont('arial', 28, bold=True)  # Fonte menor para botões de paginação
        self.current_page = 0  # Página atual (0-based)
        self.items_per_page = 5  # Limite de 5 itens por página

    def load_scores(self):
        """Carrega as pontuações de scores.json, ordenadas por pontuação descendente."""
        try:
            with open("scores.json", "r") as file:
                scores = json.load(file)
                # Ordena por pontuação em ordem descendente
                return sorted(scores, key=lambda x: x["score"], reverse=True)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def draw(self, mouse_pos):
        """Desenha a tela de lista de pontuações com paginação."""
        # Gradiente de fundo
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for y in range(self.height):
            alpha = 180 + (y / self.height) * 50  # Gradiente de 180 a 230 de opacidade
            overlay.fill((0, 0, 0, int(alpha)), (0, y, self.width, 1))
        self.menu.screen.blit(overlay, (0, 0))

        # Título
        title = "Pontuações"
        title_text = self.title_font.render(title, True, (255, 255, 255))
        title_shadow = self.title_font.render(title, True, (50, 50, 50))  # Sombra cinza
        title_rect = title_text.get_rect(center=(self.width // 2, self.height // 2 - 200))
        title_shadow_rect = title_rect.copy()
        title_shadow_rect.move_ip(3, 3)  # Deslocamento da sombra
        self.menu.screen.blit(title_shadow, title_shadow_rect)
        self.menu.screen.blit(title_text, title_rect)

        # Lista de pontuações
        scores = self.load_scores()
        if not scores:
            text = self.scores_font.render("Nenhuma pontuação disponível", True, (255, 255, 255))
            shadow = self.scores_font.render("Nenhuma pontuação disponível", True, (50, 50, 50))
            text_rect = text.get_rect(topleft=(self.width // 2 - 200, self.height // 2 - 100))
            shadow_rect = text_rect.copy()
            shadow_rect.move_ip(2, 2)
            self.menu.screen.blit(shadow, shadow_rect)
            self.menu.screen.blit(text, text_rect)
        else:
            start_idx = self.current_page * self.items_per_page
            end_idx = start_idx + self.items_per_page
            for i, score in enumerate(scores[start_idx:end_idx]):  # Exibe apenas 5 itens
                # Converte o formato da data de YYYY-MM-DD HH:MM:SS para DD/MM/YYYY HH:MM
                try:
                    date_obj = datetime.strptime(score['timestamp'], "%Y-%m-%d %H:%M:%S")
                    formatted_date = date_obj.strftime("%d/%m/%Y %H:%M")
                except ValueError:
                    formatted_date = score['timestamp']  # Usa o original se falhar
                score_text = f"{start_idx + i + 1} - {score['name']}: {score['score']} ({formatted_date})"
                text = self.scores_font.render(score_text, True, (255, 255, 255))
                shadow = self.scores_font.render(score_text, True, (50, 50, 50))
                text_rect = text.get_rect(topleft=(self.width // 2 - 200, self.height // 2 - 130 + i * 60))
                shadow_rect = text_rect.copy()
                shadow_rect.move_ip(2, 2)
                self.menu.screen.blit(shadow, shadow_rect)
                self.menu.screen.blit(text, text_rect)

        # Botões de navegação: Anterior e Próximo
        button_y = self.height // 2 + 200
        prev_button_text = "Anterior"
        next_button_text = "Próximo"
        
        # Botão Anterior
        prev_button_color = (255, 255, 0) if self.pagination_font.render(prev_button_text, True, BUTTON_COLOR).get_rect(
            center=(self.width // 2 - 100, button_y)).collidepoint(mouse_pos) else BUTTON_COLOR
        prev_button = self.pagination_font.render(prev_button_text, True, prev_button_color)
        prev_button_rect = prev_button.get_rect(center=(self.width // 2 - 100, button_y))
        prev_button_bg_rect = prev_button_rect.inflate(16, 8)  # Padding reduzido para botões menores
        prev_bg_color = (50, 50, 100) if prev_button_color == BUTTON_COLOR else HIGHLIGHT_COLOR
        pygame.draw.rect(self.menu.screen, prev_bg_color, prev_button_bg_rect, border_radius=8)
        pygame.draw.rect(self.menu.screen, prev_button_color, prev_button_bg_rect, 2, border_radius=8)
        self.menu.screen.blit(prev_button, prev_button_rect)

        # Botão Próximo
        next_button_color = (255, 255, 0) if self.pagination_font.render(next_button_text, True, BUTTON_COLOR).get_rect(
            center=(self.width // 2 + 100, button_y)).collidepoint(mouse_pos) else BUTTON_COLOR
        next_button = self.pagination_font.render(next_button_text, True, next_button_color)
        next_button_rect = next_button.get_rect(center=(self.width // 2 + 100, button_y))
        next_button_bg_rect = next_button_rect.inflate(16, 8)  # Padding reduzido para botões menores
        next_bg_color = (50, 50, 100) if next_button_color == BUTTON_COLOR else HIGHLIGHT_COLOR
        pygame.draw.rect(self.menu.screen, next_bg_color, next_button_bg_rect, border_radius=8)
        pygame.draw.rect(self.menu.screen, next_button_color, next_button_bg_rect, 2, border_radius=8)
        self.menu.screen.blit(next_button, next_button_rect)

        # Botão Voltar (abaixo dos botões de navegação)
        back_button_text = "Voltar (Enter/Esc)"
        back_button_y = self.height // 2 + 350
        back_button_color = (255, 255, 0) if self.button_font.render(back_button_text, True, BUTTON_COLOR).get_rect(
            center=(self.width // 2, back_button_y)).collidepoint(mouse_pos) else BUTTON_COLOR
        back_button = self.button_font.render(back_button_text, True, back_button_color)
        back_button_rect = back_button.get_rect(center=(self.width // 2, back_button_y))
        back_button_bg_rect = back_button_rect.inflate(20, 10)
        back_bg_color = (50, 50, 100) if back_button_color == BUTTON_COLOR else HIGHLIGHT_COLOR
        pygame.draw.rect(self.menu.screen, back_bg_color, back_button_bg_rect, border_radius=10)
        pygame.draw.rect(self.menu.screen, back_button_color, back_button_bg_rect, 2, border_radius=10)
        self.menu.screen.blit(back_button, back_button_rect)

        return prev_button_rect, next_button_rect, back_button_rect  # Retorna os retângulos para uso no handle_input

    def handle_input(self, events, running, mouse_pos):
        """Processa entrada para a tela de pontuações."""
        scores = self.load_scores()
        max_page = (len(scores) - 1) // self.items_per_page if scores else 0

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    print("Voltando ao menu inicial via tecla Enter/Esc")
                    self.menu.current_menu = 'initial'
                    self.menu.initial_menu.selected_item = 0
                elif event.key == pygame.K_LEFT and self.current_page > 0:
                    print("Página anterior selecionada via tecla Left")
                    self.current_page -= 1
                elif event.key == pygame.K_RIGHT and self.current_page < max_page:
                    print("Próxima página selecionada via tecla Right")
                    self.current_page += 1
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                print("Clique do mouse detectado na tela de pontuações")
                prev_button_rect = self.pagination_font.render("Anterior", True, (255, 255, 255)).get_rect(
                    center=(self.width // 2 - 100, self.height // 2 + 200))
                next_button_rect = self.pagination_font.render("Próximo", True, (255, 255, 255)).get_rect(
                    center=(self.width // 2 + 100, self.height // 2 + 200))
                back_button_rect = self.button_font.render("Voltar (Enter/Esc)", True, (255, 255, 255)).get_rect(
                    center=(self.width // 2, self.height // 2 + 350))
                if prev_button_rect.collidepoint(mouse_pos) and self.current_page > 0:
                    print("Página anterior selecionada via clique do mouse")
                    self.current_page -= 1
                elif next_button_rect.collidepoint(mouse_pos) and self.current_page < max_page:
                    print("Próxima página selecionada via clique do mouse")
                    self.current_page += 1
                elif back_button_rect.collidepoint(mouse_pos):
                    print("Voltando ao menu inicial via clique do mouse")
                    self.menu.current_menu = 'initial'
                    self.menu.initial_menu.selected_item = 0
        return running