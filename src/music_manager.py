import pygame
import logging

class MusicManager:
    def __init__(self):
        pygame.mixer.init()
        self.logger = logging.getLogger(__name__)

    def load_music(self, level_name):
        """Carrega e toca a música do nível especificado ou do menu."""
        music_path = f"assets/audio/soundtrack/{level_name}"
        fallback_path = "assets/audio/soundtrack/backgroundmusic.ogg"

        try:
            pygame.mixer.music.load(music_path)
            self.logger.info(f"Música carregada: {music_path}")
        except Exception as e:
            self.logger.error(f"Erro ao carregar '{music_path}': {e}")
            try:
                pygame.mixer.music.load(fallback_path)
                self.logger.info(f"Música padrão carregada: {fallback_path}")
            except Exception as fallback_error:
                self.logger.error(f"Erro ao carregar música padrão '{fallback_path}': {fallback_error}")
                return

        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)