import pygame
import sys
from player import MusicPlayer

pygame.init()

WIDTH = 600
HEIGHT = 200

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Music Player")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

font = pygame.font.SysFont(None, 36)

# создаём плеер
player = MusicPlayer("./musicPlayer/music/sampleTracks")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                player.play()
            elif event.key == pygame.K_s:
                player.stop()
            elif event.key == pygame.K_n:
                player.next()
            elif event.key == pygame.K_b:
                player.previous()
            elif event.key == pygame.K_q:
                running = False

    screen.fill(WHITE)

    # отображение текущего трека
    text = font.render(player.get_current_track(), True, BLACK)
    screen.blit(text, (20, 80))

    pygame.display.flip()

pygame.quit()
sys.exit()