from __future__ import annotations

import sys

import pygame

from config import COLORS, FPS, HEIGHT, MAP_X, MAP_Y, PANEL_W, PANEL_X, TILE, WIDTH
from data.maps import LAB_MAP, START_POS, grid_to_screen, is_walkable
from ui.drawing import draw_center, draw_text, wrap_text

pygame.init()

FONT = pygame.font.SysFont("segoeui", 18)
FONT_SM = pygame.font.SysFont("segoeui", 15)
FONT_MD = pygame.font.SysFont("segoeui", 24, bold=True)
FONT_LG = pygame.font.SysFont("segoeui", 34, bold=True)


class Button:
    def __init__(self, rect, label, action):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.action = action

    def draw(self, surface, mouse):
        hover = self.rect.collidepoint(mouse)
        fill = (50, 64, 85) if hover else COLORS["panel_2"]
        pygame.draw.rect(surface, (8, 11, 17), self.rect.move(0, 4), border_radius=10)
        pygame.draw.rect(surface, fill, self.rect, border_radius=10)
        pygame.draw.rect(surface, COLORS["cyan"], self.rect, 2, border_radius=10)
        draw_center(surface, self.label, FONT_MD, COLORS["text"], self.rect)

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.action()
                return True
        return False


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("DoAnAI - Sci-fi Grid Prototype")
        self.clock = pygame.time.Clock()
        self.robot = START_POS[:]
        self.facing = "down"
        self.message = "Dung phim mui ten hoac cac nut de di chuyen robot."
        self.buttons = []
        self.make_buttons()

    def make_buttons(self):
        cx = PANEL_X + PANEL_W // 2
        cy = 435
        size = 60
        gap = 12
        self.buttons = [
            Button((cx - size // 2, cy - size - gap, size, size), "UP", lambda: self.move(-1, 0)),
            Button((cx - size // 2, cy + size + gap, size, size), "DN", lambda: self.move(1, 0)),
            Button((cx - size - gap - size // 2, cy, size, size), "LT", lambda: self.move(0, -1)),
            Button((cx + gap + size // 2, cy, size, size), "RT", lambda: self.move(0, 1)),
        ]

    def move(self, dr, dc):
        if dr < 0:
            self.facing = "up"
        elif dr > 0:
            self.facing = "down"
        elif dc < 0:
            self.facing = "left"
        elif dc > 0:
            self.facing = "right"

        nr = self.robot[0] + dr
        nc = self.robot[1] + dc
        if is_walkable(nr, nc):
            self.robot = [nr, nc]
            self.message = f"Robot di chuyen toi o ({nr}, {nc})."
        else:
            self.message = "Khong the di vao tuong hoac vung trong."

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.move(-1, 0)
                elif event.key == pygame.K_DOWN:
                    self.move(1, 0)
                elif event.key == pygame.K_LEFT:
                    self.move(0, -1)
                elif event.key == pygame.K_RIGHT:
                    self.move(0, 1)
                elif event.key == pygame.K_r:
                    self.robot = START_POS[:]
                    self.facing = "down"
                    self.message = "Da reset robot ve vi tri ban dau."
            for button in self.buttons:
                if button.handle(event):
                    break

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            self.draw()
            pygame.display.flip()

    def draw(self):
        self.screen.fill(COLORS["bg"])
        self.draw_background_pattern()
        self.draw_title()
        self.draw_map()
        self.draw_robot()
        self.draw_panel()

    def draw_background_pattern(self):
        for x in range(0, WIDTH, 70):
            pygame.draw.line(self.screen, (15, 18, 25), (x, 0), (x + 120, HEIGHT), 2)
        for y in range(0, HEIGHT, 70):
            pygame.draw.line(self.screen, (12, 15, 21), (0, y), (WIDTH, y), 1)

    def draw_title(self):
        draw_text(self.screen, "DoAnAI Lab Map", FONT_LG, COLORS["text"], (54, 28))
        draw_text(self.screen, "Map ma tran rong hon, giao dien gon hon, dieu khien robot thu cong", FONT, COLORS["muted"], (56, 66))

    def draw_map(self):
        rows = len(LAB_MAP)
        cols = len(LAB_MAP[0])
        outer = pygame.Rect(MAP_X - 14, MAP_Y - 14, cols * TILE + 28, rows * TILE + 28)
        pygame.draw.rect(self.screen, (2, 3, 6), outer.move(0, 8), border_radius=6)
        pygame.draw.rect(self.screen, (26, 31, 43), outer, border_radius=6)
        pygame.draw.rect(self.screen, (85, 96, 116), outer, 2, border_radius=6)

        for r, row in enumerate(LAB_MAP):
            for c, tile in enumerate(row):
                if tile == ".":
                    continue
                rect = pygame.Rect(*grid_to_screen(r, c), TILE, TILE)
                self.draw_tile(rect, tile)

    def draw_tile(self, rect, tile):
        if tile == "W":
            self.draw_wall(rect)
        elif tile == "X":
            self.draw_bridge(rect)
        elif tile == "D":
            self.draw_door(rect)
        else:
            self.draw_floor(rect)

        pygame.draw.rect(self.screen, (13, 18, 28), rect, 1)
        for px, py in [
            (rect.x + 5, rect.y + 5),
            (rect.right - 8, rect.y + 5),
            (rect.x + 5, rect.bottom - 8),
            (rect.right - 8, rect.bottom - 8),
        ]:
            pygame.draw.circle(self.screen, (28, 38, 51), (px, py), 2)

    def draw_floor(self, rect):
        pygame.draw.rect(self.screen, COLORS["floor"], rect)
        pygame.draw.rect(self.screen, COLORS["floor_light"], (rect.x + 5, rect.y + 5, rect.w - 10, rect.h - 10), 1)
        pygame.draw.line(self.screen, (130, 150, 170), (rect.x + 8, rect.y + 10), (rect.right - 8, rect.bottom - 10), 1)

    def draw_wall(self, rect):
        pygame.draw.rect(self.screen, COLORS["wall"], rect)
        pygame.draw.rect(self.screen, COLORS["wall_edge"], (rect.x + 4, rect.y + 4, rect.w - 8, rect.h - 8), 2)
        y = rect.y + 9
        while y < rect.bottom - 6:
            pygame.draw.line(self.screen, (64, 72, 94), (rect.x + 5, y), (rect.right - 5, y), 2)
            y += 12
        self.draw_hazard_strip(rect.x + 3, rect.bottom - 12, rect.w - 6, 7)

    def draw_bridge(self, rect):
        pygame.draw.rect(self.screen, COLORS["bridge"], rect)
        pygame.draw.rect(self.screen, COLORS["bridge_edge"], (rect.x + 5, rect.y + 5, rect.w - 10, rect.h - 10), 3)
        pygame.draw.line(self.screen, COLORS["bridge_edge"], (rect.x + 10, rect.y + 10), (rect.right - 10, rect.bottom - 10), 4)
        pygame.draw.line(self.screen, COLORS["bridge_edge"], (rect.right - 10, rect.y + 10), (rect.x + 10, rect.bottom - 10), 4)

    def draw_door(self, rect):
        pygame.draw.rect(self.screen, COLORS["wall"], rect)
        door = pygame.Rect(rect.x + 9, rect.y + 6, rect.w - 18, rect.h - 12)
        pygame.draw.rect(self.screen, COLORS["door"], door)
        pygame.draw.rect(self.screen, (82, 88, 91), door, 3)
        pygame.draw.line(self.screen, (230, 230, 220), (door.centerx, door.y + 5), (door.centerx, door.bottom - 5), 2)
        pygame.draw.circle(self.screen, COLORS["green"], (door.right - 7, door.centery), 3)

    def draw_hazard_strip(self, x, y, w, h):
        pygame.draw.rect(self.screen, COLORS["hazard_black"], (x, y, w, h))
        for sx in range(x - h, x + w, 11):
            pygame.draw.polygon(
                self.screen,
                COLORS["hazard_yellow"],
                [(sx, y + h), (sx + 6, y + h), (sx + h + 6, y), (sx + h, y)],
            )

    def draw_robot(self):
        row, col = self.robot
        x, y = grid_to_screen(row, col)
        cx, cy = x + TILE // 2, y + TILE // 2
        scale = 1.22
        outline = (5, 8, 14)
        metal = (212, 225, 231)
        metal_dark = (126, 145, 155)
        accent = COLORS["cyan"]
        eye = (167, 245, 255)

        def p(value):
            return int(round(value * scale))

        def pos(px, py):
            return int(round(cx + px * scale)), int(round(cy + py * scale))

        def rect(px, py, w, h, color):
            pygame.draw.rect(
                self.screen,
                color,
                (int(round(cx + px * scale)), int(round(cy + py * scale)), max(1, p(w)), max(1, p(h))),
            )

        def joint(px, py, color=metal):
            pygame.draw.circle(self.screen, outline, pos(px, py), p(4))
            pygame.draw.circle(self.screen, color, pos(px, py), p(3))

        pygame.draw.ellipse(self.screen, (3, 5, 9), (cx - p(17), cy + p(14), p(34), p(9)))

        rect(-9, 7, 5, 9, outline)
        rect(4, 7, 5, 9, outline)
        rect(-8, 8, 3, 7, metal_dark)
        rect(5, 8, 3, 7, metal_dark)
        rect(-12, 16, 8, 4, outline)
        rect(4, 16, 8, 4, outline)
        rect(-11, 16, 6, 2, accent)
        rect(5, 16, 6, 2, accent)

        left_arm = -16 if self.facing != "left" else -18
        right_arm = 13 if self.facing != "right" else 15
        pygame.draw.line(self.screen, outline, pos(-12, -3), pos(left_arm, 8), p(4))
        pygame.draw.line(self.screen, outline, pos(12, -3), pos(right_arm, 8), p(4))
        pygame.draw.line(self.screen, accent, pos(-12, -3), pos(left_arm, 8), p(2))
        pygame.draw.line(self.screen, accent, pos(12, -3), pos(right_arm, 8), p(2))
        joint(left_arm // 2, 4, accent)
        joint(right_arm // 2, 4, accent)

        rect(-10, -2, 20, 12, outline)
        rect(-8, 0, 16, 8, metal)
        rect(-5, 1, 10, 3, accent)
        rect(-3, 5, 6, 2, metal_dark)

        rect(-3, -6, 6, 4, outline)
        rect(-2, -6, 4, 3, metal_dark)

        rect(-13, -20, 26, 16, outline)
        rect(-11, -18, 22, 12, (25, 36, 50))
        rect(-16, -15, 3, 8, outline)
        rect(13, -15, 3, 8, outline)
        rect(-16, -13, 2, 4, accent)
        rect(14, -13, 2, 4, accent)

        if self.facing == "left":
            eye_shift = -2
        elif self.facing == "right":
            eye_shift = 2
        else:
            eye_shift = 0
        rect(-6 + eye_shift, -13, 3, 4, eye)
        rect(4 + eye_shift, -13, 3, 4, eye)
        rect(-5 + eye_shift, -8, 10, 1, accent)

    def draw_panel(self):
        panel = pygame.Rect(PANEL_X, 92, PANEL_W, 630)
        pygame.draw.rect(self.screen, (7, 10, 16), panel.move(0, 6), border_radius=14)
        pygame.draw.rect(self.screen, COLORS["panel"], panel, border_radius=14)
        pygame.draw.rect(self.screen, (80, 95, 120), panel, 2, border_radius=14)
        draw_text(self.screen, "Dieu khien", FONT_MD, COLORS["text"], (panel.x + 24, panel.y + 26))
        draw_text(self.screen, "Robot", FONT, COLORS["muted"], (panel.x + 24, panel.y + 60))

        info = [
            f"Vi tri: ({self.robot[0]}, {self.robot[1]})",
            "O di duoc: san, cau, cua",
            "Chan: tuong, vung trong",
            "Phim: mui ten, R de reset",
        ]
        y = panel.y + 105
        for line in info:
            draw_text(self.screen, line, FONT_SM, COLORS["text"], (panel.x + 24, y))
            y += 28

        mouse = pygame.mouse.get_pos()
        for button in self.buttons:
            button.draw(self.screen, mouse)

        log_box = pygame.Rect(panel.x + 24, panel.bottom - 122, panel.w - 48, 82)
        pygame.draw.rect(self.screen, COLORS["panel_2"], log_box, border_radius=10)
        pygame.draw.rect(self.screen, (80, 95, 120), log_box, 1, border_radius=10)
        for i, line in enumerate(wrap_text(self.message, FONT_SM, log_box.w - 20)[:3]):
            draw_text(self.screen, line, FONT_SM, COLORS["text"], (log_box.x + 10, log_box.y + 10 + i * 21))
