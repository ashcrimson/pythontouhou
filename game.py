import pygame
from setting import *
from player import Player
from  enemy import Enemy
import random
from support import draw_text
from explosion import Explosion
from enemy_bullet import EnemyBullet
import cv2


class Game:

    def __init__(self):
        self.screen = pygame.display.get_surface()

        #グループの作成
        self.create_group()

        #nose
        self.player = Player(self.player_group, 300, 500, self.enemy_group)

        #敵
        self.reimu_portraits = []
        for i in range(8):
            image = pygame.image.load(
                f"assets/img/portrait/reimu/reimu{i}.png"
            ).convert_alpha()
            self.reimu_portraits.append(image)

        self.minoriko_portraits = []
        for i in range(3):
            image = pygame.image.load(
                f"assets/img/portrait/minoriko/minoriko{i}.png"
            ).convert_alpha()
            self.minoriko_portraits.append(image)

        self.dialogue_script = [
            # Reimu aparece sin hablar
            ("reimu", 3, None, None, ""),

            # Minoriko habla antes de mostrar su retrato
            ("minoriko", None, None, None,
             "You are a shrine maiden, yet you'd eat a god."),

            # Aparece el retrato de Minoriko
            ("minoriko", 2, "reimu", 0,
             "How ridiculous! What insolence!"),

            ("reimu", 7, "minoriko", 2,
             "Who said I was going to eat you? That said... is that tasty smell coming from you?"),

            ("minoriko", 0, "reimu", 7,
             "Gods always put a great deal of care into their scent. Oh, yes—I'm the harvest god."),

            ("reimu", 1, "minoriko", 0,
             "Mmmm. So that's why you smell like half-baked sweet potatoes."),

            ("minoriko", 2, "reimu", 1,
             "Freshly-harvested sweet potatoes are my perfume. You think I'd let a shrine maiden eat me?"),
        ]

        self.dialogue_index = 0
        self.dialogue_active = False

        self.dialogue_index = 0
        self.dialogue_active = False
        self.dialogue_timer = 0
        self.timer = 0
        self.killed_enemies = 0

        # Fases de la Stage 1
        self.stage_phase = "wave1"

        # Sub-jefe provisional: cuadrado rojo
        self.subboss_active = False
        self.subboss_max_hp = 100
        self.subboss_hp = self.subboss_max_hp
        self.subboss_rect = pygame.Rect(0, 0, 80, 80)
        self.subboss_rect.midtop = (screen_width // 2, 80)

        # Animación del sub-jefe
        self.subboss_image_list = []

        for i in range(5):
            image = pygame.image.load(
                f"assets/img/sub-boss/sub-boss{i}.png"
            ).convert_alpha()

            image = pygame.transform.scale(image, (80, 80))
            self.subboss_image_list.append(image)

        self.subboss_index = 0
        self.subboss_image = self.subboss_image_list[0]
        self.subboss_animation_speed = 0.05

        # Movimiento
        self.subboss_direction = 2
        self.subboss_move_timer = 0

        # Disparos
        self.subboss_shoot_timer = 0
        self.subboss_bullet_group = pygame.sprite.Group()

        # Efecto de daño
        self.subboss_hit_time = 0
        self.subboss_flash_duration = 80

        # Explosión
        self.subboss_explosion_group = pygame.sprite.Group()
        self.subboss_exploded = False

        self.boss_active = False
        self.boss_max_hp = 100
        self.boss_hp = self.boss_max_hp
        self.boss_hit_time = 0
        self.boss_flash_duration = 80
        self.boss_image_list = []
        for i in range(6):
            image = pygame.image.load(f"assets/img/boss/boss{i}.png")
            image = pygame.transform.scale(image, (80, 80))
            self.boss_image_list.append(image)

        self.boss_index = 0
        self.boss_image = self.boss_image_list[self.boss_index]
        self.boss_rect = self.boss_image.get_rect(
            midtop=(screen_width // 2, 80)
        )
        # Entrada del jefe durante el diálogo
        self.boss_intro_active = False
        self.boss_intro_done = False
        self.boss_intro_speed = 3
        self.boss_intro_target_y = 80
        self.boss_animation_speed = 0.05

        self.boss_direction = 2
        self.boss_move_timer = 0
        self.boss_shoot_timer = 0
        self.boss_bullet_group = pygame.sprite.Group()

        self.boss_explosion_group = pygame.sprite.Group()
        self.boss_exploded = False

        self.boss_explosion_sound = pygame.mixer.Sound(
            'assets/sound/explosion.mp3'
        )
        self.boss_explosion_sound.set_volume(0.2)

        self.boss_damage_sound = pygame.mixer.Sound(
            'assets/sound/damage.mp3'
        )
        self.boss_damage_sound.set_volume(0.4)

        

        self.bg_video = cv2.VideoCapture(
            'assets/video/background.mp4'
        )

        self.bg_video.set(cv2.CAP_PROP_POS_FRAMES, 0)

        self.bg_video_fps = self.bg_video.get(cv2.CAP_PROP_FPS)
        if self.bg_video_fps <= 0:
            self.bg_video_fps = 30

        self.bg_video_timer = 0
        self.bg_video_frame = None
        self.bg_video_surface = None



        #ゲームオーバー判定
        self.game_over = False

        # BGM
        self.normal_bgm = 'assets/sound/bgm.mp3'
        self.boss_bgm = 'assets/sound/boss_bgm.mp3'

        pygame.mixer.music.load(self.normal_bgm)
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
        if self.stage_phase not in ("wave1", "wave2"):
            return

        if self.killed_enemies >= 10:
            return

        self.timer += 1

        if self.timer > 50:
            Enemy(
                self.enemy_group,
                random.randint(50, 550),
                0,
                self.player.bullet_group,
                self.enemy_killed
            )
            self.timer = 0

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
        self.bg_video_timer += 1

        # Controlar la velocidad de reproducción
        frames_per_update = max(1, round(60 / self.bg_video_fps))

        if self.bg_video_timer >= frames_per_update:
            self.bg_video_timer = 0

            success, frame = self.bg_video.read()

            # Volver al inicio al terminar el video
            if not success:
                self.bg_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                success, frame = self.bg_video.read()

            if success:
                frame = cv2.resize(
                    frame,
                    (screen_width, screen_height)
                )

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                self.bg_video_surface = pygame.surfarray.make_surface(
                    frame.swapaxes(0, 1)
                )

        if self.bg_video_surface is not None:
            self.screen.blit(self.bg_video_surface, (0, 0))

    def draw_boss_hp(self):
        bar_width = 120
        bar_height = 10

        x = self.boss_rect.centerx - bar_width // 2
        y = self.boss_rect.top - 20

        pygame.draw.rect(
            self.screen,
            (100, 100, 100),
            (x, y, bar_width, bar_height)
        )

        hp_width = int(bar_width * self.boss_hp / self.boss_max_hp)

        pygame.draw.rect(
            self.screen,
            GREEN,
            (x, y, hp_width, bar_height)
        )

    def subboss_move(self):
        if not self.subboss_active:
            return

        self.subboss_rect.x += self.subboss_direction
        self.subboss_move_timer += 1

        if (self.subboss_rect.left <= 0
                or self.subboss_rect.right >= screen_width):
            self.subboss_direction *= -1

    def subboss_animation(self):
        if not self.subboss_active:
            return

        self.subboss_index += self.subboss_animation_speed

        if self.subboss_index >= len(self.subboss_image_list):
            self.subboss_index = 0

        self.subboss_image = self.subboss_image_list[
            int(self.subboss_index)
        ]

    def subboss_shoot(self):
        if not self.subboss_active:
            return

        self.subboss_shoot_timer += 1

        if self.subboss_shoot_timer >= 100:
            EnemyBullet(
                self.subboss_bullet_group,
                self.subboss_rect.centerx,
                self.subboss_rect.bottom
            )
            self.subboss_shoot_timer = 0

    def subboss_collision(self):
        if not self.subboss_active:
            return

        for bullet in self.player.bullet_group.copy():
            if self.subboss_rect.colliderect(bullet.rect):
                bullet.kill()

                self.boss_damage_sound.play()
                self.subboss_hit_time = pygame.time.get_ticks()

                self.subboss_hp -= 10
                self.subboss_hp = max(0, self.subboss_hp)

                if self.subboss_hp == 0 and not self.subboss_exploded:
                    self.subboss_active = False
                    self.subboss_exploded = True

                    Explosion(
                        self.subboss_explosion_group,
                        self.subboss_rect.centerx,
                        self.subboss_rect.centery
                    )

                    self.boss_explosion_sound.play()
                    break

    def boss_collision(self):
        if not self.boss_active:
            return

        for bullet in self.player.bullet_group.copy():
            if self.boss_rect.colliderect(bullet.rect):
                bullet.kill()
                self.boss_damage_sound.play()
                self.boss_hit_time = pygame.time.get_ticks()
                self.boss_hp -= 10
                self.boss_hp = max(0, self.boss_hp)
                print("Vida del jefe:", self.boss_hp)

                if self.boss_hp == 0 and not self.boss_exploded:
                    self.boss_active = False
                    self.boss_exploded = True

                    Explosion(
                        self.boss_explosion_group,
                        self.boss_rect.centerx,
                        self.boss_rect.centery
                    )

                    self.boss_explosion_sound.play()
                    break

    def boss_intro(self):
        # Comienza cuando Minoriko dice "eat a god"
        if (self.dialogue_active
                and self.dialogue_index == 1
                and not self.boss_intro_done
                and not self.boss_intro_active):
            self.boss_intro_active = True
            self.boss_rect.top = -self.boss_rect.height

        if not self.boss_intro_active:
            return

        self.boss_rect.y += self.boss_intro_speed

        if self.boss_rect.y >= self.boss_intro_target_y:
            self.boss_rect.y = self.boss_intro_target_y
            self.boss_intro_active = False
            self.boss_intro_done = True
    def boss_move(self):
        if not self.boss_active:
            return

        self.boss_rect.x += self.boss_direction
        self.boss_move_timer += 1

        if self.boss_rect.left <= 0 or self.boss_rect.right >= screen_width:
            self.boss_direction *= -1

    def boss_shoot(self):
        if not self.boss_active:
            return

        self.boss_shoot_timer += 1

        if self.boss_shoot_timer >= 100:
            EnemyBullet(
                self.boss_bullet_group,
                self.boss_rect.centerx,
                self.boss_rect.bottom
            )
            self.boss_shoot_timer = 0

    def boss_animation(self):
        if not self.boss_active:
            return

        self.boss_index += self.boss_animation_speed

        if self.boss_index >= len(self.boss_image_list):
            self.boss_index = 0

        self.boss_image = self.boss_image_list[int(self.boss_index)]

    def dialogue(self):
        if not self.dialogue_active:
            return

        speaker, speaker_img, listener, listener_img, message = (
            self.dialogue_script[self.dialogue_index]
        )

        # Retratos
        if speaker == "reimu" and speaker_img is not None:
            reimu = self.reimu_portraits[speaker_img]
            reimu = pygame.transform.scale(reimu, (220, 320))

            if listener != "reimu":
                reimu = reimu.copy()
                reimu.fill(
                    (100, 100, 100, 255),
                    special_flags=pygame.BLEND_RGBA_MULT
                )

            self.screen.blit(reimu, (20, screen_height - 350))

        if speaker == "minoriko" and speaker_img is not None:
            minoriko = self.minoriko_portraits[speaker_img]
            minoriko = pygame.transform.scale(minoriko, (220, 320))
            self.screen.blit(minoriko, (screen_width - 240, screen_height - 350))

        # Caja de diálogo
        box = pygame.Surface((screen_width - 40, 100), pygame.SRCALPHA)
        box.fill((0, 0, 0, 200))
        self.screen.blit(box, (20, screen_height - 120))

        font = pygame.font.Font(None, 30)
        name = "Reimu" if speaker == "reimu" else "Minoriko"

        name_text = font.render(name, True, (255, 220, 150))
        self.screen.blit(name_text, (40, screen_height - 110))

        # Saltos de línea automáticos
        max_width = screen_width - 80
        words = message.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()

            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        # Dibujar cada línea del diálogo
        for i, line in enumerate(lines):
            message_text = font.render(line, True, WHITE)
            self.screen.blit(
                message_text,
                (40, screen_height - 75 + i * 30)
            )

    def dialogue_input(self, event):
        if not self.dialogue_active:
            return

        if event.key in (pygame.K_z, pygame.K_RETURN):
            self.dialogue_index += 1

            if self.dialogue_index >= len(self.dialogue_script):
                self.dialogue_active = False
                self.boss_active = True

                pygame.mixer.music.load(self.boss_bgm)
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.3)

    def run(self):
        self.scroll_bg()

        self.create_enemy()

        # Termina la primera oleada: aparece el sub-jefe
        if (self.stage_phase == "wave1"
                and self.killed_enemies >= 10
                and len(self.enemy_group) == 0):
            self.stage_phase = "subboss"
            self.subboss_active = True
            self.subboss_hp = self.subboss_max_hp
            self.subboss_rect.midtop = (screen_width // 2, 80)

        # Termina la segunda oleada: comienza el diálogo de Minoriko
        if (self.stage_phase == "wave2"
                and self.killed_enemies >= 10
                and len(self.enemy_group) == 0):
            self.stage_phase = "minoriko"
            self.dialogue_index = 0
            self.dialogue_active = True

        self.player_death()

        self.reset()

        self.boss_intro()

        self.subboss_collision()
        self.subboss_move()
        self.subboss_shoot()

        self.boss_collision()
        self.boss_move()
        self.boss_shoot()

        #グループの描画と更新
        if self.dialogue_active:
            self.player.rect.midbottom = (
                screen_width // 2,
                screen_height - 20
            )
            self.player.bullet_group.empty()
            self.player_group.draw(self.screen)
        else:
            self.player_group.draw(self.screen)
            self.player_group.update()
        self.player.collision_boss_bullet(self.boss_bullet_group)
        self.player.collision_boss_bullet(self.subboss_bullet_group)
        self.enemy_group.draw(self.screen)
        self.enemy_group.update()

        # Dibujar el sub-jefe animado
        if self.subboss_active:
            self.subboss_animation()

            subboss_image = self.subboss_image

            # Parpadeo blanco al recibir daño
            if (pygame.time.get_ticks() - self.subboss_hit_time
                    < self.subboss_flash_duration):
                subboss_image = subboss_image.copy()
                subboss_image.fill(
                    (255, 255, 255),
                    special_flags=pygame.BLEND_RGB_ADD
                )

            self.screen.blit(subboss_image, self.subboss_rect)

            # Barra de vida
            bar_width = 120
            bar_height = 10
            x = self.subboss_rect.centerx - bar_width // 2
            y = self.subboss_rect.top - 20

            pygame.draw.rect(
                self.screen,
                (100, 100, 100),
                (x, y, bar_width, bar_height)
            )

            hp_width = int(
                bar_width * self.subboss_hp / self.subboss_max_hp
            )

            pygame.draw.rect(
                self.screen,
                GREEN,
                (x, y, hp_width, bar_height)
            )

        if self.boss_active or self.boss_intro_active or (
                self.dialogue_active and self.boss_intro_done):

            self.boss_animation()
            boss_image = self.boss_image

            if pygame.time.get_ticks() - self.boss_hit_time < self.boss_flash_duration:
                boss_image = boss_image.copy()
                boss_image.fill(
                    (255, 255, 255),
                    special_flags=pygame.BLEND_RGB_ADD
                )

            self.screen.blit(boss_image, self.boss_rect)

            if self.boss_active:
                self.draw_boss_hp()

        self.boss_explosion_group.draw(self.screen)
        self.boss_explosion_group.update()

        self.subboss_explosion_group.draw(self.screen)
        self.subboss_explosion_group.update()

        self.boss_bullet_group.draw(self.screen)
        self.boss_bullet_group.update()

        self.subboss_bullet_group.draw(self.screen)
        self.subboss_bullet_group.update()

        # La segunda oleada comienza tras terminar la explosión
        if (self.subboss_exploded
                and len(self.subboss_explosion_group) == 0
                and self.stage_phase == "subboss"):
            self.stage_phase = "wave2"
            self.killed_enemies = 0
            self.timer = 0

        self.dialogue()





