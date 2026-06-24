from __future__ import annotations

import sys

import pygame

from config import COLORS, FPS, HEIGHT, MAP_X, MAP_Y, PANEL_W, PANEL_X, TILE, WIDTH
from data.maps import BATTERY_MAX, CHARGERS, DELIVERY_POINTS, LAB_MAP, LASER_LINES, START_POS, grid_to_screen, is_charger, is_walkable
from ui.drawing import draw_center, draw_text, wrap_text
from ui.sprites import draw_battery_bar, draw_charger

pygame.init()

FONT = pygame.font.SysFont("segoeui", 18)
FONT_SM = pygame.font.SysFont("segoeui", 15)
FONT_BADGE = pygame.font.SysFont("segoeui", 14, bold=True)
FONT_MD = pygame.font.SysFont("segoeui", 24, bold=True)
FONT_LG = pygame.font.SysFont("segoeui", 34, bold=True)


class Button:
    def __init__(self, rect, label, action, font=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.action = action
        self.font = font

    def draw(self, surface, mouse, selected=False, enabled=True):
        hover = self.rect.collidepoint(mouse)
        if selected:
            fill = (31, 111, 135)
            border = COLORS["green"]
        elif not enabled:
            fill = (26, 31, 42)
            border = (65, 76, 96)
        else:
            fill = (50, 64, 85) if hover else COLORS["panel_2"]
            border = COLORS["cyan"]
        font = self.font if self.font else FONT_MD
        pygame.draw.rect(surface, (8, 11, 17), self.rect.move(0, 4), border_radius=10)
        pygame.draw.rect(surface, fill, self.rect, border_radius=10)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=10)
        color = COLORS["text"] if enabled else COLORS["muted"]
        draw_center(surface, self.label, font, color, self.rect)

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
        self.battery = BATTERY_MAX
        self.algorithm = "BFS"
        self.path = [tuple(START_POS)]
        self.message = "Dung phim mui ten de di chuyen robot."
        self.buttons = []
        self.make_buttons()

    def make_buttons(self):
        left = PANEL_X + 24
        top = 244
        bw = 118
        bh = 36
        gap = 10
        algorithms = ["BFS", "DFS", "IDS", "UCS"]
        self.algo_buttons = []
        self.buttons = [
            Button((left, 344, 118, 38), "RESET", self.reset_game, FONT),
            Button((left + 128, 344, 118, 38), "QUA MAN", self.next_stage, FONT),
        ]
        for i, name in enumerate(algorithms):
            x = left + (i % 2) * (bw + gap)
            y = top + (i // 2) * (bh + gap)
            button = Button((x, y, bw, bh), name, lambda n=name: self.select_algorithm(n), FONT)
            self.algo_buttons.append(button)
            self.buttons.append(button)

    def reset_game(self):
        self.robot = START_POS[:]
        self.facing = "down"
        self.battery = BATTERY_MAX
        self.path = [tuple(START_POS)]
        self.message = "Da reset man choi ve trang thai ban dau."

    def select_algorithm(self, name):
        self.algorithm = name
        self.message = f"Da chon thuat toan {name}. Phan xu ly se them sau."

    def next_stage(self):
        self.message = "Nut qua man dang de san, se gan chuc nang sau."

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
        if self.battery <= 0:
            self.message = "Robot da het pin, can den tram sac."
            return

        if is_walkable(nr, nc):
            self.robot = [nr, nc]
            self.path.append((nr, nc))
            self.battery = max(0, self.battery - 1)
            if is_charger(nr, nc):
                self.battery = BATTERY_MAX
                self.message = f"Robot den tram sac ({nr}, {nc}) va sac day pin."
            else:
                self.message = f"Robot di chuyen toi o ({nr}, {nc}), ton 1 pin."
        else:
            self.message = "Khong the di vao tuong, hop, ho, laser hoac vung trong."

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
                    self.reset_game()
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
        self.draw_stars()

    def draw_stars(self):
        stars = [
            (1018, 58, 2),
            (1228, 44, 1),
            (1320, 760, 2),
            (1008, 715, 1),
            (90, 748, 1),
            (344, 744, 2),
            (930, 710, 1),
            (1360, 238, 1),
        ]
        for x, y, size in stars:
            color = (214, 234, 255) if size == 2 else (128, 158, 190)
            pygame.draw.circle(self.screen, color, (x, y), size)
            if size == 2:
                pygame.draw.line(self.screen, color, (x - 4, y), (x + 4, y), 1)
                pygame.draw.line(self.screen, color, (x, y - 4), (x, y + 4), 1)

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

        for start, end in LASER_LINES:
            self.draw_laser(start, end)

        for index, (r, c) in enumerate(CHARGERS, start=1):
            rect = pygame.Rect(*grid_to_screen(r, c), TILE, TILE)
            draw_charger(self.screen, rect, f"C{index}", COLORS, FONT_SM)

        for label, (r, c), kind in DELIVERY_POINTS:
            rect = pygame.Rect(*grid_to_screen(r, c), TILE, TILE)
            self.draw_delivery_point(rect, label, kind)

    def draw_tile(self, rect, tile):
        if tile == "W":
            self.draw_wall(rect)
        elif tile == "X":
            self.draw_obstacle(rect)
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

    def draw_obstacle(self, rect):
        shadow = rect.move(0, 3)
        pygame.draw.rect(self.screen, (8, 11, 18), shadow)
        pygame.draw.rect(self.screen, COLORS["bridge"], rect)
        pygame.draw.rect(self.screen, COLORS["bridge_edge"], (rect.x + 5, rect.y + 5, rect.w - 10, rect.h - 10), 3)
        pygame.draw.line(self.screen, COLORS["bridge_edge"], (rect.x + 10, rect.y + 10), (rect.right - 10, rect.bottom - 10), 4)
        pygame.draw.line(self.screen, COLORS["bridge_edge"], (rect.right - 10, rect.y + 10), (rect.x + 10, rect.bottom - 10), 4)
        pygame.draw.rect(self.screen, (42, 50, 66), (rect.x + 9, rect.y + 9, rect.w - 18, rect.h - 18), 1)

    def draw_delivery_point(self, rect, label, kind):
        pad = rect.inflate(-10, -10)
        pygame.draw.rect(self.screen, (22, 27, 35), pad, border_radius=8)

        if kind == "medicine":
            color = (245, 92, 116)
            pygame.draw.rect(self.screen, (245, 245, 235), (rect.centerx - 8, rect.centery - 12, 16, 24), border_radius=4)
            pygame.draw.rect(self.screen, color, (rect.centerx - 8, rect.centery - 2, 16, 8))
            pygame.draw.rect(self.screen, (70, 82, 96), (rect.centerx - 6, rect.centery - 16, 12, 5), border_radius=2)
            pygame.draw.line(self.screen, color, (rect.centerx - 5, rect.centery + 2), (rect.centerx + 5, rect.centery + 2), 2)
            pygame.draw.line(self.screen, color, (rect.centerx, rect.centery - 3), (rect.centerx, rect.centery + 7), 2)
        elif kind == "computer":
            color = (98, 207, 255)
            screen = pygame.Rect(rect.centerx - 13, rect.centery - 13, 26, 17)
            pygame.draw.rect(self.screen, (13, 19, 28), screen, border_radius=3)
            pygame.draw.rect(self.screen, color, screen, 2, border_radius=3)
            pygame.draw.rect(self.screen, (33, 88, 112), screen.inflate(-7, -7))
            pygame.draw.rect(self.screen, color, (rect.centerx - 5, rect.centery + 5, 10, 3), border_radius=1)
            pygame.draw.rect(self.screen, color, (rect.centerx - 10, rect.centery + 9, 20, 3), border_radius=1)
        elif kind == "bolt":
            color = (238, 202, 98)
            pygame.draw.circle(self.screen, color, rect.center, 12)
            pygame.draw.circle(self.screen, (39, 43, 50), rect.center, 6)
            for dx, dy in [(-12, 0), (12, 0), (0, -12), (0, 12), (-8, -8), (8, -8), (-8, 8), (8, 8)]:
                pygame.draw.circle(self.screen, color, (rect.centerx + dx, rect.centery + dy), 3)
            pygame.draw.circle(self.screen, (255, 238, 150), rect.center, 2)
        else:
            color = (178, 123, 255)
            points = [
                (rect.centerx, rect.centery - 14),
                (rect.centerx + 12, rect.centery - 5),
                (rect.centerx + 8, rect.centery + 12),
                (rect.centerx - 8, rect.centery + 12),
                (rect.centerx - 12, rect.centery - 5),
            ]
            pygame.draw.polygon(self.screen, (45, 31, 72), points)
            pygame.draw.polygon(self.screen, color, points, 2)
            pygame.draw.circle(self.screen, (214, 190, 255), rect.center, 5)

        pygame.draw.rect(self.screen, color, pad, 2, border_radius=8)
        badge = pygame.Rect(rect.right - 21, rect.y + 5, 16, 16)
        pygame.draw.rect(self.screen, (6, 10, 16), badge, border_radius=4)
        pygame.draw.rect(self.screen, color, badge, 2, border_radius=4)
        draw_center(self.screen, label, FONT_BADGE, COLORS["text"], badge)

    def draw_laser(self, start, end):
        r1, c1 = start
        r2, c2 = end
        x1, y1 = grid_to_screen(r1, c1)
        x2, y2 = grid_to_screen(r2, c2)
        p1 = (x1 + TILE // 2, y1 + TILE // 2)
        p2 = (x2 + TILE // 2, y2 + TILE // 2)

        pygame.draw.line(self.screen, (78, 15, 24), p1, p2, 9)
        pygame.draw.line(self.screen, (235, 64, 83), p1, p2, 5)
        pygame.draw.line(self.screen, (255, 199, 120), p1, p2, 2)
        pygame.draw.circle(self.screen, (255, 199, 120), p1, 5)
        pygame.draw.circle(self.screen, (255, 199, 120), p2, 5)

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
        draw_text(self.screen, "Bang dieu khien", FONT_MD, COLORS["text"], (panel.x + 24, panel.y + 24))
        draw_text(self.screen, "Man 1 - Tim kiem khong co thong tin", FONT_SM, COLORS["muted"], (panel.x + 24, panel.y + 58))

        info = [
            f"Thuat toan dang chon: {self.algorithm}",
            "Chuc nang AI: de sau",
        ]
        y = panel.y + 92
        for line in info:
            draw_text(self.screen, line, FONT_SM, COLORS["text"], (panel.x + 24, y))
            y += 24

        draw_text(self.screen, "Chon thuat toan", FONT, COLORS["text"], (panel.x + 24, panel.y + 128))

        mouse = pygame.mouse.get_pos()
        for button in self.buttons:
            selected = button in self.algo_buttons and button.label == self.algorithm
            button.draw(self.screen, mouse, selected)

        draw_text(self.screen, "Pin", FONT_SM, COLORS["muted"], (panel.x + 24, panel.y + 300))
        draw_battery_bar(self.screen, panel.x + 62, panel.y + 296, 150, 24, self.battery, BATTERY_MAX, COLORS, FONT_SM)

        status_box = pygame.Rect(panel.x + 24, panel.y + 338, panel.w - 48, 82)
        pygame.draw.rect(self.screen, COLORS["panel_2"], status_box, border_radius=10)
        pygame.draw.rect(self.screen, (80, 95, 120), status_box, 1, border_radius=10)
        status = [
            f"Vi tri: ({self.robot[0]}, {self.robot[1]})",
            f"Duong da di: {max(0, len(self.path) - 1)} buoc",
            f"Giao hang: {len(DELIVERY_POINTS)} diem",
        ]
        for i, line in enumerate(status):
            draw_text(self.screen, line, FONT_SM, COLORS["text"], (status_box.x + 10, status_box.y + 10 + i * 21))

        path_box = pygame.Rect(panel.x + 24, panel.y + 430, panel.w - 48, 70)
        pygame.draw.rect(self.screen, COLORS["panel_2"], path_box, border_radius=10)
        pygame.draw.rect(self.screen, (80, 95, 120), path_box, 1, border_radius=10)
        recent = self.path[-5:]
        recent_text = " -> ".join([f"({r},{c})" for r, c in recent])
        draw_text(self.screen, "Cac o vua di:", FONT_SM, COLORS["muted"], (path_box.x + 10, path_box.y + 8))
        for i, line in enumerate(wrap_text(recent_text, FONT_SM, path_box.w - 20)[:2]):
            draw_text(self.screen, line, FONT_SM, COLORS["text"], (path_box.x + 10, path_box.y + 31 + i * 19))

        todo_box = pygame.Rect(panel.x + 24, panel.y + 504, panel.w - 48, 38)
        pygame.draw.rect(self.screen, (24, 30, 40), todo_box, border_radius=10)
        pygame.draw.rect(self.screen, (65, 76, 96), todo_box, 1, border_radius=10)
        draw_center(self.screen, "O chuc nang: de sau", FONT_SM, COLORS["muted"], todo_box)

        log_box = pygame.Rect(panel.x + 24, panel.bottom - 78, panel.w - 48, 58)
        pygame.draw.rect(self.screen, COLORS["panel_2"], log_box, border_radius=10)
        pygame.draw.rect(self.screen, (80, 95, 120), log_box, 1, border_radius=10)
        for i, line in enumerate(wrap_text(self.message, FONT_SM, log_box.w - 20)[:2]):
            draw_text(self.screen, line, FONT_SM, COLORS["text"], (log_box.x + 10, log_box.y + 9 + i * 20))
