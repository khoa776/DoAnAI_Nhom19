import random
from collections import deque


def get_labels(csp_map):
    labels = []
    for label, pos, kind in csp_map["delivery"]:
        labels.append(label)
    return labels


def get_delivery_pos(csp_map, label):
    for item_label, pos, kind in csp_map["delivery"]:
        if item_label == label:
            return pos
    return None


def consistent(value, assignment, constraints, total_count):
    if value in assignment:
        return False

    temp = assignment + [value]

    for left, rule, right, text in constraints:
        if rule == "before":
            if left in temp and right in temp:
                if temp.index(left) > temp.index(right):
                    return False

            if right in temp and left not in temp:
                return False

        elif rule == "not_first":
            if len(temp) == 1 and temp[0] == left:
                return False

        elif rule == "not_last":
            if len(temp) == total_count and temp[-1] == left:
                return False

    return True


def backtracking_order(csp_map):
    labels = get_labels(csp_map)
    constraints = csp_map["constraints"]
    nodes = 0

    def backtrack(assignment):
        nonlocal nodes

        if len(assignment) == len(labels):
            return assignment

        domain = []
        for label in labels:
            if label not in assignment:
                domain.append(label)

        random.shuffle(domain)

        for value in domain:
            nodes += 1

            if consistent(value, assignment, constraints, len(labels)):
                assignment.append(value)

                result = backtrack(assignment)
                if result is not None:
                    return result

                assignment.pop()

        return None

    result = backtrack([])
    return result, nodes


def forward_check(assignment, labels, constraints):
    if len(assignment) == len(labels):
        return True

    remaining = []
    for label in labels:
        if label not in assignment:
            remaining.append(label)

    for value in remaining:
        if consistent(value, assignment, constraints, len(labels)):
            return True

    return False


def forward_checking_order(csp_map):
    labels = get_labels(csp_map)
    constraints = csp_map["constraints"]
    nodes = 0

    def backtrack(assignment):
        nonlocal nodes

        if len(assignment) == len(labels):
            return assignment

        domain = []
        for label in labels:
            if label not in assignment:
                domain.append(label)

        random.shuffle(domain)

        for value in domain:
            nodes += 1

            if consistent(value, assignment, constraints, len(labels)):
                assignment.append(value)

                if forward_check(assignment, labels, constraints):
                    result = backtrack(assignment)
                    if result is not None:
                        return result

                assignment.pop()

        return None

    result = backtrack([])
    return result, nodes


def is_free(csp_map, row, col):
    grid = csp_map["grid"]

    if row < 0 or row >= len(grid):
        return False
    if col < 0 or col >= len(grid[0]):
        return False

    tile = grid[row][col]
    if (row, col) in csp_map.get("laser_cells", set()):
        return False

    return tile != "W" and tile != "X" and tile != "."


def bfs_path(csp_map, start, goal):
    frontier = deque()
    frontier.append((start, [start]))
    visited = set()

    while frontier:
        current, path = frontier.popleft()

        if current in visited:
            continue

        visited.add(current)

        if current == goal:
            return path

        row, col = current
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in moves:
            nr = row + dr
            nc = col + dc
            next_pos = (nr, nc)

            if is_free(csp_map, nr, nc) and next_pos not in visited:
                frontier.append((next_pos, path + [next_pos]))

    return None


def make_delivery_route(csp_map, order):
    current = tuple(csp_map["start"])
    route = [current]

    for label in order:
        goal = get_delivery_pos(csp_map, label)
        path = bfs_path(csp_map, current, goal)

        if path is None:
            return None

        route += path[1:]
        current = goal

    return route
