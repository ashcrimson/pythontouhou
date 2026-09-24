import pygame

import explosion
from setting import *
import random
from explosion import Explosion
from enemy_bullet import EnemyBullet

class Enemy(pygame.sprite.Sprite):
    def __init__(self, groups, x, y, bullet_group, enemy_killed):
        super().__init__(groups)

        self.screen = pygame.display.get_surface()

        #グループ
        self.bullet_group = bullet_group
        self.enemy_killed = enemy_killed
        self.enemy_bullet_group = pygame.sprite.Group()
        self.exposion_group = pygame.sprite.Group()

        #画像
        self.image_list = []
        for i in range(5):
            image = pygame.image.load(f'assets/img/enemy/enemy{i}.png')
            self.image_list.append(image)

        self.index = 0
        self.pre_image = self.image_list[self.index]
        self.image = pygame.transform.scale(self.pre_image, (50, 50))
        self.rect = self.image.get_rect(center=(x,y))

        #移動
        move_list = [1, -1]
        self.direction = pygame.math.Vector2((random.choice(move_list), 1))
        self.speed = 1
        self.timer = 0
        self.shoot_timer = 0

        #体力
        self.health = 1
        self.alive = True

        #爆発
        self.explosion = False

        #効果音
        self.explosion_sound = pygame.mixer.Sound('assets/sound/explosion.mp3')
        self.explosion_sound.set_volume(0.2)

    def move(self):
        self.timer += 1
        if self.timer > 80:
            self.direction.x *= -1
            self.timer = 0

        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

    def shoot(self):
        self.shoot_timer += 1

        if self.shoot_timer >= 100:
            EnemyBullet(
                self.enemy_bullet_group,
                self.rect.centerx,
                self.rect.bottom
            )
            self.shoot_timer = 0

    def animation(self):
        if self.alive == True:
            self.index += 0.15
            if self.index >= len(self.image_list):
                self.index = 0

            self.pre_image = self.image_list[int(self.index)]
            self.image = pygame.transform.scale(self.pre_image, (50, 50))
        else:
            self.image.set_alpha(0)

    def check_off_screen(self):
        if self.rect.top > screen_height:
            self.kill()

    def collision_bullet(self):
        for bullet in self.bullet_group:
            if self.rect.colliderect(bullet.rect):
                bullet.kill()
                self.health -= 1

            if self.health <= 0:
                self.alive = False

    def check_death(self):
        if self.alive == False and self.explosion == False:
            self.speed = 0
            explosion = Explosion(self.exposion_group, self.rect.centerx, self.rect.centery)
            self.explosion = True
            self.enemy_killed()
            self.explosion_sound.play()

        if self.explosion and len(self.exposion_group) == 0:
            self.kill()

    def update(self):
        self.move()
        self.shoot()
        self.check_off_screen()
        self.animation()
        self.collision_bullet()
        self.check_death()

        #グループの描画と更新
        self.exposion_group.draw(self.screen)
        self.exposion_group.update()
        self.enemy_bullet_group.draw(self.screen)
        self.enemy_bullet_group.update()