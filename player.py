import pygame
from pygame.sprite import Sprite

from setting import *
from bullet import Bullet

class Player(pygame.sprite.Sprite):

    def __init__(
            self, groups, x, y, enemy_group, target_provider=None
    ):
            super().__init__(groups)

            self.screen = pygame.display.get_surface()

            #グループ
            self.bullet_group = pygame.sprite.Group()
            self.enemy_group = enemy_group
            self.target_provider = target_provider

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
            self.normal_speed = 5
            self.focused_speed = 2.5

            #弾
            self.fire = False
            self.timer = 0
            self.fire_interval = 7
            self.focused = False

            self.power = 1.00
            self.max_power = 5.00
            self.bomb_requested = False
            self.bomb_ready = True
            self.invulnerability_timer = 0

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
        self.focused = key[pygame.K_LSHIFT] or key[pygame.K_RSHIFT]
        self.speed = self.focused_speed if self.focused else self.normal_speed
        self.fire_interval = 7 if self.power < 2 else 6 if self.power < 4 else 5

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
            self.shoot()

            self.fire = True
            self.shot_sound.play()

        if key[pygame.K_x] and self.bomb_ready and self.power >= 1:
            self.bomb_requested = True
            self.bomb_ready = False
        elif not key[pygame.K_x]:
            self.bomb_ready = True

    def shoot(self):
        if self.focused:
            if self.power < 2:
                offsets = (0,)
            elif self.power < 3:
                offsets = (-6, 6)
            elif self.power < 4:
                offsets = (-12, 0, 12)
            else:
                offsets = (-18, -6, 6, 18)

            for offset in offsets:
                Bullet(
                    self.bullet_group,
                    self.rect.centerx + offset,
                    self.rect.top,
                    speed=11
                )
            return

        if self.power < 2:
            direct_offsets = (0,)
        elif self.power < 3:
            direct_offsets = (-7, 7)
        elif self.power < 4:
            direct_offsets = (-12, 0, 12)
        else:
            direct_offsets = (-18, -6, 6, 18)

        for offset in direct_offsets:
            Bullet(
                self.bullet_group,
                self.rect.centerx + offset,
                self.rect.top,
                speed=10
            )

        homing_offsets = ()
        if self.power >= 3:
            homing_offsets = (-26, 26)
        if self.power >= 5:
            homing_offsets = (-42, -26, 26, 42)

        for offset in homing_offsets:
            Bullet(
                self.bullet_group,
                self.rect.centerx + offset,
                self.rect.top + 4,
                speed=8.5,
                target_provider=self.target_provider,
                homing_targets=self.enemy_group
            )

    def cooldown_bullet(self):
        if self.fire:
            self.timer += 1
        if self.timer >= self.fire_interval:
            self.timer = 0
            self.fire = False

    def add_power(self, value):
        self.power = min(self.max_power, self.power + value)
        self.power = round(self.power * 20) / 20

    def use_bomb(self):
        if not self.bomb_requested:
            return False

        self.bomb_requested = False

        if self.power < 1:
            return False

        self.power = round((self.power - 1) * 20) / 20
        return True

    def start_bomb_invulnerability(self, duration):
        self.invulnerability_timer = duration

    @property
    def invulnerable(self):
        return self.invulnerability_timer > 0

    def update_invulnerability(self):
        if self.invulnerability_timer > 0:
            self.invulnerability_timer -= 1

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
        if self.invulnerable or self.bomb_requested:
            return

        for enemy in self.enemy_group:
            if self.rect.colliderect(enemy.rect) and enemy.alive:
                self.health -= 1

        if self.health <= 0:
            self.alive = False

    def collision_enemy_bullet(self):
        if self.invulnerable or self.bomb_requested:
            return

        for enemy in self.enemy_group:
            for bullet in enemy.enemy_bullet_group:
                if self.rect.colliderect(bullet.rect):
                    bullet.kill()
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

        if self.invulnerable and self.invulnerability_timer % 10 < 5:
            self.image.set_alpha(100)

    def update(self):
        self.update_invulnerability()
        self.input()
        self.move()
        self.update_image()
        self.cooldown_bullet()
        self.collision_enemy()
        self.collision_enemy_bullet()
        self.check_death()

        #グループの描画と更新
        self.bullet_group.draw(self.screen)
        self.bullet_group.update()

    def collision_boss_bullet(self, boss_bullet_group):
        if self.invulnerable or self.bomb_requested:
            return

        for bullet in boss_bullet_group.copy():
            if self.rect.colliderect(bullet.rect):
                bullet.kill()
                self.health -= 1

        if self.health <= 0:
            self.alive = False

