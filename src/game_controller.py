import pygame
from level import Level

# Pegar o timestamp de quando começar a processar o frame, e depois quando ele terminra, o fator do tempo decorrido se chama
# delta t, quando for atualizar a posição de um objeto, multiplique a velocidade por esse valor e só depois faça a soma à posição
# para poder fazer a movimentação

class GameController:
    def __init__(self, width=1600, height=900, title="Teste de Execução"):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(title)

        self.level = Level(self.screen, "level_1")
        self.clock = pygame.time.Clock()
        self.running = True
        self.last_time = pygame.time.get_ticks()

    def run(self):
        while self.running:
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - self.last_time)   
            
            self.last_time = current_time
            
            # Limita a 100ms para evitar bugs em lag
            # delta_time = min(delta_time, 0.1)
            
            pygame.display.set_caption(f"{self.clock.get_fps():.1f} FPS")


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.level.update(delta_time)
            self.level.draw()
            pygame.display.flip()

        pygame.quit()
