from ui.ui import Ui
import pygame
import math

class HotBar(Ui):
    def __init__(self, screen, asset_loader):
        super().__init__(screen, asset_loader)
        box_size = 50  # Tamanho de cada caixa (50x50 pixels)
        self.box_size = box_size
        self.box_spacing = 10  # Espaço entre caixas

        # Carregar ícones (assumindo que estão em assets/ui)
        try:
            projectile_icon = self.asset_loader.load_image("assets/ui/spells/projectile.png")
            dash_icon = self.asset_loader.load_image("assets/ui/spells/dash.png")
            shield_icon = self.asset_loader.load_image("assets/ui/spells/shield.png")
        except Exception as e:
            print(f"Erro ao carregar ícones da hotbar: {e}")
            # Ícones de fallback (retângulos coloridos)
            projectile_icon = pygame.Surface((40, 40))
            projectile_icon.fill((255, 0, 0))  # Vermelho para projétil
            dash_icon = pygame.Surface((40, 40))
            dash_icon.fill((0, 255, 0))  # Verde para dash
            shield_icon = pygame.Surface((40, 40))
            shield_icon.fill((0, 0, 255))  # Azul para escudo

        # Escalar ícones para caber nas caixas (40x40 para deixar margem)
        self.projectile_icon = pygame.transform.scale(projectile_icon, (40, 40))
        self.dash_icon = pygame.transform.scale(dash_icon, (40, 40))
        self.shield_icon = pygame.transform.scale(shield_icon, (40, 40))

    def draw(self, player):
        screen_width, screen_height = self.screen.get_size()
        total_width = (self.box_size * 3) + (self.box_spacing * 2)  # Largura total da hotbar
        start_x = (screen_width - total_width) // 2  # Centralizar horizontalmente
        start_y = screen_height - self.box_size - 10  # 10 pixels acima da borda inferior

        # Associar ícones e feitiços
        hotbar_items = [
            {"icon": self.projectile_icon, "rect": pygame.Rect(start_x, start_y, self.box_size, self.box_size), "spell": player.spell_system.spellbook[0]},
            {"icon": self.dash_icon, "rect": pygame.Rect(start_x + self.box_size + self.box_spacing, start_y, self.box_size, self.box_size), "spell": player.spell_system.spellbook[1]},
            {"icon": self.shield_icon, "rect": pygame.Rect(start_x + (self.box_size + self.box_spacing) * 2, start_y, self.box_size, self.box_size), "spell": player.spell_system.spellbook[2]},
        ]

        for item in hotbar_items:
            # Desenhar a caixa (fundo cinza com borda branca)
            pygame.draw.rect(self.screen, (50, 50, 50), item["rect"])  # Fundo
            pygame.draw.rect(self.screen, (255, 255, 255), item["rect"], 2)  # Borda

            # Desenhar o ícone centralizado na caixa
            icon_x = item["rect"].x + (self.box_size - 40) // 2  # Centralizar ícone (40x40) na caixa (50x50)
            icon_y = item["rect"].y + (self.box_size - 40) // 2
            self.screen.blit(item["icon"], (icon_x, icon_y))

            # Desenhar o indicador de cooldown como um arco (gráfico de pizza)
            spell = item["spell"]
            if spell.current_cooldown > 0:
                # Calcular a proporção do cooldown restante
                cooldown_ratio = spell.current_cooldown / spell.cooldown
                # Ângulo do arco (0 a 360 graus, no sentido anti-horário para esvaziar a partir das 12 horas)
                start_angle_rad = math.radians(-90 + 360 * (1 - cooldown_ratio))  # Começa ajustado pelo cooldown
                end_angle_rad = math.radians(-90)  # Termina no topo (12 horas)
                # Centro e raio do arco
                center = (item["rect"].centerx, item["rect"].centery)
                radius = self.box_size // 3  # Círculo menor (1/3 do tamanho da caixa)
                # Criar uma superfície temporária para o arco com transparência
                temp_surface = pygame.Surface((self.box_size, self.box_size), pygame.SRCALPHA)
                # Desenhar o arco na superfície temporária
                pygame.draw.arc(temp_surface, (0, 0, 0, 160),  # Preto com transparência
                                (self.box_size // 2 - radius, self.box_size // 2 - radius, radius * 2, radius * 2),
                                start_angle_rad, end_angle_rad, radius)  # Espessura igual ao raio para círculo cheio
                # Desenhar a superfície temporária na tela
                self.screen.blit(temp_surface, (item["rect"].x, item["rect"].y))