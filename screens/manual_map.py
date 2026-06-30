from __future__ import annotations

import os
import sys
import time

import pygame

from algorithms.astar import astar_search
from algorithms.adversarial_search import make_alpha_beta_plan, make_minimax_plan
from algorithms.belief_search import make_known_map, make_possible_goals, reveal_area, unknown_goal_belief_search, unknown_goal_dfs_search, update_possible_goals
from algorithms.bfs import bfs
from algorithms.csp_backtracking import backtracking_order, forward_checking_order, make_delivery_route
from algorithms.dfs import dfs
from algorithms.greedy import greedy_search
from algorithms.local_search import manhattan, simple_hill_climbing, simulated_annealing
from algorithms.search_common import get_delivery_at
from config import COLORS, FPS, HEIGHT, MAP_X, MAP_Y, PANEL_W, PANEL_X, TILE, WIDTH
from data.maps import BATTERY_MAX_STAGE2, BELIEF_MAP, BOSS_MAP, CSP_MAP, LOCAL_MAP, belief_grid_to_screen, belief_map_count, get_belief_map, get_map, grid_to_screen, is_belief_walkable, is_cost2, is_local_walkable, is_walkable, local_grid_to_screen, map_count, tile_cost
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
    "sensor": "Cam bien",
}

ITEM_COLORS = {
    "medicine": (245, 92, 116),
    "computer": (98, 207, 255),
    "bolt": (238, 202, 98),
    "core": (178, 123, 255),
    "sensor": (82, 220, 145),
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
        self.boss_image = self.load_boss_image()
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
        self.known_map = make_known_map(BELIEF_MAP)
        self.possible_goals = set()
        self.revealed_cells = 0
        self.unknown_cells = 0
        self.goal_seen = True
        self.csp_order = []
        self.boss = BOSS_MAP["boss"][:]
        self.boss_delivered = set()
        self.boss_delivered_path = []
        self.path = [tuple(self.current_map["start"])]
        self.delivered = set()
        self.auto_path = []
        self.boss_auto_path = []
        self.auto_wait = 0
        self.nodes_checked = 0
        self.algorithm_time = 0.0
        self.solution_steps = 0
        self.result_message = "Chua chay"
        self.message = "Dung phim mui ten de di chuyen robot."
        self.buttons = []
        self.make_buttons()

    def load_boss_image(self):
        root_folder = os.path.dirname(os.path.dirname(__file__))
        image_path = os.path.join(root_folder, "assets", "boss_sprite.png")

        if not os.path.exists(image_path):
            return None

        image = pygame.image.load(image_path).convert_alpha()
        width = int(TILE * 2.7)
        height = int(width * image.get_height() / image.get_width())
        return pygame.transform.smoothscale(image, (width, height))

    def max_battery(self):
        return BATTERY_MAX_STAGE2

    def active_belief_map(self):
        return get_belief_map(self.map_index)

    def count_unknown_cells(self):
        count = 0
        for row in self.known_map:
            for tile in row:
                if tile == "?":
                    count += 1
        return count

    def reset_belief_state(self):
        game_map = self.active_belief_map()
        self.known_map = make_known_map(game_map, False)
        self.possible_goals = make_possible_goals(game_map, tuple(self.robot))

        new_cells, found_goal = reveal_area(game_map, self.known_map, tuple(self.robot), know_goal=False)
        self.revealed_cells = new_cells
        self.goal_seen = found_goal
        if update_possible_goals(game_map, self.known_map, self.possible_goals):
            self.goal_seen = True
        self.unknown_cells = self.count_unknown_cells()

    def make_buttons(self):
        left = PANEL_X + 24
        top = 244
        gap = 12
        bw = (PANEL_W - 48 - gap) // 2
        bh = 38
        if self.stage == 1:
            algorithms = ["BFS", "DFS"]
        elif self.stage == 2:
            algorithms = ["GREEDY", "A*"]
        elif self.stage == 3:
            algorithms = ["HILL", "ANNEAL"]
        elif self.stage == 4:
            algorithms = ["BFS", "DFS"]
        elif self.stage == 5:
            algorithms = ["BACKTRACK", "FORWARD"]
        else:
            algorithms = ["MINIMAX", "ALPHA-BETA"]
        self.algo_buttons = []
        self.buttons = [
            Button((left, 296, bw, 38), "RESET", self.reset_game, FONT),
            Button((left + bw + gap, 296, bw, 38), "CHAY AI", self.run_algorithm, FONT),
            Button((left, 344, bw, 38), "DOI MAP", self.change_map, FONT),
            Button((left + bw + gap, 344, bw, 38), "DOI MAN", self.change_stage, FONT),
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
        elif self.stage == 4:
            self.robot = self.active_belief_map()["start"][:]
        elif self.stage == 5:
            self.robot = CSP_MAP["start"][:]
        elif self.stage == 6:
            self.robot = BOSS_MAP["start"][:]
            self.boss = BOSS_MAP["boss"][:]
            self.boss_delivered = set()
            self.boss_delivered_path = []
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
        self.boss_auto_path = []
        self.auto_wait = 0
        self.nodes_checked = 0
        self.algorithm_time = 0.0
        self.solution_steps = 0
        self.csp_order = []
        self.result_message = "Chua chay"
        if self.stage == 4:
            self.reset_belief_state()
        self.message = "Da reset man choi ve trang thai ban dau."

    def select_algorithm(self, name):
        self.algorithm = name
        if self.stage == 4:
            self.reset_game()
        self.message = f"Da chon thuat toan {name}."

    def run_algorithm(self):
        if self.stage == 2:
            self.auto_path = []
            start_pos = tuple(self.robot)

            start_time = time.perf_counter()
            if self.algorithm == "GREEDY":
                path, nodes, cost = greedy_search(self.current_map, start_pos, self.battery, self.delivered)
            else:
                path, nodes, cost = astar_search(self.current_map, start_pos, self.battery, self.delivered)
            self.algorithm_time = time.perf_counter() - start_time

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

            start_time = time.perf_counter()
            if self.algorithm == "HILL":
                path, nodes, distance, success, steps, bad_moves = simple_hill_climbing(LOCAL_MAP)
            else:
                path, nodes, distance, success, steps, bad_moves = simulated_annealing(LOCAL_MAP)
            self.algorithm_time = time.perf_counter() - start_time

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

        if self.stage == 4:
            game_map = self.active_belief_map()
            self.robot = game_map["start"][:]
            self.facing = "down"
            self.path = [tuple(self.robot)]
            self.auto_path = []
            self.auto_wait = 0
            self.result_message = "Chua chay"
            self.reset_belief_state()

            start_time = time.perf_counter()
            if self.algorithm == "DFS":
                path, nodes, revealed, success, possible_count = unknown_goal_dfs_search(game_map, tuple(self.robot))
            else:
                path, nodes, revealed, success, possible_count = unknown_goal_belief_search(game_map, tuple(self.robot))
            self.algorithm_time = time.perf_counter() - start_time

            self.nodes_checked = nodes
            self.solution_steps = max(0, len(path) - 1)

            if success:
                self.auto_path = path[1:]
                self.result_message = "Dang chay"
                self.message = f"{self.algorithm} tim duong {self.solution_steps} buoc, mo them {revealed} o."
            else:
                self.auto_path = path[1:]
                self.result_message = "That bai"
                self.message = f"{self.algorithm} khong tim duoc goal voi thong tin da mo."
            return

        if self.stage == 5:
            self.robot = CSP_MAP["start"][:]
            self.facing = "down"
            self.path = [tuple(self.robot)]
            self.delivered = set()
            self.auto_path = []
            self.auto_wait = 0

            start_time = time.perf_counter()
            if self.algorithm == "FORWARD":
                order, nodes = forward_checking_order(CSP_MAP)
            else:
                order, nodes = backtracking_order(CSP_MAP)
            self.algorithm_time = time.perf_counter() - start_time
            self.nodes_checked = nodes

            if order is None:
                self.csp_order = []
                self.solution_steps = 0
                self.result_message = "That bai"
                self.message = f"{self.algorithm} khong tim duoc thu tu giao hop le."
            else:
                route = make_delivery_route(CSP_MAP, order)
                self.csp_order = order

                if route is None:
                    self.solution_steps = 0
                    self.result_message = "That bai"
                    self.message = "Tim duoc thu tu nhung robot khong co duong di."
                else:
                    self.solution_steps = len(route) - 1
                    self.auto_path = route[1:]
                    self.result_message = "Dang chay"
                    self.message = "Thu tu CSP: " + " -> ".join(order)
            return

        if self.stage == 6:
            self.robot = BOSS_MAP["start"][:]
            self.boss = BOSS_MAP["boss"][:]
            self.facing = "down"
            self.boss_delivered = set()
            self.boss_delivered_path = []
            self.path = [tuple(self.robot)]
            self.auto_path = []
            self.boss_auto_path = []
            self.auto_wait = 0

            start_time = time.perf_counter()
            if self.algorithm == "ALPHA-BETA":
                robot_path, boss_path, delivered_path, nodes, success, reason = make_alpha_beta_plan(BOSS_MAP, depth=6, max_turns=120)
            else:
                robot_path, boss_path, delivered_path, nodes, success, reason = make_minimax_plan(BOSS_MAP, depth=6, max_turns=120)
            self.algorithm_time = time.perf_counter() - start_time

            self.nodes_checked = nodes
            self.solution_steps = max(0, len(robot_path) - 1)
            self.auto_path = robot_path[1:]
            self.boss_auto_path = boss_path[1:]
            self.boss_delivered_path = delivered_path[1:]
            self.result_message = "Dang chay" if self.auto_path else ("Hoan thanh" if success else "That bai")
            self.message = f"{self.algorithm} tao {self.solution_steps} luot, du kien: {reason}."
            return

        self.auto_path = []
        start_pos = tuple(self.robot)

        start_time = time.perf_counter()
        if self.algorithm == "BFS":
            path, nodes = bfs(self.current_map, start_pos, self.delivered)
        else:
            path, nodes = dfs(self.current_map, start_pos, self.delivered)
        self.algorithm_time = time.perf_counter() - start_time

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

        if self.stage == 4:
            self.map_index = (self.map_index + 1) % belief_map_count()
            self.reset_game()
            game_map = self.active_belief_map()
            self.message = f"Da doi sang map {self.map_index + 1}: {game_map['name']}."
            return

        if self.stage == 5:
            self.message = "Man 5 hien chi co 1 map CSP."
            return

        if self.stage == 6:
            self.message = "Man 6 hien chi co 1 map boss."
            return

        self.map_index = (self.map_index + 1) % map_count()
        self.current_map = get_map(self.map_index)
        self.reset_game()
        self.message = f"Da doi sang map {self.map_index + 1}: {self.current_map['name']}."

    def change_stage(self):
        if self.stage == 1:
            self.stage = 2
            self.algorithm = "GREEDY"
        elif self.stage == 2:
            self.stage = 3
            self.algorithm = "HILL"
        elif self.stage == 3:
            self.stage = 4
            self.algorithm = "BFS"
        elif self.stage == 4:
            self.stage = 5
            self.algorithm = "BACKTRACK"
        elif self.stage == 5:
            self.stage = 6
            self.algorithm = "MINIMAX"
        else:
            self.stage = 1
            self.algorithm = "BFS"

        self.make_buttons()
        self.reset_game()
        self.message = ""

    def active_chargers(self):
        if self.stage == 6:
            return BOSS_MAP["chargers"]
        return self.current_map["chargers"]

    def is_active_charger(self, row, col):
        return (row, col) in self.active_chargers()

    def boss_danger_cells(self):
        cells = set()
        boss_row, boss_col = self.boss
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                cells.add((boss_row + dr, boss_col + dc))
        return cells

    def current_boss_target(self):
        labels = []
        for label, pos, kind in BOSS_MAP["delivery"]:
            if label not in self.boss_delivered:
                labels.append(label)
        return ", ".join(labels) if labels else "Xong"

    def update_delivery(self, row, col):
        if self.stage == 3:
            self.local_distance = manhattan((row, col), LOCAL_MAP["goal"])
            if (row, col) == LOCAL_MAP["goal"]:
                self.result_message = "Hoan thanh"
                self.message = f"{self.algorithm} da toi diem giao hang."
            return

        if self.stage == 4:
            if (row, col) == self.active_belief_map()["goal"]:
                self.result_message = "Hoan thanh"
                self.message = "Robot da giao chip trong vung map bi mu."
            return

        if self.stage == 5:
            label = get_delivery_at(CSP_MAP, row, col)
            if label and label not in self.delivered:
                self.delivered.add(label)
                self.message = f"Da giao mon {label} theo thu tu CSP."
                if len(self.delivered) == len(CSP_MAP["delivery"]):
                    self.result_message = "Hoan thanh"
                    self.message = "Hoan thanh giao hang theo rang buoc CSP."
            return

        if self.stage == 6:
            label = get_delivery_at(BOSS_MAP, row, col)
            if label and label not in self.boss_delivered:
                self.boss_delivered.add(label)
                if len(self.boss_delivered) == len(BOSS_MAP["delivery"]):
                    self.result_message = "Hoan thanh"
                    self.message = "Da giao du hang va thang man boss."
                else:
                    self.message = f"Da giao {label}."
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
        elif self.stage == 4:
            game_map = self.active_belief_map()
            new_cells, found_goal = reveal_area(game_map, self.known_map, (row, col), know_goal=False)
            self.revealed_cells += new_cells
            if found_goal:
                self.goal_seen = True
            if update_possible_goals(game_map, self.known_map, self.possible_goals):
                self.goal_seen = True
            self.unknown_cells = self.count_unknown_cells()
            self.message = f"Robot quan sat quanh ({row}, {col}), mo them {new_cells} o."
        elif self.stage == 6:
            if (row, col) in self.boss_danger_cells():
                self.result_message = "That bai"
                self.message = "Robot di vao vung nguy hiem cua boss."
            else:
                self.message = f"Robot di toi ({row}, {col})."
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

        if self.stage == 6:
            row, col = self.auto_path.pop(0)
            boss_pos = self.boss
            if self.boss_auto_path:
                boss_pos = self.boss_auto_path.pop(0)

            self.step_to(row, col)
            if self.boss_delivered_path:
                self.boss_delivered = set(self.boss_delivered_path.pop(0))

            if self.result_message != "Hoan thanh":
                self.boss = [boss_pos[0], boss_pos[1]]
                if tuple(self.robot) in self.boss_danger_cells():
                    self.auto_path = []
                    self.boss_auto_path = []
                    self.result_message = "That bai"
                    self.message = "Boss da ap sat robot trong vung nguy hiem."
                    return

            if not self.auto_path:
                if len(self.boss_delivered) == len(BOSS_MAP["delivery"]):
                    self.result_message = "Hoan thanh"
                    self.message = f"{self.algorithm} da giao du 4 mon hang."
                elif tuple(self.robot) in self.boss_danger_cells():
                    self.result_message = "That bai"
                    self.message = f"{self.algorithm} dung lai vi boss bat kip."
                else:
                    self.result_message = "That bai"
                    self.message = f"{self.algorithm} dung lai khi chua giao du hang."
            return

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

            if self.stage == 4:
                if tuple(self.robot) == self.active_belief_map()["goal"]:
                    self.result_message = "Hoan thanh"
                    self.message = f"{self.algorithm} da tim duoc duong toi goal."
                else:
                    self.result_message = "That bai"
                    self.message = f"{self.algorithm} dung lai khi chua den goal."
                return

            if self.stage == 5:
                if len(self.delivered) == len(CSP_MAP["delivery"]):
                    self.result_message = "Hoan thanh"
                    self.message = f"{self.algorithm} da giao du hang theo dung rang buoc."
                else:
                    self.result_message = "That bai"
                    self.message = "Robot dung lai khi chua giao du hang CSP."
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

        if self.stage == 4:
            if is_belief_walkable(nr, nc, self.active_belief_map()):
                self.auto_path = []
                self.step_to(nr, nc)
            else:
                self.message = "Khong the di vao tuong, hop hoac vung trong."
            return

        if self.stage == 5:
            if is_belief_walkable(nr, nc, CSP_MAP):
                self.auto_path = []
                self.step_to(nr, nc)
            else:
                self.message = "Khong the di vao tuong, hop hoac vung trong."
            return

        if self.stage == 6:
            if self.result_message in ["Hoan thanh", "That bai"]:
                self.message = "Man choi da ket thuc, bam RESET de choi lai."
                return
            if is_belief_walkable(nr, nc, BOSS_MAP) and (nr, nc) not in BOSS_MAP["laser_cells"]:
                self.auto_path = []
                self.step_to(nr, nc)
            else:
                self.message = "Khong the di vao tuong, hop hoac vung trong."
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
            (1320, 760, 2),
            (1008, 715, 1),
            (90, 748, 1),
            (344, 744, 2),
            (930, 710, 1),
            (1360, 238, 1),
            (1160, 706, 1),
            (690, 742, 2),
            (1464, 612, 1),
            (1214, 322, 2),
            (80, 182, 1),
            (204, 148, 2),
            (430, 114, 1),
            (620, 166, 1),
            (884, 176, 2),
            (1044, 232, 1),
            (1390, 164, 1),
            (1438, 394, 2),
            (1266, 544, 1),
            (1110, 610, 2),
            (772, 676, 1),
            (510, 706, 1),
            (190, 624, 2),
            (58, 512, 1),
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
            title = "LEVEL 1"
            note = "Giao tat ca cac mon hang !"
        elif self.stage == 2:
            title = "LEVEL 2"
            note = "Giao hang, co pin va tram sac !"
        elif self.stage == 3:
            title = "LEVEL 3"
            note = "Giao hang qua me cung !"
            title_x, _ = local_grid_to_screen(0, 0)
            note_x = title_x + 2
        elif self.stage == 4:
            title = "LEVEL 4"
            note = "Giao hang, moi truong mat tin hieu !"
            title_x, _ = belief_grid_to_screen(0, 0, self.active_belief_map())
            note_x = title_x + 2
        elif self.stage == 5:
            title = "LEVEL 5"
            note = "Giao hang theo dung thu tu !"
        else:
            title = "LEVEL 6"
            note = "Giao hang, tranh khoi ke dich !"
        draw_text(self.screen, title, FONT_LG, COLORS["text"], (title_x, 28))
        draw_text(self.screen, note, FONT, COLORS["muted"], (note_x, 66))

    def draw_map(self):
        if self.stage == 3:
            self.draw_local_map()
            return

        if self.stage == 4:
            self.draw_belief_map()
            return

        if self.stage == 5:
            self.draw_csp_map()
            return

        if self.stage == 6:
            self.draw_boss_map()
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

        if self.stage == 2:
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

    def draw_belief_map(self):
        game_map = self.active_belief_map()
        grid = game_map["grid"]
        rows = len(grid)
        cols = len(grid[0])
        start_x, start_y = belief_grid_to_screen(0, 0, game_map)
        outer = pygame.Rect(start_x - 14, start_y - 14, cols * TILE + 28, rows * TILE + 28)
        pygame.draw.rect(self.screen, (2, 3, 6), outer.move(0, 8), border_radius=6)
        pygame.draw.rect(self.screen, (26, 31, 43), outer, border_radius=6)
        pygame.draw.rect(self.screen, (85, 96, 116), outer, 2, border_radius=6)

        goal_row, goal_col = game_map["goal"]

        for r, row in enumerate(grid):
            for c, tile in enumerate(row):
                rect = pygame.Rect(*belief_grid_to_screen(r, c, game_map), TILE, TILE)

                if tile == "W":
                    self.draw_tile(rect, "W", r, c)
                    continue

                if (r, c) == (goal_row, goal_col) and self.known_map[r][c] == "G":
                    self.draw_floor(rect)
                    self.draw_goal_beacon(rect)
                    continue

                known_tile = self.known_map[r][c]
                if known_tile == "?":
                    self.draw_unknown_tile(rect)
                elif known_tile == ".":
                    self.draw_hole(rect)
                elif known_tile == "W" or known_tile == "X":
                    self.draw_tile(rect, known_tile, r, c)
                else:
                    self.draw_tile(rect, "F", r, c)

    def draw_csp_map(self):
        grid = CSP_MAP["grid"]
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

        for start, end in CSP_MAP["lasers"]:
            self.draw_laser(start, end)

        for label, (r, c), kind in CSP_MAP["delivery"]:
            rect = pygame.Rect(*grid_to_screen(r, c), TILE, TILE)
            self.draw_delivery_point(rect, label, kind)

    def draw_boss_map(self):
        grid = BOSS_MAP["grid"]
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

        for r, c in self.boss_danger_cells():
            if is_belief_walkable(r, c, BOSS_MAP):
                rect = pygame.Rect(*grid_to_screen(r, c), TILE, TILE)
                self.draw_boss_danger(rect)

        for start, end in BOSS_MAP["lasers"]:
            self.draw_laser(start, end)

        for index, (r, c) in enumerate(BOSS_MAP["chargers"], start=1):
            rect = pygame.Rect(*grid_to_screen(r, c), TILE, TILE)
            draw_charger(self.screen, rect, f"S{index}", COLORS, FONT_SM)

        for label, (r, c), kind in BOSS_MAP["delivery"]:
            rect = pygame.Rect(*grid_to_screen(r, c), TILE, TILE)
            self.draw_delivery_point(rect, label, kind)

        self.draw_boss()

    def draw_path(self):
        for index, (r, c) in enumerate(self.path[:-1]):
            if self.stage == 3:
                x, y = local_grid_to_screen(r, c)
            elif self.stage == 4:
                x, y = belief_grid_to_screen(r, c, self.active_belief_map())
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

    def draw_unknown_tile(self, rect):
        pygame.draw.rect(self.screen, (12, 17, 27), rect)
        pygame.draw.rect(self.screen, (34, 47, 66), rect.inflate(-6, -6), 1)

        for offset in range(-TILE, TILE, 12):
            start = (rect.x + offset, rect.bottom)
            end = (rect.x + offset + TILE, rect.y)
            pygame.draw.line(self.screen, (20, 33, 48), start, end, 1)

        pulse = pygame.Rect(rect.x + 11, rect.y + 11, rect.w - 22, rect.h - 22)
        pygame.draw.rect(self.screen, (33, 80, 105), pulse, 1, border_radius=4)
        pygame.draw.circle(self.screen, (57, 175, 190), rect.center, 3)
        draw_center(self.screen, "?", FONT_SM, (92, 124, 150), rect)

    def draw_boss_danger(self, rect):
        warning = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        pygame.draw.rect(warning, (210, 35, 48, 88), (0, 0, TILE, TILE))
        pygame.draw.rect(warning, (255, 118, 118, 125), (4, 4, TILE - 8, TILE - 8), 2)
        pygame.draw.line(warning, (255, 90, 90, 130), (8, 8), (TILE - 8, TILE - 8), 2)
        pygame.draw.line(warning, (255, 90, 90, 130), (TILE - 8, 8), (8, TILE - 8), 2)
        self.screen.blit(warning, rect.topleft)

    def draw_goal_beacon(self, rect):
        self.draw_delivery_point(rect, "G", "core")
        pygame.draw.circle(self.screen, (178, 123, 255), rect.center, 20, 1)
        pygame.draw.circle(self.screen, (77, 194, 255), rect.center, 16, 1)

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
        elif kind == "sensor":
            color = (82, 220, 145)
            pygame.draw.rect(self.screen, (18, 45, 38), (rect.centerx - 13, rect.centery - 10, 26, 20), border_radius=5)
            pygame.draw.rect(self.screen, color, (rect.centerx - 13, rect.centery - 10, 26, 20), 2, border_radius=5)
            pygame.draw.circle(self.screen, color, rect.center, 4)
            pygame.draw.arc(self.screen, (166, 255, 207), (rect.centerx - 11, rect.centery - 11, 22, 22), 3.7, 5.7, 2)
            pygame.draw.arc(self.screen, (166, 255, 207), (rect.centerx - 17, rect.centery - 17, 34, 34), 3.7, 5.7, 1)
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
        elif self.stage == 4:
            x, y = belief_grid_to_screen(row, col, self.active_belief_map())
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

    def draw_boss(self):
        row, col = self.boss
        x, y = grid_to_screen(row, col)
        cx, cy = x + TILE // 2, y + TILE // 2

        if self.boss_image:
            rect = self.boss_image.get_rect(midbottom=(cx, y + TILE + 4))
            pygame.draw.ellipse(self.screen, (2, 3, 6), (cx - 35, y + TILE - 5, 70, 13))
            self.screen.blit(self.boss_image, rect)
            return

        dark = (24, 22, 25)
        mid = (54, 48, 52)
        edge = (113, 102, 104)
        glow = (255, 205, 82)
        red = (183, 52, 62)

        pygame.draw.ellipse(self.screen, (2, 3, 6), (cx - 30, cy + 20, 60, 14))

        pygame.draw.circle(self.screen, dark, (cx - 22, cy - 1), 13)
        pygame.draw.circle(self.screen, dark, (cx + 22, cy - 1), 13)
        pygame.draw.circle(self.screen, edge, (cx - 22, cy - 1), 13, 2)
        pygame.draw.circle(self.screen, edge, (cx + 22, cy - 1), 13, 2)

        pygame.draw.line(self.screen, dark, (cx - 16, cy + 9), (cx - 28, cy + 22), 8)
        pygame.draw.line(self.screen, dark, (cx + 16, cy + 9), (cx + 28, cy + 22), 8)
        pygame.draw.circle(self.screen, mid, (cx - 31, cy + 25), 7)
        pygame.draw.circle(self.screen, mid, (cx + 31, cy + 25), 7)

        body = [
            (cx, cy - 10),
            (cx + 18, cy + 3),
            (cx + 12, cy + 26),
            (cx, cy + 34),
            (cx - 12, cy + 26),
            (cx - 18, cy + 3),
        ]
        pygame.draw.polygon(self.screen, dark, body)
        pygame.draw.polygon(self.screen, edge, body, 2)
        pygame.draw.circle(self.screen, mid, (cx, cy + 11), 11)
        pygame.draw.circle(self.screen, edge, (cx, cy + 11), 11, 2)

        head = pygame.Rect(cx - 13, cy - 30, 26, 22)
        pygame.draw.rect(self.screen, dark, head, border_radius=8)
        pygame.draw.rect(self.screen, edge, head, 2, border_radius=8)
        pygame.draw.circle(self.screen, glow, (cx - 5, cy - 18), 3)
        pygame.draw.circle(self.screen, glow, (cx + 5, cy - 18), 3)
        pygame.draw.line(self.screen, red, (cx - 7, cy - 11), (cx + 7, cy - 11), 2)

        pygame.draw.line(self.screen, dark, (cx - 9, cy + 28), (cx - 18, cy + 43), 8)
        pygame.draw.line(self.screen, dark, (cx + 9, cy + 28), (cx + 18, cy + 43), 8)
        pygame.draw.rect(self.screen, mid, (cx - 26, cy + 39, 16, 7), border_radius=3)
        pygame.draw.rect(self.screen, mid, (cx + 10, cy + 39, 16, 7), border_radius=3)

    def draw_panel(self):
        panel = pygame.Rect(PANEL_X, 72, PANEL_W, 700)
        pygame.draw.rect(self.screen, (7, 10, 16), panel.move(0, 6), border_radius=14)
        pygame.draw.rect(self.screen, COLORS["panel"], panel, border_radius=14)
        pygame.draw.rect(self.screen, (80, 95, 120), panel, 2, border_radius=14)
        draw_text(self.screen, "Bang dieu khien", FONT_MD, COLORS["text"], (panel.x + 24, panel.y + 24))
        map_line = f"LEVEL {self.stage}"
        draw_text(self.screen, map_line, FONT_SM, COLORS["muted"], (panel.x + 24, panel.y + 58))

        info = [
            f"Thuat toan dang chon: {self.algorithm}",
        ]
        y = panel.y + 92
        for line in info:
            draw_text(self.screen, line, FONT_SM, COLORS["text"], (panel.x + 24, y))
            y += 24

        draw_text(self.screen, "Chon thuat toan", FONT, COLORS["text"], (panel.x + 24, panel.y + 136))

        mouse = pygame.mouse.get_pos()
        for button in self.buttons:
            selected = button in self.algo_buttons and button.label == self.algorithm
            button.draw(self.screen, mouse, selected)

        status_box = pygame.Rect(panel.x + 24, panel.y + 316, panel.w - 48, 112)
        pygame.draw.rect(self.screen, COLORS["panel_2"], status_box, border_radius=10)
        pygame.draw.rect(self.screen, (80, 95, 120), status_box, 1, border_radius=10)
        if self.stage == 2:
            draw_text(self.screen, f"Thoi gian chay: {self.algorithm_time * 1000:.2f} ms", FONT_SM, COLORS["text"], (status_box.x + 10, status_box.y + 8))
            draw_text(self.screen, f"Node da xet: {self.nodes_checked}", FONT_SM, COLORS["text"], (status_box.x + 10, status_box.y + 30))
            draw_text(self.screen, "Pin", FONT_SM, COLORS["muted"], (status_box.x + 10, status_box.y + 54))
            draw_battery_bar(
                self.screen,
                status_box.x + 48,
                status_box.y + 51,
                150,
                22,
                self.battery,
                self.max_battery(),
                COLORS,
                FONT_XS,
            )
            draw_text(self.screen, f"Pin da tieu: {self.energy_used}", FONT_SM, COLORS["text"], (status_box.x + 10, status_box.y + 82))
        else:
            draw_text(self.screen, f"Thoi gian chay: {self.algorithm_time * 1000:.2f} ms", FONT_SM, COLORS["text"], (status_box.x + 10, status_box.y + 28))
            draw_text(self.screen, f"Node da xet: {self.nodes_checked}", FONT_SM, COLORS["text"], (status_box.x + 10, status_box.y + 58))
            draw_text(self.screen, f"So buoc: {self.solution_steps}", FONT_SM, COLORS["text"], (status_box.x + 10, status_box.y + 88))

        if self.stage != 5:
            path_box = pygame.Rect(panel.x + 24, panel.y + 448, panel.w - 48, 58)
            pygame.draw.rect(self.screen, COLORS["panel_2"], path_box, border_radius=10)
            pygame.draw.rect(self.screen, (80, 95, 120), path_box, 1, border_radius=10)
            recent = self.path[-4:]
            recent_text = " -> ".join([f"({r},{c})" for r, c in recent])
            draw_text(self.screen, "Cac o vua di:", FONT_SM, COLORS["muted"], (path_box.x + 10, path_box.y + 8))
            for i, line in enumerate(wrap_text(recent_text, FONT_SM, path_box.w - 20)[:2]):
                draw_text(self.screen, line, FONT_SM, COLORS["text"], (path_box.x + 10, path_box.y + 28 + i * 18))

        if self.stage == 5:
            delivery_y = panel.y + 448
            delivery_h = 172
        else:
            delivery_y = panel.y + 522
            delivery_h = 96
        delivery_box = pygame.Rect(panel.x + 24, delivery_y, panel.w - 48, delivery_h)
        pygame.draw.rect(self.screen, COLORS["panel_2"], delivery_box, border_radius=10)
        pygame.draw.rect(self.screen, (80, 95, 120), delivery_box, 1, border_radius=10)

        def draw_delivery_badges(deliveries, delivered_set, start_y):
            count = len(deliveries)
            gap = 68 if count >= 5 else 86
            for i, (label, pos, kind) in enumerate(deliveries):
                x = delivery_box.x + 10 + i * gap
                y = start_y
                color = ITEM_COLORS.get(kind, COLORS["cyan"])
                fill = color if label in delivered_set else COLORS["panel"]
                pygame.draw.rect(self.screen, fill, (x, y, 28, 22), border_radius=6)
                pygame.draw.rect(self.screen, color, (x, y, 28, 22), 2, border_radius=6)
                draw_center(self.screen, label, FONT_BADGE, COLORS["text"], pygame.Rect(x, y, 28, 22))
                if label in delivered_set:
                    pygame.draw.line(self.screen, COLORS["green"], (x + 5, y + 11), (x + 12, y + 18), 2)
                    pygame.draw.line(self.screen, COLORS["green"], (x + 12, y + 18), (x + 25, y + 4), 2)

        if self.stage == 3:
            delivered = {"G"} if self.result_message == "Hoan thanh" else set()
            draw_text(self.screen, "Hang can giao:", FONT_SM, COLORS["muted"], (delivery_box.x + 10, delivery_box.y + 7))
            draw_delivery_badges([("G", LOCAL_MAP["goal"], "core")], delivered, delivery_box.y + 34)
        elif self.stage == 4:
            delivered = {"G"} if self.result_message == "Hoan thanh" else set()
            draw_text(self.screen, "Hang can giao:", FONT_SM, COLORS["muted"], (delivery_box.x + 10, delivery_box.y + 7))
            draw_delivery_badges([("G", self.active_belief_map()["goal"], "core")], delivered, delivery_box.y + 34)
        elif self.stage == 5:
            draw_text(self.screen, "Hang can giao:", FONT_SM, COLORS["muted"], (delivery_box.x + 10, delivery_box.y + 7))
            draw_delivery_badges(CSP_MAP["delivery"], self.delivered, delivery_box.y + 34)
            draw_text(self.screen, "Rang buoc:", FONT_SM, COLORS["muted"], (delivery_box.x + 10, delivery_box.y + 68))
            for i, (left, rule, right, text) in enumerate(CSP_MAP["constraints"]):
                if rule == "before":
                    line = f"{left} truoc {right}"
                elif rule == "not_last":
                    line = f"{left} khong cuoi"
                else:
                    line = f"{left} khong dau"
                col = i // 4
                row = i % 4
                x = delivery_box.x + 12 + col * 170
                y = delivery_box.y + 90 + row * 18
                draw_text(self.screen, line, FONT_XS, COLORS["text"], (x, y))
        elif self.stage == 6:
            draw_text(self.screen, "Hang can giao:", FONT_SM, COLORS["muted"], (delivery_box.x + 10, delivery_box.y + 7))
            draw_delivery_badges(BOSS_MAP["delivery"], self.boss_delivered, delivery_box.y + 34)
            draw_text(self.screen, "Di vao vung do cua boss la thua", FONT_XS, COLORS["muted"], (delivery_box.x + 10, delivery_box.y + 78))
        else:
            draw_text(self.screen, "Hang can giao:", FONT_SM, COLORS["muted"], (delivery_box.x + 10, delivery_box.y + 7))
            draw_delivery_badges(self.current_map["delivery"], self.delivered, delivery_box.y + 34)

        if self.stage == 5:
            log_box = pygame.Rect(panel.x + 24, panel.bottom - 70, panel.w - 48, 48)
        else:
            log_box = pygame.Rect(panel.x + 24, panel.bottom - 78, panel.w - 48, 58)
        pygame.draw.rect(self.screen, COLORS["panel_2"], log_box, border_radius=10)
        pygame.draw.rect(self.screen, (80, 95, 120), log_box, 1, border_radius=10)
        for i, line in enumerate(wrap_text(self.message, FONT_SM, log_box.w - 20)[:2]):
            draw_text(self.screen, line, FONT_SM, COLORS["text"], (log_box.x + 10, log_box.y + 9 + i * 20))
