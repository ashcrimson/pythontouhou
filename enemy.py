import math

import pygame

from setting import *
from explosion import Explosion
from enemy_bullet import EnemyBullet


class Enemy(pygame.sprite.Sprite):

    def __init__(
            self, groups, x, y, bullet_group, enemy_killed,
            entry_target, exit_target, shot_delays, target_provider,
            bullet_count=1, bullet_speed=3.2
    ):
        super().__init__(groups)

        self.screen = pygame.display.get_surface()
        self.bullet_group = bullet_group
        self.enemy_killed = enemy_killed
        self.target_provider = target_provider
        self.enemy_bullet_group = pygame.sprite.Group()
        self.exposion_group = pygame.sprite.Group()

        self.image_list = [
            pygame.image.load(f"assets/img/enemy/enemy{i}.png")
            for i in range(5)
        ]
        self.index = 0
        self.pre_image = self.image_list[self.index]
        self.image = pygame.transform.scale(self.pre_image, (50, 50))
        self.rect = self.image.get_rect(center=(x, y))

        self.position = pygame.math.Vector2(self.rect.center)
        self.entry_target = pygame.math.Vector2(entry_target)
        self.exit_target = pygame.math.Vector2(exit_target)
        self.path_speed = 2.4
        self.state = "enter"
        self.shot_delays = shot_delays
        self.shot_timer = 0
        self.shots_fired = 0
        self.bullet_count = bullet_count
        self.bullet_speed = bullet_speed

        self.health = 1
        self.alive = True
        self.explosion = False

        self.explosion_sound = pygame.mixer.Sound(
            "assets/sound/explosion.mp3"
        )
        self.explosion_sound.set_volume(0.2)

    def move_toward(self, target):
        distance = target - self.position

        if distance.length_squared() <= self.path_speed ** 2:
            self.position = target
            self.rect.center = round(self.position.x), round(self.position.y)
            return True

        self.position += distance.normalize() * self.path_speed
        self.rect.center = round(self.position.x), round(self.position.y)
        return False

    def move(self):
        if self.state == "enter":
            if self.move_toward(self.entry_target):
                self.state = "attack"
        elif self.state == "retreat":
            if self.move_toward(self.exit_target):
                self.state = "exit"

    def shoot(self):
        if self.state != "attack":
            return

        self.shot_timer += 1

        if (
                self.shots_fired < len(self.shot_delays)
                and self.shot_timer >= self.shot_delays[self.shots_fired]
        ):
            self.fire_aimed_burst()
            self.shots_fired += 1

        if self.shots_fired == len(self.shot_delays):
            self.state = "retreat"

    def fire_aimed_burst(self):
        target_x, target_y = self.target_provider()
        origin = pygame.math.Vector2(self.rect.centerx, self.rect.bottom)
        target = pygame.math.Vector2(target_x, target_y)
        base_angle = math.atan2(target.y - origin.y, target.x - origin.x)

        for index in range(self.bullet_count):
            angle_offset = (index - (self.bullet_count - 1) / 2) * 0.12
            angle = base_angle + angle_offset
            EnemyBullet(
                self.enemy_bullet_group,
                origin.x,
                origin.y,
                velocity_x=math.cos(angle) * self.bullet_speed,
                velocity_y=math.sin(angle) * self.bullet_speed
            )

    def animation(self):
        if self.alive:
            self.index += 0.15
            if self.index >= len(self.image_list):
                self.index = 0

            self.pre_image = self.image_list[int(self.index)]
            self.image = pygame.transform.scale(self.pre_image, (50, 50))
        else:
            self.image.set_alpha(0)

    def check_off_screen(self):
        if self.state == "exit" and len(self.enemy_bullet_group) == 0:
            self.kill()

    def collision_bullet(self):
        if self.state == "exit":
            return

        for bullet in self.bullet_group:
            if self.rect.colliderect(bullet.rect):
                bullet.kill()
                self.health -= 1

                if self.health <= 0:
                    self.alive = False
                    break

    def check_death(self):
        if not self.alive and not self.explosion:
            Explosion(
                self.exposion_group, self.rect.centerx, self.rect.centery
            )
            self.explosion = True
            self.enemy_killed(self.rect.center)
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

        self.exposion_group.draw(self.screen)
        self.exposion_group.update()
        self.enemy_bullet_group.draw(self.screen)
        self.enemy_bullet_group.update()
