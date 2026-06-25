from algorithms.search_common import expand_state, get_all_labels, is_goal, make_start_state


def dfs(game_map, robot_pos, delivered, max_depth=180):
    goal_labels = get_all_labels(game_map)
    start_state = make_start_state(game_map, robot_pos, delivered)

    stack = []
    stack.append((start_state, [robot_pos]))

    visited = set()
    nodes = 0

    while stack:
        state, path = stack.pop()

        if state in visited:
            continue

        visited.add(state)

        if is_goal(state, goal_labels):
            return path, nodes

        if len(path) >= max_depth:
            continue

        neighbors = expand_state(game_map, state)
        neighbors.reverse()

        frontier_states = []
        for item in stack:
            frontier_states.append(item[0])

        for new_state in neighbors:
            nodes += 1

            if new_state not in visited and new_state not in frontier_states:
                nr, nc = new_state[0], new_state[1]
                stack.append((new_state, path + [(nr, nc)]))
                frontier_states.append(new_state)

    return None, nodes
