import math
import random

from data.maps import is_local_walkable


def manhattan(pos, goal):
    row, col = pos
    goal_row, goal_col = goal
    return abs(row - goal_row) + abs(col - goal_col)


def get_neighbors(pos):
    row, col = pos
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    result = []

    for dr, dc in moves:
        nr = row + dr
        nc = col + dc

        if is_local_walkable(nr, nc):
            result.append((nr, nc))

    return result


def simple_hill_climbing(local_map, max_steps=80):
    current = local_map["start"]
    goal = local_map["goal"]
    path = [current]
    nodes = 0
    steps = 0

    while steps < max_steps and current != goal:
        current_h = manhattan(current, goal)
        neighbors = get_neighbors(current)
        best = current
        best_h = current_h

        for neighbor in neighbors:
            nodes += 1
            h = manhattan(neighbor, goal)

            if h < best_h:
                best = neighbor
                best_h = h

        if best == current:
            return path, nodes, current_h, False, steps, 0

        current = best
        path.append(current)
        steps += 1

    success = current == goal
    return path, nodes, manhattan(current, goal), success, steps, 0


def simulated_annealing(local_map, max_steps=140):
    random.seed(7)
    current = local_map["start"]
    goal = local_map["goal"]
    path = [current]
    nodes = 0
    steps = 0
    bad_moves = 0
    temperature = 8.0

    while steps < max_steps and current != goal and temperature > 0.1:
        current_h = manhattan(current, goal)
        neighbors = get_neighbors(current)

        if not neighbors:
            break

        choices = neighbors[:]
        if len(path) >= 2 and len(choices) > 1:
            previous = path[-2]
            choices.remove(previous)

        better_choices = []
        for item in choices:
            if manhattan(item, goal) < current_h:
                better_choices.append(item)

        if better_choices:
            neighbor = random.choice(better_choices)
        else:
            neighbor = choices[0]
        next_h = manhattan(neighbor, goal)
        nodes += 1

        delta = current_h - next_h

        if delta > 0:
            current = neighbor
            path.append(current)
        else:
            chance = math.exp(delta / temperature)
            if random.random() < chance:
                current = neighbor
                path.append(current)
                bad_moves += 1

        temperature = temperature * 0.96
        steps += 1

    success = current == goal
    return path, nodes, manhattan(current, goal), success, steps, bad_moves
