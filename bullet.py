import pygame
from setting import *


class Bullet(pygame.sprite.Sprite):

    def __init__(self, groups,x,y):
        super().__init__(groups)

        #画像
        self.image_list = []
        for i in range(2):
            image = pygame.image.load(f"assets/img/bullet/{i}.png")
            self.image_list.append(image)

        self.index = 0
        self.pre_image = self.image_list[self.index]
        self.image = pygame.transform.scale(self.pre_image,(24,48))
        self.rect = self.image.get_rect(midbottom=(x,y))

        #移動
        self.speed = 8

    def check_off_screen(self):
        if self.rect.bottom < 0:
            self.kill()

    def animation(self):
        self.index += 0.05

        if self.index >= len(self.image_list):
            self.index = 0

        self.pre_image = self.image_list[int(self.index)]
        self.image = pygame.transform.scale(self.pre_image, (24, 48))

    def move(self):
        self.rect.y -= self.speed

    def update(self):
        self.move()
        self.check_off_screen()
        self.animation()