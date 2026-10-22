import pygame
from setting import *


class Bullet(pygame.sprite.Sprite):
    images = None

    def __init__(
            self, groups, x, y, direction=0, speed=8,
            homing_targets=None, target_provider=None, turn_rate=0.08
    ):
        super().__init__(groups)

        if Bullet.images is None:
            Bullet.images = [
                pygame.image.load(f"assets/img/bullet/shot{i}.png")
                for i in range(3)
            ]

        #画像
        self.image_list = Bullet.images

        self.index = 0
        self.pre_image = self.image_list[self.index]
        self.image = pygame.transform.scale(self.pre_image, (12, 32))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.position = pygame.math.Vector2(self.rect.center)

        #移動
        self.speed = speed
        self.velocity = pygame.math.Vector2(direction, -speed)
        self.homing_targets = homing_targets
        self.target_provider = target_provider
        self.turn_rate = turn_rate

    def check_off_screen(self):
        if self.rect.bottom < 0:
            self.kill()

    def animation(self):
        self.index += 0.05

        if self.index >= len(self.image_list):
            self.index = 0

        self.pre_image = self.image_list[int(self.index)]
        self.image = pygame.transform.scale(self.pre_image, (12, 32))

    def move(self):
        target = self.get_target()

        if target is not None:
            target_rect = getattr(target, "rect", target)
            target_direction = (
                pygame.math.Vector2(target_rect.center) - self.position
            )

            if target_direction.length_squared() > 0:
                desired_velocity = target_direction.normalize() * self.speed
                self.velocity = self.velocity.lerp(
                    desired_velocity, self.turn_rate
                )

        self.position += self.velocity
        self.rect.center = round(self.position.x), round(self.position.y)

    def get_target(self):
        targets = (
            self.target_provider()
            if self.target_provider is not None
            else self.homing_targets
        )

        if targets is None:
            return None

        targets = [
            target for target in targets
            if (getattr(target, "alive", True)
                and getattr(target, "state", "") != "retreat")
        ]

        if not targets:
            return None

        return min(
            targets,
            key=lambda target: self.position.distance_squared_to(
                getattr(target, "rect", target).center
            )
        )

    def update(self):
        self.move()
        self.check_off_screen()
        self.animation()
