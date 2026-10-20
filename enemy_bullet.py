import pygame
import math
from setting import *


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(
        self, groups, x, y, speed=5, direction=0,
        velocity_x=None, velocity_y=None
    ):
        super().__init__(groups)

        self.image_list = []
        for i in range(2):
            image = pygame.image.load(
                f"assets/img/bullet/enemy_shot{i}.png"
            ).convert_alpha()
            self.image_list.append(image)

        self.index = 0
        self.image = pygame.transform.scale(
            self.image_list[0], (24, 48)
        )
        self.rect = self.image.get_rect(midtop=(x, y))

        self.speed = speed
        self.direction = direction
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

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
        if self.velocity_x is not None:
            self.rect.x += self.velocity_x
            self.rect.y += self.velocity_y
        else:
            self.rect.x += self.direction
            self.rect.y += self.speed

    def update(self):
        self.move()
        self.check_off_screen()
        self.animation()