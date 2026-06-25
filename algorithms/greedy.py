from algorithms.informed_common import expand_state, get_all_labels, heuristic, is_goal, make_start_state


def choose_min_h(frontier):
    best_index = 0

    for i in range(1, len(frontier)):
        if frontier[i]["h"] < frontier[best_index]["h"]:
            best_index = i

    return frontier.pop(best_index)


def state_base(state):
    row, col, battery, delivered = state
    return (row, col, delivered)


def has_better_battery(frontier, reached_battery, state):
    base = state_base(state)
    battery = state[2]

    if base in reached_battery and reached_battery[base] >= battery:
        return True

    for node in frontier:
        old_state = node["state"]
        if state_base(old_state) == base and old_state[2] >= battery:
            return True

    return False


def remove_weaker_frontier(frontier, state):
    base = state_base(state)
    battery = state[2]
    new_frontier = []

    for node in frontier:
        old_state = node["state"]
        if state_base(old_state) == base and old_state[2] < battery:
            continue
        new_frontier.append(node)

    return new_frontier


def greedy_search(game_map, robot_pos, battery, delivered):
    goal_labels = get_all_labels(game_map)
    start_state = make_start_state(game_map, robot_pos, battery, delivered)

    start_node = {
        "state": start_state,
        "path": [robot_pos],
        "g": 0,
        "h": heuristic(game_map, start_state),
    }

    frontier = [start_node]
    reached = set()
    reached_battery = {}
    nodes = 0

    while frontier:
        current = choose_min_h(frontier)
        state = current["state"]

        if is_goal(state, goal_labels):
            return current["path"], nodes, current["g"]

        reached.add(state)
        base = state_base(state)
        if base not in reached_battery or state[2] > reached_battery[base]:
            reached_battery[base] = state[2]

        frontier_states = []
        for item in frontier:
            frontier_states.append(item["state"])

        for new_state, step_cost in expand_state(game_map, state):
            nodes += 1

            if new_state not in reached and new_state not in frontier_states:
                if has_better_battery(frontier, reached_battery, new_state):
                    continue

                nr, nc = new_state[0], new_state[1]
                new_node = {
                    "state": new_state,
                    "path": current["path"] + [(nr, nc)],
                    "g": current["g"] + step_cost,
                    "h": heuristic(game_map, new_state),
                }
                frontier = remove_weaker_frontier(frontier, new_state)
                frontier.append(new_node)
                frontier_states.append(new_state)

    return None, nodes, 0
