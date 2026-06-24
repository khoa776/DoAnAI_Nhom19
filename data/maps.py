from config import MAP_X, MAP_Y, TILE

# F = floor, X = metal bridge, W = wall, D = door, . = empty/void.
LAB_MAP = [
    "WWWWWWWWWWXWWWWWWWWW",
    "WFFFFFFFFFXXXFFFFFFW",
    "WFFFFFFFFFXXXFFFFFFW",
    "WFFFFXXXFFXXXFFXXXFW",
    "WFFFFXFFFFXFFFFXFFFW",
    "DFFFFX....X....XFFFD",
    "WFFFFXFFFFXFFFFXFFFW",
    "WFFFFXXXFFXXXFFXXXFW",
    "WFFFFFFFFFXXXFFFFFFW",
    "WFFFFFFFFFXXXFFFFFFW",
    "WWWWWWWWWWXWWWWWWWWW",
]

START_POS = [2, 2]


def grid_to_screen(row, col):
    return MAP_X + col * TILE, MAP_Y + row * TILE


def in_bounds(row, col):
    return 0 <= row < len(LAB_MAP) and 0 <= col < len(LAB_MAP[0])


def is_walkable(row, col):
    if not in_bounds(row, col):
        return False
    return LAB_MAP[row][col] in "FXD"
