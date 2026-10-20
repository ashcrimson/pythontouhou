import pygame

import explosion
from setting import *
import random
from explosion import Explosion
from enemy_bullet import EnemyBullet

class Enemy(pygame.sprite.Sprite):
    def __init__(
            self, groups, x, y, bullet_group, enemy_killed,
            target_y=100, move_direction=0, shot_count=3
    ):
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

        # Movimiento y ataque
        self.target_y = target_y
        self.move_direction = move_direction
        self.shot_count = shot_count
        self.state = "enter"
        self.speed = 2
        self.shoot_timer = random.randint(40, 70)
        self.shots_fired = 0
        self.max_shots = 2

        #体力
        self.health = 3
        self.alive = True

        #爆発
        self.explosion = False

        #効果音
        self.explosion_sound = pygame.mixer.Sound('assets/sound/explosion.mp3')
        self.explosion_sound.set_volume(0.2)

    def move(self):
        if self.state == "enter":
            self.rect.x += self.move_direction
            self.rect.y += self.speed

            if self.rect.top >= self.target_y:
                self.rect.top = self.target_y
                self.state = "attack"

        elif self.state == "retreat":
            self.rect.y -= 3

    def shoot(self):
        if self.state != "attack":
            return

        self.shoot_timer += 1

        if self.shoot_timer >= 70:
            if self.shot_count == 5:
                directions = [-2, -1, 0, 1, 2]
                speed = 3.2
            else:
                directions = [-1.5, 0, 1.5]
                speed = 3.8

            for direction in directions:
                EnemyBullet(
                    self.enemy_bullet_group,
                    self.rect.centerx,
                    self.rect.bottom,
                    speed=speed,
                    direction=direction
                )

            self.shoot_timer = 0
            self.shots_fired += 1

            if self.shots_fired >= self.max_shots:
                self.state = "retreat"

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
        if self.state == "retreat" and self.rect.bottom < 0:
            if len(self.enemy_bullet_group) == 0:
                self.kill()

    def collision_bullet(self):
        if self.rect.top < 0 or self.state == "retreat":
            return

        for bullet in self.bullet_group:
            if self.rect.colliderect(bullet.rect):
                bullet.kill()
                self.health -= 1

                if self.health <= 0:
                    self.alive = False
                    break

    def check_death(self):
        if self.alive == False and self.explosion == False:
            self.speed = 0
            explosion = Explosion(self.exposion_group, self.rect.centerx, self.rect.centery)
            self.explosion = True
            self.enemy_killed()
            self.explosion_sound.play()

        if self.explosion and len(self.exposion_group) == 0:
            self.enemy_bullet_group.empty()
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