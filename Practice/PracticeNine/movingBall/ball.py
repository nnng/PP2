import pygame

class Ball:
    def __init__(self, x, y, radius, speed, screen_width, screen_height):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.screen_width = screen_width
        self.screen_height = screen_height

    def move(self, keys):
        # вверх
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if self.y - self.speed - self.radius >= 0:
                self.y -= self.speed

        # вниз
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if self.y + self.speed + self.radius <= self.screen_height:
                self.y += self.speed

        # влево
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if self.x - self.speed - self.radius >= 0:
                self.x -= self.speed

        # вправо
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if self.x + self.speed + self.radius <= self.screen_width:
                self.x += self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (self.x, self.y), self.radius)