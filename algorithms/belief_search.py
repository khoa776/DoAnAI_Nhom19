from collections import deque


def make_known_map(game_map, know_goal=True):
    grid = game_map["grid"]
    known = []

    for row in grid:
        known.append(["?"] * len(row))

    if know_goal:
        goal_row, goal_col = game_map["goal"]
        known[goal_row][goal_col] = "G"

    return known


def make_possible_goals(game_map, start):
    grid = game_map["grid"]
    possible = set()

    for r in range(1, len(grid) - 1):
        for c in range(1, len(grid[0]) - 1):
            if (r, c) != start:
                possible.add((r, c))

    return possible


def in_bounds(game_map, row, col):
    grid = game_map["grid"]
    return 0 <= row < len(grid) and 0 <= col < len(grid[0])


def is_real_walkable(game_map, row, col):
    if not in_bounds(game_map, row, col):
        return False

    tile = game_map["grid"][row][col]
    return tile != "W" and tile != "X" and tile != "."


def is_known_walkable(known_map, row, col):
    if row < 0 or row >= len(known_map):
        return False
    if col < 0 or col >= len(known_map[0]):
        return False

    return known_map[row][col] == "F" or known_map[row][col] == "G"


def reveal_area(game_map, known_map, pos, radius=1, know_goal=True):
    row, col = pos
    count = 0
    goal = game_map["goal"]
    found_goal = False

    for r in range(row - radius, row + radius + 1):
        for c in range(col - radius, col + radius + 1):
            if in_bounds(game_map, r, c):
                if known_map[r][c] == "?":
                    count += 1

                if (r, c) == goal:
                    known_map[r][c] = "G"
                    found_goal = True
                else:
                    known_map[r][c] = game_map["grid"][r][c]

    if know_goal:
        goal_row, goal_col = game_map["goal"]
        known_map[goal_row][goal_col] = "G"
        found_goal = True

    return count, found_goal


def update_possible_goals(game_map, known_map, possible_goals):
    goal = game_map["goal"]

    if known_map[goal[0]][goal[1]] == "G":
        possible_goals.clear()
        possible_goals.add(goal)
        return True

    remove_list = []
    for pos in possible_goals:
        row, col = pos
        if known_map[row][col] != "?":
            remove_list.append(pos)

    for pos in remove_list:
        possible_goals.remove(pos)

    return False


def bfs_on_known_map(known_map, start, goal):
    frontier = deque()
    frontier.append((start, [start]))
    visited = set()
    nodes = 0

    while frontier:
        current, path = frontier.popleft()

        if current in visited:
            continue

        visited.add(current)

        if current == goal:
            return path, nodes

        row, col = current
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        frontier_positions = []
        for item in frontier:
            frontier_positions.append(item[0])

        for dr, dc in moves:
            nr = row + dr
            nc = col + dc
            new_pos = (nr, nc)

            if is_known_walkable(known_map, nr, nc):
                nodes += 1
                if new_pos not in visited and new_pos not in frontier_positions:
                    frontier.append((new_pos, path + [new_pos]))
                    frontier_positions.append(new_pos)

    return None, nodes


def is_frontier_cell(known_map, row, col):
    if not is_known_walkable(known_map, row, col):
        return False

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in moves:
        nr = row + dr
        nc = col + dc

        if 0 <= nr < len(known_map) and 0 <= nc < len(known_map[0]):
            if known_map[nr][nc] == "?":
                return True

    return False


def find_nearest_frontier(known_map, start):
    frontier = deque()
    frontier.append((start, [start]))
    visited = set()
    nodes = 0

    while frontier:
        current, path = frontier.popleft()

        if current in visited:
            continue

        visited.add(current)

        row, col = current
        if is_frontier_cell(known_map, row, col) and current != start:
            return path, nodes

        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        frontier_positions = []
        for item in frontier:
            frontier_positions.append(item[0])

        for dr, dc in moves:
            nr = row + dr
            nc = col + dc
            new_pos = (nr, nc)

            if is_known_walkable(known_map, nr, nc):
                nodes += 1
                if new_pos not in visited and new_pos not in frontier_positions:
                    frontier.append((new_pos, path + [new_pos]))
                    frontier_positions.append(new_pos)

    return None, nodes


def known_goal_belief_search(game_map, start, max_steps=220):
    known_map = make_known_map(game_map, True)
    current = start
    goal = game_map["goal"]
    path = [current]
    nodes = 0
    revealed = 0

    reveal_area(game_map, known_map, current, know_goal=True)

    while current != goal and len(path) < max_steps:
        goal_path, checked = bfs_on_known_map(known_map, current, goal)
        nodes += checked

        if goal_path:
            for step in goal_path[1:]:
                path.append(step)
                current = step
                new_cells, found_goal = reveal_area(game_map, known_map, current, know_goal=True)
                revealed += new_cells
            return path, nodes, revealed, True

        frontier_path, checked = find_nearest_frontier(known_map, current)
        nodes += checked

        if frontier_path is None:
            return path, nodes, revealed, False

        for step in frontier_path[1:]:
            path.append(step)
            current = step
            new_cells, found_goal = reveal_area(game_map, known_map, current, know_goal=True)
            revealed += new_cells

    return path, nodes, revealed, current == goal


def unknown_goal_belief_search(game_map, start, max_steps=260):
    known_map = make_known_map(game_map, False)
    possible_goals = make_possible_goals(game_map, start)
    current = start
    goal = game_map["goal"]
    path = [current]
    nodes = 0
    revealed = 0
    goal_seen = False

    new_cells, found_goal = reveal_area(game_map, known_map, current, know_goal=False)
    revealed += new_cells
    if found_goal:
        goal_seen = True
    update_possible_goals(game_map, known_map, possible_goals)

    while current != goal and len(path) < max_steps:
        if goal_seen:
            goal_path, checked = bfs_on_known_map(known_map, current, goal)
            nodes += checked

            if goal_path:
                for step in goal_path[1:]:
                    path.append(step)
                    current = step
                    new_cells, found_goal = reveal_area(game_map, known_map, current, know_goal=False)
                    revealed += new_cells
                    update_possible_goals(game_map, known_map, possible_goals)
                return path, nodes, revealed, True, len(possible_goals)

        frontier_path, checked = find_nearest_frontier(known_map, current)
        nodes += checked

        if frontier_path is None:
            return path, nodes, revealed, False, len(possible_goals)

        for step in frontier_path[1:]:
            path.append(step)
            current = step
            new_cells, found_goal = reveal_area(game_map, known_map, current, know_goal=False)
            revealed += new_cells
            if found_goal:
                goal_seen = True
            update_possible_goals(game_map, known_map, possible_goals)

            if current == goal:
                return path, nodes, revealed, True, len(possible_goals)

            if goal_seen:
                break

    return path, nodes, revealed, current == goal, len(possible_goals)
