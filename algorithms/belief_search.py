from collections import deque


# Thu tu huong di dung chung cho ca BFS va DFS:
# trai, phai, len, xuong.
MOVE_ORDER = [(0, -1), (0, 1), (-1, 0), (1, 0)]


def make_known_map(game_map, know_goal=False):
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


def is_known_walkable(known_map, row, col):
    if row < 0 or row >= len(known_map):
        return False
    if col < 0 or col >= len(known_map[0]):
        return False

    return known_map[row][col] == "F" or known_map[row][col] == "G"


def reveal_area(game_map, known_map, pos, radius=1, know_goal=False):
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
        goal_row, goal_col = goal
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


def is_frontier_cell(known_map, row, col):
    if not is_known_walkable(known_map, row, col):
        return False

    for dr, dc in MOVE_ORDER:
        nr = row + dr
        nc = col + dc

        if 0 <= nr < len(known_map) and 0 <= nc < len(known_map[0]):
            if known_map[nr][nc] == "?":
                return True

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

        frontier_positions = []
        for item in frontier:
            frontier_positions.append(item[0])

        row, col = current
        for dr, dc in MOVE_ORDER:
            nr = row + dr
            nc = col + dc
            new_pos = (nr, nc)

            if is_known_walkable(known_map, nr, nc):
                nodes += 1
                if new_pos not in visited and new_pos not in frontier_positions:
                    frontier.append((new_pos, path + [new_pos]))
                    frontier_positions.append(new_pos)

    return None, nodes


def dfs_on_known_map(known_map, start, goal):
    frontier = []
    frontier.append((start, [start]))
    visited = set()
    nodes = 0

    while frontier:
        current, path = frontier.pop()

        if current in visited:
            continue

        visited.add(current)

        if current == goal:
            return path, nodes

        frontier_positions = []
        for item in frontier:
            frontier_positions.append(item[0])

        row, col = current
        # DFS lay phan tu cuoi ra truoc, nen them nguoc lai de thu tu thuc te
        # van la trai, phai, len, xuong.
        for dr, dc in reversed(MOVE_ORDER):
            nr = row + dr
            nc = col + dc
            new_pos = (nr, nc)

            if is_known_walkable(known_map, nr, nc):
                nodes += 1
                if new_pos not in visited and new_pos not in frontier_positions:
                    frontier.append((new_pos, path + [new_pos]))
                    frontier_positions.append(new_pos)

    return None, nodes


def find_frontier_bfs(known_map, start):
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

        frontier_positions = []
        for item in frontier:
            frontier_positions.append(item[0])

        for dr, dc in MOVE_ORDER:
            nr = row + dr
            nc = col + dc
            new_pos = (nr, nc)

            if is_known_walkable(known_map, nr, nc):
                nodes += 1
                if new_pos not in visited and new_pos not in frontier_positions:
                    frontier.append((new_pos, path + [new_pos]))
                    frontier_positions.append(new_pos)

    return None, nodes


def find_frontier_dfs(known_map, start):
    frontier = []
    frontier.append((start, [start]))
    visited = set()
    nodes = 0

    while frontier:
        current, path = frontier.pop()

        if current in visited:
            continue

        visited.add(current)

        row, col = current
        if is_frontier_cell(known_map, row, col) and current != start:
            return path, nodes

        frontier_positions = []
        for item in frontier:
            frontier_positions.append(item[0])

        for dr, dc in reversed(MOVE_ORDER):
            nr = row + dr
            nc = col + dc
            new_pos = (nr, nc)

            if is_known_walkable(known_map, nr, nc):
                nodes += 1
                if new_pos not in visited and new_pos not in frontier_positions:
                    frontier.append((new_pos, path + [new_pos]))
                    frontier_positions.append(new_pos)

    return None, nodes


def unknown_goal_belief_search(game_map, start, max_steps=320, use_dfs=False):
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
            if use_dfs:
                goal_path, checked = dfs_on_known_map(known_map, current, goal)
            else:
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

        if use_dfs:
            frontier_path, checked = find_frontier_dfs(known_map, current)
        else:
            frontier_path, checked = find_frontier_bfs(known_map, current)
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


def unknown_goal_dfs_search(game_map, start, max_steps=320):
    return unknown_goal_belief_search(game_map, start, max_steps, True)


def known_goal_belief_search(game_map, start, max_steps=320):
    # Giu ham nay de cac file cu import khong bi loi.
    return unknown_goal_belief_search(game_map, start, max_steps, False)[:4]
