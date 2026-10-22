import math

import pygame


class Bomb:

    def __init__(self, position):
        self.position = pygame.math.Vector2(position)
        self.duration = 120
        self.timer = 0
        self.damage_interval = 8

    @property
    def finished(self):
        return self.timer >= self.duration

    @property
    def should_damage(self):
        return self.timer % self.damage_interval == 0

    def update(self, position):
        self.position.update(position)
        self.timer += 1

    def draw(self, screen):
        progress = self.timer / self.duration
        radius = int(45 + progress * 230)
        alpha = int(180 * (1 - progress))
        center = (round(self.position.x), round(self.position.y))
        surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        pygame.draw.circle(surface, (255, 80, 80, alpha), center, radius, 3)
        pygame.draw.circle(surface, (255, 235, 180, alpha), center, radius // 2, 2)

        for index in range(8):
            angle = math.radians(self.timer * 5 + index * 45)
            offset = pygame.math.Vector2(radius * 0.65, 0).rotate_rad(angle)
            seal_center = (
                round(self.position.x + offset.x),
                round(self.position.y + offset.y)
            )
            pygame.draw.circle(surface, (255, 230, 180, alpha), seal_center, 9)
            pygame.draw.circle(surface, (220, 50, 50, alpha), seal_center, 5)

        screen.blit(surface, (0, 0))
