import pygame
from objects.dynamic_objects.player import Player
from objects.static_objects.terrain import Terrain
from level_loader import LevelLoader

pygame.init()

# WIDTH, HEIGHT = 800, 600
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("Teste de Execução")

# WHITE = (255, 255, 255)

# player = Player(position=(100, 300), size=(50, 50), speed=5, jump_power=15)



# platforms = [
#     Terrain((0, HEIGHT - 50), (WIDTH, 50)),  
#     Terrain((200, 450), (150, 20)),
#     Terrain((400, 350), (150, 20)),
#     Terrain((600, 250), (150, 20)),
# ]

# all_sprites = pygame.sprite.Group()
# all_sprites.add(player)
# for platform in platforms:
#     all_sprites.add(platform)
    
screen = pygame.display.set_mode((640, 480))

level_name = sys.argv[1] if len(sys.argv) > 1 else "level_1"

player = Player(position=(100, 300), size=(50, 50), speed=5, jump_power=15)
level = LevelLoader(screen, player, level_name)

clock = pygame.time.Clock()

running = True
while running:
    clock.tick(60) 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    level.update()

    player.movement_update(level.platforms, WIDTH)

    screen.fill(WHITE)
    level.draw()
    pygame.display.flip()

pygame.quit()
