from config import MAP_X, MAP_Y, PANEL_X, TILE

# F = floor, X = box, W = wall, . = hole/empty/void.
BATTERY_MAX_STAGE2 = 30

LOCAL_MAP = {
    "name": "Bay cuc bo",
    "grid": [
        "WWWWWWWWWWWWWWWWW",
        "WFFFFFFFFFFFFXXGW",
        "WFX.XXXFXFXXFFXFW",
        "WFFFFFXFFFFXFXFFW",
        "WFFX.XXXFXFXXFFFW",
        "WFFFFXFFFXFFFFFFW",
        "WFXFXXFX.FXFFXFFW",
        "WFFFFFFFFFFFFFFFW",
        "WFFFXFFFFFXFFXFFW",
        "WSFFFFFFFXFFFFFFW",
        "WWWWWWWWWWWWWWWWW",
    ],
    "start": (9, 1),
    "goal": (1, 15),
    "lasers": [((5, 5), (5, 9)), ((8, 4), (8, 10))],
}

BELIEF_MAP = {
    "name": "Kho mat tin hieu",
    "grid": [
        "WWWWWWWWWWWWWWWWWWWW",
        "WFFFFFFFFFFFFXFFFFFW",
        "WFFFFXFFFFF.FXFFFFFW",
        "WFFXFFFFXFFFFFFFXFFW",
        "WFFFFF....FFFFXFFFFW",
        "WFXFFFFFFFFFFFFFFXFW",
        "WFFFFXFFFFXFFFF.FFFW",
        "WFFFFFFFFFFFFXFFFFFW",
        "WFFXFFFF....FFFFXFFW",
        "WFFFFFFFFXFFFFFFFFFW",
        "WWWWWWWWWWWWWWWWWWWW",
    ],
    "start": [9, 2],
    "goal": (1, 17),
    "delivery": [("G", (1, 17), "core")],
    "lasers": [],
}

BELIEF_UNKNOWN_MAP = {
    "name": "Khu hang bi an",
    "grid": [
        "WWWWWWWWWWWWWWWWWWWW",
        "WFFFFFFFFFFXFFFFFFFW",
        "WFXFFF.FFFFXFFFFXFFW",
        "WFXFXXFFFFF.FFFFXFFW",
        "WFFFFFXFFFFFXXXFFFFW",
        "WFFFFF....FFFFFFFFFW",
        "WFXFFFFFXFFFFFXFFFFW",
        "WFFFFXFFFFFFF.FFFXFW",
        "WFFFFFXXXFFFFFXFFFFW",
        "WFFFFFFFFFFFFFXXFFFW",
        "WWWWWWWWWWWWWWWWWWWW",
    ],
    "start": [1, 2],
    "goal": (9, 17),
    "delivery": [("G", (9, 17), "core")],
    "lasers": [],
}

