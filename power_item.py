import pygame

from setting import screen_height


class PowerItem(pygame.sprite.Sprite):

    def __init__(self, groups, x, y, value=0.05):
        super().__init__(groups)

        self.value = value
        self.image = self.create_image()
        self.rect = self.image.get_rect(center=(x, y))
        self.position = pygame.math.Vector2(self.rect.center)
        self.fall_speed = 1.4
        self.attraction_radius = 120

    def create_image(self):
        size = 22 if self.value >= 1 else 14
        image = pygame.Surface((size, size), pygame.SRCALPHA)
        color = (255, 85, 85) if self.value < 1 else (255, 205, 70)
        pygame.draw.rect(image, color, (1, 1, size - 2, size - 2), 2)

        font = pygame.font.Font(None, size)
        label = font.render("P", True, color)
        label_rect = label.get_rect(center=(size // 2, size // 2))
        image.blit(label, label_rect)
        return image

    def update(self, player):
        distance = pygame.math.Vector2(player.rect.center) - self.position

        if distance.length_squared() <= self.attraction_radius ** 2:
            if distance.length_squared() > 0:
                self.position += distance.normalize() * 6
        else:
            self.position.y += self.fall_speed

        self.rect.center = round(self.position.x), round(self.position.y)

        if self.rect.colliderect(player.rect):
            player.add_power(self.value)
            self.kill()
        elif self.rect.top > screen_height:
            self.kill()
