import pygame
import time
import math

class Clock:
    def __init__(self, center_x, center_y):
        self.center_x = center_x
        self.center_y = center_y

        self.background = pygame.image.load("./mickeysClock/images/mickeyclock.jpeg")

        self.bg_rect = self.background.get_rect()
        self.bg_rect.center = (self.center_x, self.center_y)

    def get_time_angles(self):
        t = time.localtime()

        seconds = t.tm_sec
        minutes = t.tm_min

        seconds_angle = math.radians(seconds * 6 - 90)
        minutes_angle = math.radians(minutes * 6 - 90)

        return seconds_angle, minutes_angle

    def draw_hand(self, screen, angle, length, color, width):
        x0, y0 = self.center_x, self.center_y

        end_x = x0 + length * math.cos(angle)
        end_y = y0 + length * math.sin(angle)

        pygame.draw.line(
            screen,
            color,
            (x0, y0),
            (end_x, end_y),
            width
        )

    def draw(self, screen):
        screen.blit(self.background, self.bg_rect)

        seconds_angle, minutes_angle = self.get_time_angles()

        self.draw_hand(
            screen,
            seconds_angle,
            300,
            (255, 0, 0),
            10
        )

        self.draw_hand(
            screen,
            minutes_angle,
            120,
            (0, 0, 0),
            20
        )