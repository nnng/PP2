import pygame
import sys
from clock import Clock

pygame.init()

# размер окна (под картинку часов лучше квадрат)
WIDTH = 900
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mickey Clock")

# создаём объект часов
clock = Clock(WIDTH // 2, HEIGHT // 2)

# FPS (очень важно для стабильности)
fps = pygame.time.Clock()

running = True
while running:
    # обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # фон + стрелки
    screen.fill((255, 255, 255))

    # рисуем часы
    clock.draw(screen)

    # обновление экрана
    pygame.display.flip()

    # ограничение FPS (60 кадров в секунду)
    fps.tick(60)

pygame.quit()
sys.exit()