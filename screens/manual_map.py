from __future__ import annotations

import sys

import pygame

from algorithms.astar import astar_search
from algorithms.bfs import bfs
from algorithms.dfs import dfs
from algorithms.greedy import greedy_search
from algorithms.local_search import manhattan, simple_hill_climbing, simulated_annealing
from algorithms.search_common import get_delivery_at
from config import COLORS, FPS, HEIGHT, MAP_X, MAP_Y, PANEL_W, PANEL_X, TILE, WIDTH
from data.maps import BATTERY_MAX_STAGE2, LOCAL_MAP, get_map, grid_to_screen, is_cost2, is_local_walkable, is_walkable, local_grid_to_screen, map_count, tile_cost
from ui.drawing import draw_center, draw_text, wrap_text
from ui.sprites import draw_battery_bar, draw_charger

pygame.init()

FONT = pygame.font.SysFont("segoeui", 18)
FONT_XS = pygame.font.SysFont("segoeui", 13)
FONT_SM = pygame.font.SysFont("segoeui", 15)
FONT_BADGE = pygame.font.SysFont("segoeui", 14, bold=True)
FONT_MD = pygame.font.SysFont("segoeui", 24, bold=True)
FONT_LG = pygame.font.SysFont("segoeui", 34, bold=True)

ITEM_NAMES = {
    "medicine": "Thuoc",
    "computer": "May tinh",
    "bolt": "Oc vit",
    "core": "Chip",
}

