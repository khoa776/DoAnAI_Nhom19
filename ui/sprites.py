import pygame

from ui.drawing import draw_center, draw_text


def battery_color(percent, colors):
    if percent > 0.45:
        return colors["green"]
    if percent > 0.2:
        return colors["hazard_yellow"]
    return (230, 78, 86)


def draw_battery_bar(surface, x, y, w, h, current, maximum, colors, font=None):
    percent = 0
    if maximum > 0:
        percent = max(0, min(1, current / maximum))

    body = pygame.Rect(x, y, w, h)
    cap = pygame.Rect(body.right + 3, body.y + h // 4, 6, h // 2)
    fill_w = int((w - 8) * percent)
    fill = pygame.Rect(body.x + 4, body.y + 4, fill_w, h - 8)

    pygame.draw.rect(surface, (8, 12, 18), body, border_radius=5)
    pygame.draw.rect(surface, colors["muted"], body, 2, border_radius=5)
    pygame.draw.rect(surface, colors["muted"], cap, border_radius=2)
    pygame.draw.rect(surface, battery_color(percent, colors), fill, border_radius=3)

    if font:
        label = f"{current}/{maximum}"
        draw_center(surface, label, font, colors["text"], body)


def draw_small_battery(surface, rect, current, maximum, colors):
    x = rect.x + 8
    y = rect.y + 5
    draw_battery_bar(surface, x, y, rect.w - 20, 9, current, maximum, colors)


def draw_charger(surface, rect, label, colors, font=None):
    pad = rect.inflate(-12, -12)
    inner = pad.inflate(-8, -8)
    port = pygame.Rect(rect.centerx - 12, rect.centery - 8, 24, 16)
    cap = pygame.Rect(port.right + 2, port.y + 4, 4, 8)

    pygame.draw.rect(surface, (18, 27, 31), pad, border_radius=8)
    pygame.draw.rect(surface, colors["green"], pad, 2, border_radius=8)
    pygame.draw.rect(surface, (24, 41, 36), inner, border_radius=6)

    pygame.draw.rect(surface, (5, 10, 12), port, border_radius=4)
    pygame.draw.rect(surface, colors["green"], port, 2, border_radius=4)
    pygame.draw.rect(surface, colors["green"], (port.x + 5, port.y + 5, 14, 6), border_radius=2)
    pygame.draw.rect(surface, colors["green"], cap, border_radius=2)

    pygame.draw.line(surface, colors["cyan"], (rect.centerx - 7, rect.centery + 13), (rect.centerx + 7, rect.centery + 13), 3)
    pygame.draw.circle(surface, colors["cyan"], (rect.centerx, rect.centery + 13), 3)

    if font:
        text_rect = pygame.Rect(rect.x, rect.bottom - 18, rect.w, 14)
        draw_center(surface, label, font, colors["text"], text_rect)
