import pygame
from pygame.sprite import Sprite

from setting import *
from bullet import Bullet

class Player(pygame.sprite.Sprite):

    def __init__(self, groups, x, y, enemy_group):
            super().__init__(groups)

            self.screen = pygame.display.get_surface()

            #グループ
            self.bullet_group = pygame.sprite.Group()
            self.enemy_group = enemy_group

            #画像
            self.image_list = []
            for i in range(3):
                image = pygame.image.load(f"assets/img/player/reimu{i}.png")
                self.image_list.append(image)

            self.index = 0 #0:idle, 1:left, 2:right
            self.pre_image = self.image_list[self.index]
            self.image = pygame.transform.scale(self.pre_image, (50, 50))
            self.rect = self.image.get_rect(center = (x, y))

            #移動
            self.direction = pygame.math.Vector2()
            self.speed = 5

            #弾
            self.fire = False
            self.timer = 0

            #体力
            self.health = 1
            self.alive = True

            #効果音
            self.shot_sound = pygame.mixer.Sound('assets/sound/shot.mp3')
            self.shot_sound.set_volume(0.2)
            self.death_sound = pygame.mixer.Sound('assets/sound/death.mp3')
            self.death_sound.set_volume(0.2)



    def input(self):
        key = pygame.key.get_pressed()

        if key[pygame.K_UP]:
            self.direction.y = -1
        elif key[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if key[pygame.K_LEFT]:
            self.direction.x = -1
            self.index = 1
        elif key[pygame.K_RIGHT]:
            self.direction.x = 1
            self.index = 2
        else:
            self.direction.x = 0
            self.index = 0

        if key[pygame.K_z] and self.fire == False:
            bullet = Bullet(self.bullet_group, self.rect.centerx, self.rect.top)
            self.fire = True
            self.shot_sound.play()

    def cooldown_bullet(self):
        if self.fire:
            self.timer += 1
        if self.timer > 10:
            self.timer = 0
            self.fire = False

    def move(self):
        if self.direction.magnitude() != 0:
            self.direction.normalize()

        self.rect.x += self.direction.x * self.speed
        self.check_off_screen("horizontal")
        self.rect.y += self.direction.y * self.speed
        self.check_off_screen("vertical")

    def check_off_screen(self, direction):
        if direction == 'horizontal':
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > screen_width:
                self.rect.right = screen_width

        if direction == 'vertical':
            if self.rect.top < 0:
                self.rect.top = 0
            if self.rect.bottom > screen_height:
                self.rect.bottom = screen_height

    def collision_enemy(self):
        for enemy in self.enemy_group:
            if self.rect.colliderect(enemy.rect) and enemy.alive:
                self.health -= 1

        if self.health <= 0:
            self.alive = False

    def check_death(self):
        if self.alive == False:
            self.death_sound.play()
            self.kill()

    def update_image(self):
        self.pre_image = self.image_list[self.index]
        self.image = pygame.transform.scale(self.pre_image, (50, 50))

    def update(self):
        self.input()
        self.move()
        self.update_image()
        self.cooldown_bullet()
        self.collision_enemy()
        self.check_death()

        #グループの描画と更新
        self.bullet_group.draw(self.screen)
        self.bullet_group.update()

        print(self.bullet_group)