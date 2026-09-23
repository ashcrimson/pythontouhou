import pygame

def draw_text(screen, txt, x, y, size, color):
    font = pygame.font.SysFont(None, size)
    surface = font.render(txt, True, color)
    x = x - surface.get_width() / 2
    y = y - surface.get_height() / 2
    screen.blit(surface, (x, y))