MAPS = [
    {
        "name": "Kho trung tam",
        "grid": [
            "WWWWWWWWWWWWWWWWWWWW",
            "WFFFFFFFFFFFFFFFFFFW",
            "WFFFFXFFFFFFFFFFFFFW",
            "WFFFFFFFXFFFFXFFFFFW",
            "WFFFFFFFFFF.FFFFFFFW",
            "WFFFFF....FFFFFFFFFW",
            "WFFFFXFFFFFFFFXFFFFW",
            "WFFF.FFFFFFFFFFFFFFW",
            "WFFFFFFXFFFFFFXFFFFW",
            "WFFFFFFFFXFF.FFFFFFW",
            "WWWWWWWWWWWWWWWWWWWW",
        ],
        "start": [2, 2],
        "chargers": [(2, 14), (8, 5), (8, 15)],
        "stage3_start": [(1, 1), (9, 18)],
        "cost2": [(1, 8), (1, 9), (2, 8), (4, 8), (6, 9), (7, 14), (9, 14)],
        "delivery": [
            ("A", (1, 3), "medicine"),
            ("B", (1, 17), "computer"),
            ("C", (9, 2), "bolt"),
            ("D", (9, 17), "core"),
        ],
        "lasers": [((3, 8), (3, 13)), ((8, 7), (8, 14))],
    },
    {
        "name": "Hang doc laser",
        "grid": [
            "WWWWWWWWWWWWWWWWWWWW",
            "WFFFFFFFFFFFFFFFFFFW",
            "WFFFFXFFFFFFXFFFFFFW",
            "WFFFFFFFFFFFFFFFFXFW",
            "WFF....FFFFFFFFFFFFW",
            "WFFFFFFFFXFFFFFFFFFW",
            "WFFFFFFF.X.FFFFFFFFW",
            "WFXFFXFFFFFFXFFFFXFW",
            "WFFFFFFFFFFFF....FFW",
            "WFFFFFFFFFFFFFFFFFFW",
            "WWWWWWWWWWWWWWWWWWWW",
        ],
        "start": [8, 2],
        "chargers": [(1, 10), (5, 15), (9, 5)],
        "stage3_start": [(1, 1), (9, 18)],
        "cost2": [(1, 7), (2, 8), (3, 9), (5, 4), (6, 14), (8, 10), (9, 13)],
        "delivery": [
            ("A", (1, 4), "medicine"),
            ("B", (1, 16), "computer"),
            ("C", (9, 3), "bolt"),
            ("D", (9, 17), "core"),
        ],
        "lasers": [((2, 5), (7, 5)), ((2, 12), (7, 12))],
    },
    {
        "name": "Vong ngoai",
        "grid": [
            "WWWWWWWWWWWWWWWWWWWW",
            "WFFFFFFFFFFFFFFFFFFW",
            "WFFFFFFFF....FFFFFFW",
            "WFXFFFFFFFFFFXFFFXFW",
            "WFFFFFFXFFFFFFFFFFFW",
            "WFFFFF....FFFFXFFFFW",
            "WFFFFFFFFFFFFFFFFFFW",
            "WFFFFFFXFFFFFFFFXFFW",
            "WFFFFFFFF....FFFFFFW",
            "WFFFFFFFFFFFFFFFFFFW",
            "WWWWWWWWWWWWWWWWWWWW",
        ],
        "start": [1, 10],
        "chargers": [(2, 5), (6, 15), (9, 9)],
        "stage3_start": [(1, 1), (9, 18)],
        "cost2": [(1, 6), (1, 7), (4, 5), (4, 14), (6, 8), (6, 9), (9, 12)],
        "delivery": [
            ("A", (1, 2), "medicine"),
            ("B", (1, 17), "computer"),
            ("C", (9, 2), "bolt"),
            ("D", (9, 17), "core"),
        ],
        "lasers": [((3, 2), (3, 13)), ((7, 7), (7, 16))],
    },
]


def make_laser_cells(laser_lines):
    cells = set()
    for start, end in laser_lines:
        r1, c1 = start
        r2, c2 = end
        if r1 == r2:
            step = 1 if c2 > c1 else -1
            for c in range(c1 + step, c2, step):
                cells.add((r1, c))
        elif c1 == c2:
            step = 1 if r2 > r1 else -1
            for r in range(r1 + step, r2, step):
                cells.add((r, c1))
    return cells


for game_map in MAPS:
    game_map["laser_cells"] = make_laser_cells(game_map["lasers"])

LOCAL_MAP["laser_cells"] = make_laser_cells(LOCAL_MAP["lasers"])
BELIEF_MAP["laser_cells"] = make_laser_cells(BELIEF_MAP["lasers"])
BELIEF_UNKNOWN_MAP["laser_cells"] = make_laser_cells(BELIEF_UNKNOWN_MAP["lasers"])


def get_map(index):
    return MAPS[index % len(MAPS)]


def map_count():
    return len(MAPS)


def grid_to_screen(row, col):
    return MAP_X + col * TILE, MAP_Y + row * TILE


def in_bounds(game_map, row, col):
    grid = game_map["grid"]
    return 0 <= row < len(grid) and 0 <= col < len(grid[0])


def is_walkable(game_map, row, col):
    if not in_bounds(game_map, row, col):
        return False
    return game_map["grid"][row][col] == "F" and not is_laser(game_map, row, col)


def is_charger(game_map, row, col):
    return (row, col) in game_map["chargers"]


def is_cost2(game_map, row, col):
    return (row, col) in game_map["cost2"]


def tile_cost(game_map, row, col):
    if is_cost2(game_map, row, col):
        return 2
    return 1


def is_laser(game_map, row, col):
    return (row, col) in game_map["laser_cells"]


def local_grid_to_screen(row, col):
    cols = len(LOCAL_MAP["grid"][0])
    start_x = (PANEL_X - cols * TILE) // 2
    return start_x + col * TILE, MAP_Y + row * TILE


def is_local_walkable(row, col):
    grid = LOCAL_MAP["grid"]

    if row < 0 or row >= len(grid):
        return False
    if col < 0 or col >= len(grid[0]):
        return False

    if (row, col) in LOCAL_MAP["laser_cells"]:
        return False

    return grid[row][col] != "W" and grid[row][col] != "X" and grid[row][col] != "."


def is_belief_walkable(row, col, game_map=None):
    if game_map is None:
        game_map = BELIEF_MAP

    grid = game_map["grid"]

    if row < 0 or row >= len(grid):
        return False
    if col < 0 or col >= len(grid[0]):
        return False

    tile = grid[row][col]
    return tile != "W" and tile != "X" and tile != "."
