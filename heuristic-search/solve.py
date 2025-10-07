import queue

import puzzle


def solve_puzzle(tiles: tuple[int, ...]) -> str:
    state = puzzle.State(tiles, "")
    frontier = queue.PriorityQueue()
    explored = set()
    while state.h > 0:
        explored.add(state.tiles)
        for new_state in state.create_new_states():
            if new_state.tiles not in explored:
                frontier.put(new_state)
        state = frontier.get()
    return state.path
