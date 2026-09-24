import pygame

from setting import *
from player import Player
from  enemy import Enemy
import random
from support import draw_text



class Game:

    def __init__(self):
        self.screen = pygame.display.get_surface()

        #グループの作成
        self.create_group()

        #nose
        self.player = Player(self.player_group, 300, 500, self.enemy_group)

        #敵
        self.timer = 0

        #背景
        self.pre_bg_img = pygame.image.load('assets/img/background/background0.png')
        self.bg_img = pygame.transform.scale(self.pre_bg_img, (screen_width, screen_height))
        self.bg_y = 0
        self.scroll_speed = 0.5

        self.middle_bg_img = pygame.image.load(
            'assets/img/background/background1.png'
        ).convert_alpha()

        self.middle_bg_img = pygame.transform.scale(
            self.middle_bg_img,
            (screen_width, screen_height)
        )

        self.middle_bg_y = 0
        self.middle_bg_speed = 1

        self.cloud_img = pygame.image.load(
            'assets/img/background/background2.png'
        ).convert_alpha()

        self.clouds = []

        for i in range(6):
            x = random.randint(0, screen_width - self.cloud_img.get_width())
            y = random.randint(0, screen_height)
            self.clouds.append([x, y])

        self.cloud_speed = 1



        #ゲームオーバー判定
        self.game_over = False

        #BGM
        pygame.mixer.music.load('assets/sound/bgm.mp3')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.3)

    def create_group(self):
        self.player_group = pygame.sprite.GroupSingle()
        self.enemy_group = pygame.sprite.Group()

    # def enemy_killed(self):
    #     self.killed_enemies += 1
    #     print("Enemigos derrotados:", self.killed_enemies)
    def enemy_killed(self):
        self.killed_enemies += 1
        print("Game:", id(self), "| Enemigos derrotados:", self.killed_enemies)

    def create_enemy(self):
        self.timer += 1
        if self.timer > 50:
            enemy = Enemy(
                self.enemy_group,
                random.randint(50, 550),
                0,
                self.player.bullet_group,
                self.enemy_killed
            )
            self.timer = 0
            self.killed_enemies = 0

    def player_death(self):
        if len(self.player_group) == 0:
            self.game_over = True
            draw_text(self.screen, 'game over', screen_width // 2, screen_height // 2, 75, RED)
            draw_text(self.screen, 'press SPACE KEY to reset', screen_width // 2, screen_height // 2 + 100, 50, RED)
    def reset(self):
        key = pygame.key.get_pressed()
        if self.game_over and key[pygame.K_SPACE]:
            self.player = Player(self.player_group, 300, 500, self.enemy_group)
            self.enemy_group.empty()
            self.game_over = False

    def scroll_bg(self):
        self.bg_y = (self.bg_y + self.scroll_speed) % screen_height

        # Suelo rocoso
        self.screen.blit(
            self.bg_img,
            (0, self.bg_y - screen_height)
        )
        self.screen.blit(
            self.bg_img,
            (0, self.bg_y)
        )

        # Malla
        self.middle_bg_y = (
                                   self.middle_bg_y + self.middle_bg_speed
                           ) % screen_height

        self.screen.blit(
            self.middle_bg_img,
            (0, self.middle_bg_y - screen_height)
        )
        self.screen.blit(
            self.middle_bg_img,
            (0, self.middle_bg_y)
        )

        # Niebla / nubes
        for cloud in self.clouds:
            cloud[1] += self.cloud_speed

            if cloud[1] > screen_height:
                cloud[1] = -self.cloud_img.get_height()
                cloud[0] = random.randint(
                    0,
                    screen_width - self.cloud_img.get_width()
                )

            self.screen.blit(self.cloud_img, cloud)

    def run(self):
        self.scroll_bg()

        self.create_enemy()

        self.player_death()

        self.reset()

        #グループの描画と更新
        self.player_group.draw(self.screen)
        self.player_group.update()
        self.enemy_group.draw(self.screen)
        self.enemy_group.update()


