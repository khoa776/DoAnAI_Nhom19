from collections import deque

from algorithms.search_common import expand_state, get_all_labels, is_goal, make_start_state


def bfs(game_map, robot_pos, delivered):
    goal_labels = get_all_labels(game_map)
    start_state = make_start_state(game_map, robot_pos, delivered)

    frontier = deque()
    frontier.append((start_state, [robot_pos]))

    visited = set()

    nodes = 0

    while frontier:
        state, path = frontier.popleft()

        if state in visited:
            continue

        visited.add(state)

        if is_goal(state, goal_labels):
            return path, nodes

        frontier_states = []
        for item in frontier:
            frontier_states.append(item[0])

        for new_state in expand_state(game_map, state):
            nodes += 1

            if new_state not in visited and new_state not in frontier_states:
                nr, nc = new_state[0], new_state[1]
                frontier.append((new_state, path + [(nr, nc)]))
                frontier_states.append(new_state)

    return None, nodes
