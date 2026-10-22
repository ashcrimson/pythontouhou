import pygame
import math
from setting import *


class EnemyBullet(pygame.sprite.Sprite):
    images = None

    def __init__(
        self, groups, x, y, speed=5, direction=0,
        velocity_x=None, velocity_y=None
    ):
        super().__init__(groups)

        if EnemyBullet.images is None:
            EnemyBullet.images = [
                pygame.image.load(
                    f"assets/img/bullet/enemy_shot{i}.png"
                ).convert_alpha()
                for i in range(2)
            ]

        self.image_list = EnemyBullet.images
        self.index = 0
        self.image = pygame.transform.scale(
            self.image_list[0], (24, 48)
        )
        self.rect = self.image.get_rect(midtop=(x, y))
        self.position = pygame.math.Vector2(self.rect.center)

        if velocity_x is None:
            self.velocity = pygame.math.Vector2(direction, speed)
        else:
            self.velocity = pygame.math.Vector2(velocity_x, velocity_y)

    def check_off_screen(self):
        if (
            self.rect.bottom < 0
            or self.rect.top > screen_height
            or self.rect.right < 0
            or self.rect.left > screen_width
        ):
            self.kill()

    def animation(self):
        self.index += 0.05
        if self.index >= len(self.image_list):
            self.index = 0

        self.image = pygame.transform.scale(
            self.image_list[int(self.index)], (24, 48)
        )

    def move(self):
        self.position += self.velocity
        self.rect.center = round(self.position.x), round(self.position.y)

    def update(self):
        self.move()
        self.check_off_screen()
        self.animation()
