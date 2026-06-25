from algorithms.informed_common import expand_state, get_all_labels, heuristic, is_goal, make_start_state


def choose_min_f(frontier):
    best_index = 0

    for i in range(1, len(frontier)):
        if frontier[i]["f"] < frontier[best_index]["f"]:
            best_index = i
        elif frontier[i]["f"] == frontier[best_index]["f"]:
            if frontier[i]["h"] < frontier[best_index]["h"]:
                best_index = i

    return frontier.pop(best_index)


def find_in_frontier(frontier, state):
    for node in frontier:
        if node["state"] == state:
            return node
    return None


def astar_search(game_map, robot_pos, battery, delivered):
    goal_labels = get_all_labels(game_map)
    start_state = make_start_state(game_map, robot_pos, battery, delivered)
    start_h = heuristic(game_map, start_state)

    start_node = {
        "state": start_state,
        "path": [robot_pos],
        "g": 0,
        "h": start_h,
        "f": start_h,
    }

    frontier = [start_node]
    reached = {}
    nodes = 0

    while frontier:
        current = choose_min_f(frontier)
        state = current["state"]

        if is_goal(state, goal_labels):
            return current["path"], nodes, current["g"]

        reached[state] = current["g"]

        for new_state, step_cost in expand_state(game_map, state):
            nodes += 1
            new_g = current["g"] + step_cost

            if new_state in reached:
                if new_g >= reached[new_state]:
                    continue
                else:
                    del reached[new_state]

            old_node = find_in_frontier(frontier, new_state)
            new_h = heuristic(game_map, new_state)
            new_f = new_g + new_h
            nr, nc = new_state[0], new_state[1]

            if old_node:
                if new_g < old_node["g"]:
                    old_node["g"] = new_g
                    old_node["h"] = new_h
                    old_node["f"] = new_f
                    old_node["path"] = current["path"] + [(nr, nc)]
            else:
                new_node = {
                    "state": new_state,
                    "path": current["path"] + [(nr, nc)],
                    "g": new_g,
                    "h": new_h,
                    "f": new_f,
                }
                frontier.append(new_node)

    return None, nodes, 0
