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

    def run(self):
        while self.running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.level.update()
            self.level.draw()
            pygame.display.flip()

        pygame.quit()
