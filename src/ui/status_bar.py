import pygame
from ui.ui import Ui
from asset_loader import AssetLoader

class StatusBar(Ui):
    def __init__(self, screen):
        super().__init__(screen)
        # Scaling factors
        self.scale_factor = 3.0  # Increase size by 200% for bars and containers
        self.icon_scale_factor = 2.0  # Smaller scale for icons (33% smaller than bars)

        # Load images
        self.status_bar_img = AssetLoader.load_image("assets/ui/status_bar.png")
        self.health_bar_img = AssetLoader.load_image("assets/ui/health_bar.png")
        self.heart_icon = AssetLoader.load_image("assets/ui/heart1.png")
        self.mana_bar_img = AssetLoader.load_image("assets/ui/mana_bar.png")
        self.staff_icon = AssetLoader.load_image("assets/ui/staff.png")
        self.shield_bar_img = AssetLoader.load_image("assets/ui/shield_bar.png")

        # Scale images
        self.status_bar_img = pygame.transform.scale(
            self.status_bar_img,
            (int(self.status_bar_img.get_width() * self.scale_factor), int(self.status_bar_img.get_height() * self.scale_factor))
        )
        self.heart_icon = pygame.transform.scale(
            self.heart_icon,
            (int(self.heart_icon.get_width() * self.icon_scale_factor), int(self.heart_icon.get_height() * self.icon_scale_factor))
        )
        self.staff_icon = pygame.transform.scale(
            self.staff_icon,
            (int(self.staff_icon.get_width() * self.icon_scale_factor), int(self.staff_icon.get_height() * self.icon_scale_factor))
        )
        self.health_bar_img = pygame.transform.scale(
            self.health_bar_img,
            (int(self.health_bar_img.get_width() * self.scale_factor), int(self.health_bar_img.get_height() * self.scale_factor))
        )
        self.mana_bar_img = pygame.transform.scale(
            self.mana_bar_img,
            (int(self.mana_bar_img.get_width() * self.scale_factor), int(self.mana_bar_img.get_height() * self.scale_factor))
        )
        self.shield_bar_img = pygame.transform.scale(
            self.shield_bar_img,
            (int(self.health_bar_img.get_width() * self.scale_factor), int(self.health_bar_img.get_height() * self.scale_factor))  # Match health bar size
        )

        # Get full sizes for scaling
        self.status_bar_size = self.status_bar_img.get_size()
        self.health_full_size = self.health_bar_img.get_size()
        self.mana_full_size = self.mana_bar_img.get_size()
        self.shield_full_size = self.shield_bar_img.get_size()

        # Define icon space (for alignment with bars)
        self.icon_space = self.heart_icon.get_width() + 10 * self.scale_factor  # Icon + padding (using scale_factor for padding)

    def draw(self, player):
        # Positions: top-left, vertically stacked status bars
        panel_pos = (10, 10)
        padding = 5 * self.scale_factor
        container_spacing = 5 * self.scale_factor
        left_shift = 2 * self.scale_factor  # Move bars 2 pixels left (scaled)

        # Health: icon + status_bar_img + bar + shield (if applicable)
        health_container_y = panel_pos[1]
        # Draw icon to the left of the container
        heart_pos = (panel_pos[0], health_container_y + (self.status_bar_size[1] - self.heart_icon.get_height()) / 2)
        self.screen.blit(self.heart_icon, heart_pos)
        # Draw container (status_bar_img) to the right of the icon
        health_container_x = panel_pos[0] + self.icon_space
        self.screen.blit(self.status_bar_img, (health_container_x, health_container_y))
        # Draw health bar inside the container, shifted left
        health_ratio = 0 if player.max_health <= 0 else player.health / player.max_health
        health_ratio = max(0, min(health_ratio, 1))  # Garante entre 0 e 1

        # Calcula o tamanho da barra com limite mínimo de 1 pixel
        width = max(1, int(self.health_full_size[0] * health_ratio))
        height = max(1, self.health_full_size[1])
        health_size = (width, height)

        scaled_health = pygame.transform.scale(self.health_bar_img, health_size)
        health_pos = (
            health_container_x + padding - left_shift,
            health_container_y + (self.status_bar_size[1] - self.health_full_size[1]) / 2
        )

        self.screen.blit(scaled_health, health_pos)
        # Draw shield bar over health bar if shield_health > 0
        if player.shield_health > 0:
            # Cap shield at max_health
            shield_ratio = min(player.shield_health / player.max_health, 1.0)  # Cap at 100% of health bar
            shield_size = (int(self.health_full_size[0] * shield_ratio), self.health_full_size[1])
            scaled_shield = pygame.transform.scale(self.shield_bar_img, shield_size)
            shield_pos = health_pos  # Same position as health bar
            self.screen.blit(scaled_shield, shield_pos)

        # Mana: icon + status_bar_img + bar
        # --- MANA BAR ---
        mana_container_y = health_container_y + self.status_bar_size[1] + container_spacing

        # Ícone da staff
        staff_pos = (panel_pos[0], mana_container_y + (self.status_bar_size[1] - self.staff_icon.get_height()) / 2)
        self.screen.blit(self.staff_icon, staff_pos)

        # Container da barra de mana
        mana_container_x = panel_pos[0] + self.icon_space
        self.screen.blit(self.status_bar_img, (mana_container_x, mana_container_y))

        # Calcula tamanho da barra de mana
        mana_ratio = 0 if player.max_mana <= 0 else player.mana / player.max_mana
        mana_width = int(self.mana_full_size[0] * mana_ratio)
        mana_width = max(mana_width, 0)                 # <-- proteção rápida
        mana_size = (mana_width, self.mana_full_size[1])

        # Escala e desenha a barra
        scaled_mana = pygame.transform.scale(self.mana_bar_img, mana_size)
        mana_pos = (
            mana_container_x + padding - left_shift,
            mana_container_y + (self.status_bar_size[1] - self.mana_full_size[1]) / 2
        )
        self.screen.blit(scaled_mana, mana_pos)