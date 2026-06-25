from algorithms.search_common import get_all_labels, get_delivery_at
from data.maps import BATTERY_MAX_STAGE2, is_charger, is_walkable, tile_cost


def make_start_state(game_map, robot_pos, battery, delivered):
    row, col = robot_pos
    new_delivered = set(delivered)

    label = get_delivery_at(game_map, row, col)
    if label:
        new_delivered.add(label)

    return (row, col, battery, tuple(sorted(new_delivered)))


def is_goal(state, goal_labels):
    delivered = state[3]
    return tuple(sorted(delivered)) == goal_labels


def heuristic(game_map, state):
    row, col, battery, delivered = state
    delivered_set = set(delivered)
    distances = []

    for label, pos, kind in game_map["delivery"]:
        if label not in delivered_set:
            goal_row, goal_col = pos
            distance = abs(row - goal_row) + abs(col - goal_col)
            distances.append(distance)

    if not distances:
        return 0

    return min(distances)


def expand_state(game_map, state):
    row, col, battery, delivered = state
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    result = []

    for dr, dc in moves:
        nr = row + dr
        nc = col + dc

        if is_walkable(game_map, nr, nc):
            cost = tile_cost(game_map, nr, nc)

            if battery >= cost:
                new_battery = battery - cost

                if is_charger(game_map, nr, nc):
                    new_battery = BATTERY_MAX_STAGE2

                new_delivered = set(delivered)
                label = get_delivery_at(game_map, nr, nc)
                if label:
                    new_delivered.add(label)

                new_state = (nr, nc, new_battery, tuple(sorted(new_delivered)))
                result.append((new_state, cost))

    return result
