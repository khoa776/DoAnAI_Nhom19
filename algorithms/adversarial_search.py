def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def in_boss_danger(robot, boss):
    return abs(robot[0] - boss[0]) <= 1 and abs(robot[1] - boss[1]) <= 1


def is_free(game_map, row, col):
    grid = game_map["grid"]

    if row < 0 or row >= len(grid):
        return False
    if col < 0 or col >= len(grid[0]):
        return False
    if (row, col) in game_map["laser_cells"]:
        return False

    tile = grid[row][col]
    return tile != "W" and tile != "X" and tile != "."


def get_moves(game_map, pos):
    row, col = pos
    moves = []

    for dr, dc in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
        nr = row + dr
        nc = col + dc
        if is_free(game_map, nr, nc):
            moves.append((nr, nc))

    if not moves:
        moves.append(pos)

    return moves


def delivery_positions(game_map):
    result = {}
    for label, pos, kind in game_map["delivery"]:
        result[label] = pos
    return result


def update_delivered(game_map, robot, delivered):
    delivered = set(delivered)
    for label, pos, kind in game_map["delivery"]:
        if robot == pos:
            delivered.add(label)
    return tuple(sorted(delivered))


def nearest_delivery_distance(game_map, robot, delivered):
    best = 999

    for label, pos, kind in game_map["delivery"]:
        if label not in delivered:
            dist = manhattan(robot, pos)
            if dist < best:
                best = dist

    return best


def evaluate(game_map, robot, boss, delivered):
    if in_boss_danger(robot, boss):
        return -10000

    boss_near = max(abs(robot[0] - boss[0]), abs(robot[1] - boss[1]))

    total = len(game_map["delivery"])
    if len(delivered) == total:
        return 10000

    score = 0
    score += len(delivered) * 1500
    score -= nearest_delivery_distance(game_map, robot, delivered) * 60
    score += manhattan(robot, boss) * 2

    if boss_near == 2:
        score -= 650
    elif boss_near == 3:
        score -= 100

    return score


def minimax(game_map, robot, boss, delivered, depth, robot_turn, robot_steps_left=1, robot_steps_per_boss_turn=2):
    nodes = 1

    if depth == 0:
        return evaluate(game_map, robot, boss, delivered), nodes

    if len(delivered) == len(game_map["delivery"]) or in_boss_danger(robot, boss):
        return evaluate(game_map, robot, boss, delivered), nodes

    if robot_turn:
        best_score = -999999
        for move in get_moves(game_map, robot):
            new_delivered = update_delivered(game_map, move, delivered)
            if robot_steps_left > 1:
                score, child_nodes = minimax(game_map, move, boss, new_delivered, depth - 1, True, robot_steps_left - 1, robot_steps_per_boss_turn)
            else:
                score, child_nodes = minimax(game_map, move, boss, new_delivered, depth - 1, False, robot_steps_per_boss_turn, robot_steps_per_boss_turn)
            nodes += child_nodes
            if score > best_score:
                best_score = score
        return best_score, nodes

    best_score = 999999
    for move in get_moves(game_map, boss):
        score, child_nodes = minimax(game_map, robot, move, delivered, depth - 1, True, robot_steps_per_boss_turn, robot_steps_per_boss_turn)
        nodes += child_nodes
        if score < best_score:
            best_score = score

    return best_score, nodes


def minimax_robot_move(game_map, robot, boss, delivered, depth, recent_path=None, robot_steps_per_boss_turn=2):
    best_move = robot
    best_score = -999999
    nodes = 0
    if recent_path is None:
        recent_path = []

    for move in get_moves(game_map, robot):
        new_delivered = update_delivered(game_map, move, delivered)
        if robot_steps_per_boss_turn > 1:
            score, child_nodes = minimax(game_map, move, boss, new_delivered, depth - 1, True, robot_steps_per_boss_turn - 1, robot_steps_per_boss_turn)
        else:
            score, child_nodes = minimax(game_map, move, boss, new_delivered, depth - 1, False, robot_steps_per_boss_turn, robot_steps_per_boss_turn)
        nodes += child_nodes

        if move in recent_path and new_delivered == delivered:
            score -= 120

        if score > best_score:
            best_score = score
            best_move = move

    return best_move, nodes


