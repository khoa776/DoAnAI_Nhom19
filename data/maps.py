from config import MAP_X, MAP_Y, TILE

# F = floor, X = box, W = wall, . = hole/empty/void.
BATTERY_MAX_STAGE2 = 30

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
