import pygame
from level import Level

pygame.init()


# Pegar o timestamp de quando começar a processar o frame, e depois quando ele terminra, o falor do tempo decorrido se chama
# delta t, quando for atualizar a posição de um objeto, multiplique a velocidade por esse valor e só depois faça a soma à posição 
# para poder fazer a movimentação

# Já em relação à POO, ao se referir a um atributo de uma classe, usar o this para deixar claro que é de uma classe e não uma variavel qualquer
# ou sempre nomear o atributo com m_ (member), ex: m_position

WIDTH, HEIGHT = 1600, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Teste de Execução")

level = Level(screen, "level_1")

clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    level.update()
    level.draw()
    pygame.display.flip()

pygame.quit()
