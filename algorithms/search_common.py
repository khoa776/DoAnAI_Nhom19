from data.maps import is_walkable


def get_all_labels(game_map):
    labels = []
    for label, pos, kind in game_map["delivery"]:
        labels.append(label)
    return tuple(sorted(labels))


def get_delivery_at(game_map, row, col):
    for label, pos, kind in game_map["delivery"]:
        if pos == (row, col):
            return label
    return None


def make_start_state(game_map, robot_pos, delivered):
    row, col = robot_pos
    new_delivered = set(delivered)
    label = get_delivery_at(game_map, row, col)
    if label:
        new_delivered.add(label)
    return (row, col, tuple(sorted(new_delivered)))


def is_goal(state, goal_labels):
    delivered = state[2]
    return tuple(sorted(delivered)) == goal_labels


def expand_state(game_map, state):
    row, col, delivered = state
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    result = []

    for dr, dc in moves:
        nr = row + dr
        nc = col + dc

        if is_walkable(game_map, nr, nc):
            new_delivered = set(delivered)
            label = get_delivery_at(game_map, nr, nc)
            if label:
                new_delivered.add(label)

            new_state = (nr, nc, tuple(sorted(new_delivered)))
            result.append(new_state)

    return result
