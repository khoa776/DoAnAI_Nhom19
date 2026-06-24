from config import MAP_X, MAP_Y, TILE

# F = floor, X = box, W = wall, . = hole/empty/void.
LAB_MAP = [
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
]

START_POS = [2, 2]

BATTERY_MAX = 24

# Cac tram sac dat tren o san de sau nay thuat toan co the chon duong ghe sac.
CHARGERS = [
    (2, 14),
    (8, 5),
    (8, 15),
]

# Cac diem giao hang nam gan ria map.
DELIVERY_POINTS = [
    ("A", (1, 3), "medicine"),
    ("B", (1, 17), "computer"),
    ("C", (9, 2), "bolt"),
    ("D", (9, 17), "core"),
]

# Laser duoc tao giua 2 hop X cung hang/cot.
# Cac o nam giua 2 dau laser se khong di qua duoc.
LASER_LINES = [
    ((3, 8), (3, 13)),
    ((8, 7), (8, 14)),
]


def make_laser_cells():
    cells = set()
    for start, end in LASER_LINES:
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


LASER_CELLS = make_laser_cells()


def grid_to_screen(row, col):
    return MAP_X + col * TILE, MAP_Y + row * TILE


def in_bounds(row, col):
    return 0 <= row < len(LAB_MAP) and 0 <= col < len(LAB_MAP[0])


def is_walkable(row, col):
    if not in_bounds(row, col):
        return False
    return LAB_MAP[row][col] == "F" and not is_laser(row, col)


def is_charger(row, col):
    return (row, col) in CHARGERS


def is_laser(row, col):
    return (row, col) in LASER_CELLS