def alpha_beta(game_map, robot, boss, delivered, depth, robot_turn, alpha, beta, robot_steps_left=1, robot_steps_per_boss_turn=2):
    nodes = 1

    if depth == 0:
        return evaluate(game_map, robot, boss, delivered), nodes

    if len(delivered) == len(game_map["delivery"]) or in_boss_danger(robot, boss):
        return evaluate(game_map, robot, boss, delivered), nodes

    if robot_turn:
        best_score = -999999
        for move in get_moves(game_map, robot):
            new_delivered = update_delivered(game_map, move, delivered)
            if robot_steps_left > 1:
                score, child_nodes = alpha_beta(game_map, move, boss, new_delivered, depth - 1, True, alpha, beta, robot_steps_left - 1, robot_steps_per_boss_turn)
            else:
                score, child_nodes = alpha_beta(game_map, move, boss, new_delivered, depth - 1, False, alpha, beta, robot_steps_per_boss_turn, robot_steps_per_boss_turn)
            nodes += child_nodes

            if score > best_score:
                best_score = score
            if best_score > alpha:
                alpha = best_score
            if beta <= alpha:
                break

        return best_score, nodes

    best_score = 999999
    for move in get_moves(game_map, boss):
        score, child_nodes = alpha_beta(game_map, robot, move, delivered, depth - 1, True, alpha, beta, robot_steps_per_boss_turn, robot_steps_per_boss_turn)
        nodes += child_nodes

        if score < best_score:
            best_score = score
        if best_score < beta:
            beta = best_score
        if beta <= alpha:
            break

    return best_score, nodes


def alpha_beta_robot_move(game_map, robot, boss, delivered, depth, recent_path=None, robot_steps_per_boss_turn=2):
    best_move = robot
    best_score = -999999
    nodes = 0
    alpha = -999999
    beta = 999999
    if recent_path is None:
        recent_path = []

    for move in get_moves(game_map, robot):
        new_delivered = update_delivered(game_map, move, delivered)
        if robot_steps_per_boss_turn > 1:
            score, child_nodes = alpha_beta(game_map, move, boss, new_delivered, depth - 1, True, alpha, beta, robot_steps_per_boss_turn - 1, robot_steps_per_boss_turn)
        else:
            score, child_nodes = alpha_beta(game_map, move, boss, new_delivered, depth - 1, False, alpha, beta, robot_steps_per_boss_turn, robot_steps_per_boss_turn)
        nodes += child_nodes

        if move in recent_path and new_delivered == delivered:
            score -= 120

        if score > best_score:
            best_score = score
            best_move = move
        if best_score > alpha:
            alpha = best_score

    return best_move, nodes


def boss_best_move(game_map, robot, boss, delivered):
    best_move = boss
    best_score = 999999

    for move in get_moves(game_map, boss):
        score = evaluate(game_map, robot, move, delivered)
        if score < best_score:
            best_score = score
            best_move = move

    return best_move


def make_adversarial_plan(game_map, algorithm="MINIMAX", depth=3, max_turns=90):
    robot = tuple(game_map["start"])
    boss = tuple(game_map["boss"])
    delivered = tuple()
    nodes = 0
    robot_steps_per_boss_turn = 2

    robot_path = [robot]
    boss_path = [boss]
    delivered_path = [delivered]

    for turn in range(max_turns):
        if len(delivered) == len(game_map["delivery"]):
            return robot_path, boss_path, delivered_path, nodes, True, "Hoan thanh"

        if in_boss_danger(robot, boss):
            return robot_path, boss_path, delivered_path, nodes, False, "Bi boss bat"

        recent_path = robot_path[-8:]

        if algorithm == "ALPHA-BETA":
            robot, new_nodes = alpha_beta_robot_move(game_map, robot, boss, delivered, depth, recent_path, robot_steps_per_boss_turn)
        else:
            robot, new_nodes = minimax_robot_move(game_map, robot, boss, delivered, depth, recent_path, robot_steps_per_boss_turn)
        nodes += new_nodes
        delivered = update_delivered(game_map, robot, delivered)
        robot_path.append(robot)

        if len(delivered) == len(game_map["delivery"]):
            boss_path.append(boss)
            delivered_path.append(delivered)
            return robot_path, boss_path, delivered_path, nodes, True, "Hoan thanh"

        # Robot di du so buoc quy dinh thi boss moi di 1 buoc.
        if turn % robot_steps_per_boss_turn == robot_steps_per_boss_turn - 1:
            boss = boss_best_move(game_map, robot, boss, delivered)

        boss_path.append(boss)
        delivered_path.append(delivered)

    return robot_path, boss_path, delivered_path, nodes, False, "Qua gioi han luot"


def make_minimax_plan(game_map, depth=3, max_turns=90):
    return make_adversarial_plan(game_map, "MINIMAX", depth, max_turns)


def make_alpha_beta_plan(game_map, depth=3, max_turns=90):
    return make_adversarial_plan(game_map, "ALPHA-BETA", depth, max_turns)
