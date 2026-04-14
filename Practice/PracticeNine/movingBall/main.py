import pygame
import sys
from ball import Ball

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball")

WHITE = (255, 255, 255)

# создаём объект шара
ball = Ball(WIDTH // 2, HEIGHT // 2, 25, 1, WIDTH, HEIGHT)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # движение шара
    ball.move(keys)

    # отрисовка
    screen.fill(WHITE)
    ball.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()