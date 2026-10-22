import pygame
from setting import *
from player import Player
from  enemy import Enemy
import random
from support import draw_text
from explosion import Explosion
from enemy_bullet import EnemyBullet
from power_item import PowerItem
import cv2
import math


class Game:

    def __init__(self):
        self.screen = pygame.display.get_surface()

        #グループの作成
        self.create_group()

        #nose
        self.player = Player(
            self.player_group, 300, 500, self.enemy_group,
            self.get_homing_targets
        )

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

        self.ending_script = [
            ("reimu", 3, "reimu", None,
             "Gods sure do come in all shapes and sizes. I wonder if my shrine's god is really any stronger?"),

            ("reimu", 6, "reimu", None,
             "I'd better hurry on ahead"),
        ]

        self.ending_dialogue = False
        self.ending_screen = False
        self.ending_screen_time = 0

        self.dialogue_index = 0
        self.dialogue_active = False

        self.dialogue_index = 0
        self.dialogue_active = False
        self.dialogue_timer = 0
        self.timer = 0
        self.killed_enemies = 0
        self.wave_group_index = 0

        # Fases de la Stage 1
        self.stage_phase = "wave1"

        # Sub-jefe provisional: cuadrado rojo
        self.subboss_active = False
        self.subboss_max_hp = 300
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
        self.boss_max_hp = 500
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
        self.boss_pattern_shot_count = 0
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
        self.power_item_group = pygame.sprite.Group()

    def get_homing_targets(self):
        targets = list(self.enemy_group)

        if self.subboss_active:
            targets.append(self.subboss_rect)

        if self.boss_active:
            targets.append(self.boss_rect)

        return targets

    # def enemy_killed(self):
    #     self.killed_enemies += 1
    #     print("Enemigos derrotados:", self.killed_enemies)
    def enemy_killed(self, position):
        self.killed_enemies += 1
        PowerItem(self.power_item_group, position[0], position[1])

    def create_enemy(self):
        if self.stage_phase not in ("wave1", "wave2"):
            return

        if self.wave_group_index >= 4:
            return

        if len(self.enemy_group) > 0:
            return

        self.timer += 1

        if self.timer < 60:
            return

        formations = self.normal_formations(self.stage_phase)
        formation = formations[self.wave_group_index]

        for x, y, entry_x, entry_y, exit_x, exit_y, delays, bullet_count in formation:
            Enemy(
                self.enemy_group,
                x,
                y,
                self.player.bullet_group,
                self.enemy_killed,
                entry_target=(entry_x, entry_y),
                exit_target=(exit_x, exit_y),
                shot_delays=delays,
                target_provider=lambda: self.player.rect.center,
                bullet_count=bullet_count
            )

        self.wave_group_index += 1
        self.timer = 0

    def normal_formations(self, stage_phase):
        if stage_phase == "wave1":
            left_count = 14
            right_count = 14
            crossing_count = 9
            column_rows = 4
            final_formation = [
                (300, -35 - column_rows * 62, 300, 300, 300, 650, (26,), 1)
            ]
        else:
            left_count = 4
            right_count = 4
            crossing_count = 2
            column_rows = 2
            final_formation = []

        return [
            [
                (-35, -25 - index * 32, 105 + index * 24,
                 100 + index * 14, 640, 205 + index * 24, (22,), 1)
                for index in range(left_count)
            ],
            [
                (635, -25 - index * 32, 495 - index * 24,
                 100 + index * 14, -40, 205 + index * 24, (22,), 1)
                for index in range(right_count)
            ],
            [
                (-35, -35 - index * 48, 170 + index * 28,
                 105 + index * 24, 640, 230 + index * 24, (18, 42), 1)
                for index in range(crossing_count)
            ] + [
                (635, -35 - index * 48, 430 - index * 28,
                 105 + index * 24, -40, 230 + index * 24, (18, 42), 1)
                for index in range(crossing_count)
            ],
            [
                (150 + column * 100, -35 - row * 62,
                 205 + column * 95, 100 + row * 55,
                 85 + column * 150, 650, (26,), 1)
                for row in range(column_rows)
                for column in range(2)
            ] + final_formation,
        ]

    def player_death(self):
        if len(self.player_group) == 0:
            self.game_over = True
            draw_text(self.screen, 'game over', screen_width // 2, screen_height // 2, 75, RED)
            draw_text(self.screen, 'press SPACE KEY to reset', screen_width // 2, screen_height // 2 + 100, 50, RED)
    def reset(self):
        key = pygame.key.get_pressed()
        if self.game_over and key[pygame.K_SPACE]:
            self.player = Player(
                self.player_group, 300, 500, self.enemy_group,
                self.get_homing_targets
            )
            self.enemy_group.empty()
            self.power_item_group.empty()
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

    def draw_power(self):
        bar_width = 140
        bar_height = 10
        power_ratio = self.player.power / self.player.max_power

        pygame.draw.rect(self.screen, (40, 40, 40), (15, 15, bar_width, bar_height))
        pygame.draw.rect(
            self.screen,
            (230, 80, 80),
            (15, 15, int(bar_width * power_ratio), bar_height)
        )

        font = pygame.font.Font(None, 24)
        label = font.render(
            f"POWER {self.player.power:.2f}", True, WHITE
        )
        self.screen.blit(label, (15, 30))

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

        # El segundo patrón comienza cuando pierde la mitad de la vida
        if self.subboss_hp <= self.subboss_max_hp // 2:
            interval = 65
            directions = [-3, -2, -1, 0, 1, 2, 3]
            speed = 3.5
        else:
            interval = 90
            directions = [-2, -1, 0, 1, 2]
            speed = 3

        if self.subboss_shoot_timer >= interval:
            for direction in directions:
                EnemyBullet(
                    self.subboss_bullet_group,
                    self.subboss_rect.centerx,
                    self.subboss_rect.bottom,
                    speed=speed,
                    direction=direction
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

                    PowerItem(
                        self.power_item_group,
                        self.subboss_rect.centerx,
                        self.subboss_rect.centery,
                        value=0.30
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

        # Dirección desde Minoriko hacia Reimu
        dx = self.player.rect.centerx - self.boss_rect.centerx
        dy = self.player.rect.centery - self.boss_rect.bottom
        base_angle = math.atan2(dy, dx)

        # Patrón 1: abanico dirigido
        if self.boss_hp > 300:
            interval = 80

            if self.boss_shoot_timer >= interval:
                offsets = [-0.4, -0.2, 0, 0.2, 0.4]

                for offset in offsets:
                    angle = base_angle + offset
                    speed = 3.5

                    EnemyBullet(
                        self.boss_bullet_group,
                        self.boss_rect.centerx,
                        self.boss_rect.bottom,
                        velocity_x=math.cos(angle) * speed,
                        velocity_y=math.sin(angle) * speed
                    )

                self.boss_shoot_timer = 0

        # Patrón 2: abanicos alternados más amplios
        elif self.boss_hp > 150:
            interval = 65

            if self.boss_shoot_timer >= interval:
                side = 1 if self.boss_pattern_shot_count % 2 == 0 else -1

                for i in range(7):
                    offset = (i - 3) * 0.17 * side
                    angle = base_angle + offset
                    speed = 3.8

                    EnemyBullet(
                        self.boss_bullet_group,
                        self.boss_rect.centerx,
                        self.boss_rect.bottom,
                        velocity_x=math.cos(angle) * speed,
                        velocity_y=math.sin(angle) * speed
                    )

                self.boss_pattern_shot_count += 1
                self.boss_shoot_timer = 0

        # Patrón 3: anillo de proyectiles
        else:
            interval = 55

            if self.boss_shoot_timer >= interval:
                bullet_count = 12
                speed = 2.8

                for i in range(bullet_count):
                    angle = (2 * math.pi * i) / bullet_count

                    EnemyBullet(
                        self.boss_bullet_group,
                        self.boss_rect.centerx,
                        self.boss_rect.centery,
                        velocity_x=math.cos(angle) * speed,
                        velocity_y=math.sin(angle) * speed
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

        script = (
            self.ending_script
            if self.ending_dialogue
            else self.dialogue_script
        )

        speaker, speaker_img, listener, listener_img, message = (
            script[self.dialogue_index]
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

            script = (
                self.ending_script
                if self.ending_dialogue
                else self.dialogue_script
            )

            if self.dialogue_index >= len(script):
                self.dialogue_active = False

                if self.ending_dialogue:
                    self.ending_dialogue = False
                    self.ending_screen = True
                    self.ending_screen_time = pygame.time.get_ticks()
                else:
                    self.boss_active = True

                    pygame.mixer.music.load(self.boss_bgm)
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(0.3)


    def run(self):
        self.scroll_bg()

        if self.ending_screen:
            self.screen.fill((0, 0, 0))

            font = pygame.font.Font(None, 48)
            text = font.render(
                "Girls are now praying", True, WHITE
            )
            rect = text.get_rect(
                center=(screen_width // 2, screen_height // 2)
            )
            self.screen.blit(text, rect)

            if pygame.time.get_ticks() - self.ending_screen_time >= 3000:
                pygame.quit()
                raise SystemExit

            return

        self.create_enemy()

        # Termina la primera oleada: aparece el sub-jefe
        if (self.stage_phase == "wave1"
                and self.wave_group_index >= 4
                and len(self.enemy_group) == 0):
            self.stage_phase = "subboss"
            self.subboss_active = True
            self.subboss_hp = self.subboss_max_hp
            self.subboss_rect.midtop = (screen_width // 2, 80)

        # Termina la segunda oleada: comienza el diálogo de Minoriko
        if (self.stage_phase == "wave2"
                and self.wave_group_index >= 4
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
        self.power_item_group.update(self.player)
        self.power_item_group.draw(self.screen)

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

        if not self.boss_exploded and (
                self.boss_active or self.boss_intro_active or
                (self.dialogue_active and self.boss_intro_done)):

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

        if (
                self.boss_exploded
                and len(self.boss_explosion_group) == 0
                and not self.ending_dialogue
                and not self.ending_screen
                and not self.dialogue_active
        ):
            self.dialogue_index = 0
            self.dialogue_active = True
            self.ending_dialogue = True

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
            self.wave_group_index = 0
            self.timer = 0

        self.draw_power()
        self.dialogue()