ITEM_COLORS = {
    "medicine": (245, 92, 116),
    "computer": (98, 207, 255),
    "bolt": (238, 202, 98),
    "core": (178, 123, 255),
}


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
        self.stage = 1
        self.map_index = 0
        self.current_map = get_map(self.map_index)
        self.robot = self.current_map["start"][:]
        self.facing = "down"
        self.algorithm = "BFS"
        self.battery = BATTERY_MAX_STAGE2
        self.energy_used = 0
        self.local_distance = manhattan(LOCAL_MAP["start"], LOCAL_MAP["goal"])
        self.local_bad_moves = 0
        self.local_steps = 0
        self.path = [tuple(self.current_map["start"])]
        self.delivered = set()
        self.auto_path = []
        self.auto_wait = 0
        self.nodes_checked = 0
        self.solution_steps = 0
        self.result_message = "Chua chay"
        self.message = "Dung phim mui ten de di chuyen robot."
        self.buttons = []
        self.make_buttons()

    def max_battery(self):
        return BATTERY_MAX_STAGE2

    def make_buttons(self):
        left = PANEL_X + 24
        top = 244
        bw = 118
        bh = 36
        gap = 10
        if self.stage == 1:
            algorithms = ["BFS", "DFS"]
        elif self.stage == 2:
            algorithms = ["GREEDY", "A*"]
        else:
            algorithms = ["HILL", "ANNEAL"]
        self.algo_buttons = []
        self.buttons = [
            Button((left, 290, 118, 38), "RESET", self.reset_game, FONT),
            Button((left + 128, 290, 118, 38), "CHAY AI", self.run_algorithm, FONT),
            Button((left, 338, 118, 38), "DOI MAP", self.change_map, FONT),
            Button((left + 128, 338, 118, 38), "DOI MAN", self.change_stage, FONT),
        ]
        for i, name in enumerate(algorithms):
            x = left + (i % 2) * (bw + gap)
            y = top + (i // 2) * (bh + gap)
            button = Button((x, y, bw, bh), name, lambda n=name: self.select_algorithm(n), FONT)
            self.algo_buttons.append(button)
            self.buttons.append(button)

    def reset_game(self):
        if self.stage == 3:
            self.robot = list(LOCAL_MAP["start"])
        else:
            self.robot = self.current_map["start"][:]
        self.facing = "down"
        self.battery = self.max_battery()
        self.energy_used = 0
        self.local_distance = manhattan(tuple(self.robot), LOCAL_MAP["goal"])
        self.local_bad_moves = 0
        self.local_steps = 0
        self.path = [tuple(self.robot)]
        self.delivered = set()
        self.auto_path = []
        self.auto_wait = 0
        self.nodes_checked = 0
        self.solution_steps = 0
        self.result_message = "Chua chay"
        self.message = "Da reset man choi ve trang thai ban dau."

    def select_algorithm(self, name):
        self.algorithm = name
        self.message = f"Da chon thuat toan {name}."

    def run_algorithm(self):
        if self.stage == 2:
            self.auto_path = []
            start_pos = tuple(self.robot)

            if self.algorithm == "GREEDY":
                path, nodes, cost = greedy_search(self.current_map, start_pos, self.battery, self.delivered)
            else:
                path, nodes, cost = astar_search(self.current_map, start_pos, self.battery, self.delivered)

            self.nodes_checked = nodes

            if path is None:
                self.solution_steps = 0
                self.result_message = "That bai"
                self.message = f"{self.algorithm} khong tim thay duong voi luong pin hien tai."
            else:
                self.solution_steps = len(path) - 1
                self.auto_path = path[1:]
                self.path = [start_pos]
                self.auto_wait = 0

                if self.solution_steps == 0:
                    self.result_message = "Hoan thanh"
                    self.message = "Tat ca don hang da duoc giao."
                else:
                    self.result_message = "Dang chay"
                    self.message = f"{self.algorithm} tim thay duong {self.solution_steps} buoc, du kien ton {cost} pin."
            return

        if self.stage == 3:
            self.robot = list(LOCAL_MAP["start"])
            self.facing = "down"
            self.battery = self.max_battery()
            self.energy_used = 0
            self.delivered = set()
            self.path = [tuple(self.robot)]
            self.auto_path = []

            if self.algorithm == "HILL":
                path, nodes, distance, success, steps, bad_moves = simple_hill_climbing(LOCAL_MAP)
            else:
                path, nodes, distance, success, steps, bad_moves = simulated_annealing(LOCAL_MAP)

            self.local_distance = distance
            self.local_bad_moves = bad_moves
            self.local_steps = steps
            self.nodes_checked = nodes

            if not success:
                self.solution_steps = 0
                self.result_message = "That bai"
                self.auto_path = path[1:]
                self.message = f"{self.algorithm} bi ket, Manhattan con {distance}."
            else:
                self.solution_steps = len(path) - 1
                self.auto_path = path[1:]
                self.auto_wait = 0
                self.result_message = "Dang chay"
                self.message = f"{self.algorithm} tim duoc duong, chap nhan xau {bad_moves} lan."
            return

        self.auto_path = []
        start_pos = tuple(self.robot)

        if self.algorithm == "BFS":
            path, nodes = bfs(self.current_map, start_pos, self.delivered)
        else:
            path, nodes = dfs(self.current_map, start_pos, self.delivered)

        self.nodes_checked = nodes

        if path is None:
            self.solution_steps = 0
            self.result_message = "That bai"
            self.message = f"{self.algorithm} khong tim thay duong giao hang."
        else:
            self.solution_steps = len(path) - 1
            self.auto_path = path[1:]
            self.path = [start_pos]
            self.auto_wait = 0
            self.result_message = "Dang chay"
            self.message = f"{self.algorithm} tim thay duong {self.solution_steps} buoc, xet {nodes} node."

    def change_map(self):
        if self.stage == 3:
            self.message = "Man 3 hien chi co 1 map local search."
            return

        self.map_index = (self.map_index + 1) % map_count()
        self.current_map = get_map(self.map_index)
        self.reset_game()
        self.message = f"Da doi sang map {self.map_index + 1}: {self.current_map['name']}."

    def change_stage(self):
        if self.stage == 1:
            self.stage = 2
            self.algorithm = "GREEDY"
            message = "Da chuyen sang man 2: co pin va o ton 2 pin."
        elif self.stage == 2:
            self.stage = 3
            self.algorithm = "HILL"
            message = "Da chuyen sang man 3: local search voi Manhattan."
        else:
            self.stage = 1
            self.algorithm = "BFS"
            message = "Da quay ve man 1: BFS/DFS khong dung pin."

        self.make_buttons()
        self.reset_game()
        self.message = message

    def active_chargers(self):
        return self.current_map["chargers"]

    def is_active_charger(self, row, col):
        return (row, col) in self.active_chargers()

    def update_delivery(self, row, col):
        if self.stage == 3:
            self.local_distance = manhattan((row, col), LOCAL_MAP["goal"])
            if (row, col) == LOCAL_MAP["goal"]:
                self.result_message = "Hoan thanh"
                self.message = f"{self.algorithm} da toi diem giao hang."
            return

        label = get_delivery_at(self.current_map, row, col)
        if label and label not in self.delivered:
            self.delivered.add(label)
            self.message = f"Da giao mon {label} tai o ({row}, {col})."
            if len(self.delivered) == len(self.current_map["delivery"]):
                self.result_message = "Hoan thanh"
                self.message = "Hoan thanh giao tat ca don hang."

    def step_to(self, row, col):
        old_row, old_col = self.robot
        if row < old_row:
            self.facing = "up"
        elif row > old_row:
            self.facing = "down"
        elif col < old_col:
            self.facing = "left"
        elif col > old_col:
            self.facing = "right"

        self.robot = [row, col]
        self.path.append((row, col))
        if self.stage == 2:
            cost = tile_cost(self.current_map, row, col)
            self.battery -= cost
            self.energy_used += cost

            if self.is_active_charger(row, col):
                self.battery = self.max_battery()
                self.message = f"Robot den tram sac ({row}, {col}), pin da day lai."
            else:
                self.message = f"Robot di chuyen toi o ({row}, {col}), ton {cost} pin."
        else:
            self.message = f"Robot di chuyen toi o ({row}, {col})."

        self.update_delivery(row, col)

    def update_auto_move(self):
        if not self.auto_path:
            return

        self.auto_wait += 1
        if self.auto_wait < 12:
            return

        self.auto_wait = 0
        row, col = self.auto_path.pop(0)
        self.step_to(row, col)

        if not self.auto_path:
            if self.stage == 3:
                if tuple(self.robot) == LOCAL_MAP["goal"]:
                    self.result_message = "Hoan thanh"
                    self.message = f"{self.algorithm} giao hang thanh cong."
                else:
                    self.result_message = "That bai"
                    self.message = f"{self.algorithm} dung lai khi Manhattan con {self.local_distance}."
                return

            if len(self.delivered) == len(self.current_map["delivery"]):
                self.result_message = "Hoan thanh"
                self.message = f"Hoan thanh giao hang bang {self.algorithm}."
            else:
                self.result_message = "That bai"
                self.message = f"Robot da di het duong {self.algorithm} nhung chua giao du hang."

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

        if self.stage == 3:
            if is_local_walkable(nr, nc):
                self.auto_path = []
                self.step_to(nr, nc)
            else:
                self.message = "Khong the di vao tuong hoac vat can."
            return

        if is_walkable(self.current_map, nr, nc):
            if self.stage == 2:
                cost = tile_cost(self.current_map, nr, nc)
                if self.battery < cost:
                    self.message = "Pin khong du de di tiep, can tim tram sac."
                    return

            self.auto_path = []
            self.step_to(nr, nc)
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
            self.update_auto_move()
            self.draw()
            pygame.display.flip()

    def draw(self):
        self.screen.fill(COLORS["bg"])
        self.draw_background_pattern()
        self.draw_title()
        self.draw_map()
        self.draw_path()
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
        title_x = 54
        note_x = 56
        if self.stage == 1:
            title = "Man 1 - Tim Kiem Khong Thong Tin"
            note = "BFS/DFS giao hang tren map khong co chi phi va khong dung pin"
        elif self.stage == 2:
            title = "Man 2 - Tuyen Duong Nang Luong"
            note = "Map co o ton 2 pin, tram sac va thanh pin cho Greedy/A*"
        else:
            title = "Man 3 - Bay Cuc Bo"
            note = "Hill Climbing dung o cuc tri cuc bo, Annealing chap nhan buoc xau de thoat"
            title_x, _ = local_grid_to_screen(0, 0)
            note_x = title_x + 2
        draw_text(self.screen, title, FONT_LG, COLORS["text"], (title_x, 28))
        draw_text(self.screen, note, FONT, COLORS["muted"], (note_x, 66))

    def draw_map(self):
        if self.stage == 3:
            self.draw_local_map()
            return

        grid = self.current_map["grid"]
        rows = len(grid)
        cols = len(grid[0])
        outer = pygame.Rect(MAP_X - 14, MAP_Y - 14, cols * TILE + 28, rows * TILE + 28)
        pygame.draw.rect(self.screen, (2, 3, 6), outer.move(0, 8), border_radius=6)
        pygame.draw.rect(self.screen, (26, 31, 43), outer, border_radius=6)
        pygame.draw.rect(self.screen, (85, 96, 116), outer, 2, border_radius=6)

        for r, row in enumerate(grid):
            for c, tile in enumerate(row):
                if tile == ".":
                    continue
                rect = pygame.Rect(*grid_to_screen(r, c), TILE, TILE)
                self.draw_tile(rect, tile, r, c)

        for start, end in self.current_map["lasers"]:
            self.draw_laser(start, end)

        for index, (r, c) in enumerate(self.current_map["chargers"], start=1):
            rect = pygame.Rect(*grid_to_screen(r, c), TILE, TILE)
            draw_charger(self.screen, rect, f"C{index}", COLORS, FONT_SM)

        for label, (r, c), kind in self.current_map["delivery"]:
            rect = pygame.Rect(*grid_to_screen(r, c), TILE, TILE)
            self.draw_delivery_point(rect, label, kind)

    def draw_local_map(self):
        grid = LOCAL_MAP["grid"]
        rows = len(grid)
        cols = len(grid[0])
        start_x, start_y = local_grid_to_screen(0, 0)
        outer = pygame.Rect(start_x - 14, start_y - 14, cols * TILE + 28, rows * TILE + 28)
        pygame.draw.rect(self.screen, (2, 3, 6), outer.move(0, 8), border_radius=6)
        pygame.draw.rect(self.screen, (26, 31, 43), outer, border_radius=6)
        pygame.draw.rect(self.screen, (85, 96, 116), outer, 2, border_radius=6)

        for r, row in enumerate(grid):
            for c, tile in enumerate(row):
                rect = pygame.Rect(*local_grid_to_screen(r, c), TILE, TILE)
                if tile == ".":
                    self.draw_hole(rect)
                elif tile == "W" or tile == "X":
                    self.draw_tile(rect, tile, r, c)
                else:
                    self.draw_tile(rect, "F", r, c)

        for start, end in LOCAL_MAP["lasers"]:
            self.draw_local_laser(start, end)

        goal_row, goal_col = LOCAL_MAP["goal"]
        goal_rect = pygame.Rect(*local_grid_to_screen(goal_row, goal_col), TILE, TILE)
        self.draw_delivery_point(goal_rect, "G", "core")

    def draw_path(self):
        for index, (r, c) in enumerate(self.path[:-1]):
            if self.stage == 3:
                x, y = local_grid_to_screen(r, c)
            else:
                x, y = grid_to_screen(r, c)
            center = (x + TILE // 2, y + TILE // 2)
            pygame.draw.circle(self.screen, (47, 214, 190), center, 5)
            pygame.draw.circle(self.screen, (5, 12, 18), center, 5, 1)

    def draw_tile(self, rect, tile, row, col):
        if tile == "W":
            self.draw_wall(rect)
        elif tile == "X":
            self.draw_obstacle(rect)
        elif self.stage == 2 and is_cost2(self.current_map, row, col):
            self.draw_cost_floor(rect)
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

    def draw_cost_floor(self, rect):
        pygame.draw.rect(self.screen, (132, 119, 91), rect)
        pygame.draw.rect(self.screen, (238, 202, 98), (rect.x + 5, rect.y + 5, rect.w - 10, rect.h - 10), 2)
        pygame.draw.line(self.screen, (210, 180, 105), (rect.x + 8, rect.y + 10), (rect.right - 8, rect.bottom - 10), 1)
        badge = pygame.Rect(rect.right - 20, rect.y + 5, 15, 15)
        pygame.draw.rect(self.screen, (41, 35, 24), badge, border_radius=4)
        pygame.draw.rect(self.screen, (238, 202, 98), badge, 1, border_radius=4)
        draw_center(self.screen, "2", FONT_XS, COLORS["text"], badge)

    def draw_hole(self, rect):
        pygame.draw.rect(self.screen, (2, 4, 8), rect)
        pygame.draw.rect(self.screen, (18, 25, 36), rect.inflate(-6, -6), 1)
        pygame.draw.circle(self.screen, (8, 12, 20), rect.center, 10)

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

    def draw_local_laser(self, start, end):
        r1, c1 = start
        r2, c2 = end
        x1, y1 = local_grid_to_screen(r1, c1)
        x2, y2 = local_grid_to_screen(r2, c2)
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
        if self.stage == 3:
            x, y = local_grid_to_screen(row, col)
        else:
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
        if self.stage == 3:
            map_line = f"Man 3 | {LOCAL_MAP['name']}"
        else:
            map_line = f"Man {self.stage} | Map {self.map_index + 1}/{map_count()} - {self.current_map['name']}"
        draw_text(self.screen, map_line, FONT_SM, COLORS["muted"], (panel.x + 24, panel.y + 58))

        info = [
            f"Thuat toan dang chon: {self.algorithm}",
            f"Node da xet: {self.nodes_checked}",
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

        status_box = pygame.Rect(panel.x + 24, panel.y + 300, panel.w - 48, 112)
        pygame.draw.rect(self.screen, COLORS["panel_2"], status_box, border_radius=10)
        pygame.draw.rect(self.screen, (80, 95, 120), status_box, 1, border_radius=10)
        if self.stage == 2:
            draw_text(self.screen, f"Vi tri: ({self.robot[0]}, {self.robot[1]})", FONT_SM, COLORS["text"], (status_box.x + 10, status_box.y + 8))
            draw_text(self.screen, "Pin", FONT_SM, COLORS["muted"], (status_box.x + 10, status_box.y + 32))
            draw_battery_bar(
                self.screen,
                status_box.x + 48,
                status_box.y + 29,
                150,
                22,
                self.battery,
                self.max_battery(),
                COLORS,
                FONT_XS,
            )
            draw_text(self.screen, f"Pin da tieu: {self.energy_used}", FONT_SM, COLORS["text"], (status_box.x + 10, status_box.y + 56))
            draw_text(self.screen, f"Da giao: {len(self.delivered)}/{len(self.current_map['delivery'])}", FONT_SM, COLORS["text"], (status_box.x + 10, status_box.y + 76))
            draw_text(self.screen, f"Ket qua: {self.result_message}", FONT_SM, COLORS["text"], (status_box.x + 10, status_box.y + 96))
        elif self.stage == 3:
            draw_text(self.screen, f"Vi tri: ({self.robot[0]}, {self.robot[1]})", FONT_SM, COLORS["text"], (status_box.x + 10, status_box.y + 8))
            draw_text(self.screen, f"Goal: {LOCAL_MAP['goal']}", FONT_SM, COLORS["text"], (status_box.x + 10, status_box.y + 30))
            draw_text(self.screen, f"Manhattan: {self.local_distance}", FONT_SM, COLORS["text"], (status_box.x + 10, status_box.y + 52))
            draw_text(self.screen, f"Buoc xau: {self.local_bad_moves}", FONT_SM, COLORS["text"], (status_box.x + 10, status_box.y + 74))
            draw_text(self.screen, f"Ket qua: {self.result_message}", FONT_SM, COLORS["text"], (status_box.x + 10, status_box.y + 96))
        else:
            status = [
                f"Vi tri: ({self.robot[0]}, {self.robot[1]})",
                f"Duong da di: {max(0, len(self.path) - 1)} buoc",
                f"Da giao: {len(self.delivered)}/{len(self.current_map['delivery'])}",
                f"Ket qua: {self.result_message}",
            ]
            for i, line in enumerate(status):
                draw_text(self.screen, line, FONT_SM, COLORS["text"], (status_box.x + 10, status_box.y + 12 + i * 22))

        path_box = pygame.Rect(panel.x + 24, panel.y + 422, panel.w - 48, 58)
        pygame.draw.rect(self.screen, COLORS["panel_2"], path_box, border_radius=10)
        pygame.draw.rect(self.screen, (80, 95, 120), path_box, 1, border_radius=10)
        recent = self.path[-4:]
        recent_text = " -> ".join([f"({r},{c})" for r, c in recent])
        draw_text(self.screen, "Cac o vua di:", FONT_SM, COLORS["muted"], (path_box.x + 10, path_box.y + 8))
        for i, line in enumerate(wrap_text(recent_text, FONT_SM, path_box.w - 20)[:2]):
            draw_text(self.screen, line, FONT_SM, COLORS["text"], (path_box.x + 10, path_box.y + 28 + i * 18))

        delivery_box = pygame.Rect(panel.x + 24, panel.y + 488, panel.w - 48, 56)
        pygame.draw.rect(self.screen, COLORS["panel_2"], delivery_box, border_radius=10)
        pygame.draw.rect(self.screen, (80, 95, 120), delivery_box, 1, border_radius=10)
        if self.stage == 3:
            draw_text(self.screen, "Muc tieu local:", FONT_SM, COLORS["muted"], (delivery_box.x + 10, delivery_box.y + 7))
            draw_text(self.screen, "G: Giao chip khan cap", FONT_XS, COLORS["text"], (delivery_box.x + 10, delivery_box.y + 30))
            draw_text(self.screen, "Hill chi di khi Manhattan giam", FONT_XS, COLORS["muted"], (delivery_box.x + 10, delivery_box.y + 44))
        else:
            draw_text(self.screen, "Hang can giao:", FONT_SM, COLORS["muted"], (delivery_box.x + 10, delivery_box.y + 7))

            for i, (label, pos, kind) in enumerate(self.current_map["delivery"]):
                x = delivery_box.x + 10 + (i % 2) * 118
                y = delivery_box.y + 26 + (i // 2) * 15
                color = ITEM_COLORS.get(kind, COLORS["cyan"])
                name = ITEM_NAMES.get(kind, kind)
                if label in self.delivered:
                    name = name + " OK"
                pygame.draw.rect(self.screen, color, (x, y + 3, 9, 9), border_radius=2)
                draw_text(self.screen, f"{label}: {name}", FONT_XS, COLORS["text"], (x + 14, y))

        log_box = pygame.Rect(panel.x + 24, panel.bottom - 78, panel.w - 48, 58)
        pygame.draw.rect(self.screen, COLORS["panel_2"], log_box, border_radius=10)
        pygame.draw.rect(self.screen, (80, 95, 120), log_box, 1, border_radius=10)
        for i, line in enumerate(wrap_text(self.message, FONT_SM, log_box.w - 20)[:2]):
            draw_text(self.screen, line, FONT_SM, COLORS["text"], (log_box.x + 10, log_box.y + 9 + i * 20))
