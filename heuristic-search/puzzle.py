import random

import heuristic


def is_optimal_solution(tiles: tuple[int], path: str, opt_len: int) -> bool:
    return is_solution(tiles, path) and len(path) <= opt_len


def is_solution(tiles: tuple[int], path: str) -> bool:
    if not isinstance(path, str):
        return False
    state = State(tiles, "")
    for move in path:
        try:
            state = state._move_tile(move)
        except IndexError:
            return False
    return state.tiles == tuple(sorted(tiles))


class State:

    _MOVES = "←↓↑→"

    @staticmethod
    def randomize(size: int) -> "State":
        state = None
        while not (state and state.is_solvable()):
            tiles = tuple(random.sample(range(size ** 2), size ** 2))
            state = State(tiles, "")
        return state

    def __init__(self, tiles: tuple[int, ...], path: str) -> None:
        self.tiles = tuple(tiles)
        self.path = path
        self._size = int(len(tiles) ** 0.5)
        self.lc = heuristic.Heuristic.get_linear_conflicts(tiles, self._size)
        self._md = heuristic.Heuristic.get_manhattan_distance(tiles, self._size)
        self.h = self._md + self.lc
        self._cost = len(self.path) + self.h

    def __lt__(self, other) -> bool:
        return self._cost < other._cost

    def __hash__(self) -> int:
        return hash((self.tiles, len(self.path)))

    def create_new_states(self) -> list["State"]:
        states = []
        for move in State._MOVES:
            if (
                self._is_valid_move(move)
                and not self._is_opposing_move(move)
            ):
                states.append(self._move_tile(move))
        return states

    def is_solvable(self) -> bool:
        """
        Return True if the given tiles represent a solvable puzzle and False
        otherwise.

        >>> is_solvable((3, 2, 1, 0))
        True
        >>> is_solvable((0, 2, 1, 3))
        False
        """
        _, inversions = self._count_inversions(list(self.tiles))
        width = int(len(self.tiles) ** 0.5)
        if width % 2 == 0:
            row = self.tiles.index(0) // width
            return (
                row % 2 == 0 and inversions % 2 == 0 or
                row % 2 == 1 and inversions % 2 == 1
            )
        else:
            return inversions % 2 == 0

    def _is_valid_move(self, move: str) -> bool:
        i = self.tiles.index(0)
        if move == State._MOVES[0]:
            return (i + 1) % self._size != 0
        elif move == State._MOVES[1]:
            return i // self._size != 0
        elif move == State._MOVES[2]:
            return (i // self._size) + 1 < self._size
        elif move == State._MOVES[3]:
            return i % self._size != 0
        else:
            return False

    def _is_opposing_move(self, move: str) -> bool:
            if len(self.path) == 0:
                return False
            opposing_move = State._MOVES[::-1].find(move)
            return State._MOVES.find(self.path[-1]) == opposing_move

    def _move_tile(self, move: str) -> "State":
        """
        Given tiles and a move to apply, return the updated tiles.
        """
        tiles = list(self.tiles)
        i = tiles.index(0)
        if move.upper() == State._MOVES[0]:
            tiles[i], tiles[i + 1] = tiles[i + 1], tiles[i]
        elif move.upper() == State._MOVES[1]:
            tiles[i], tiles[i - self._size] = tiles[i - self._size], tiles[i]
        elif move.upper() == State._MOVES[2]:
            tiles[i], tiles[i + self._size] = tiles[i + self._size], tiles[i]
        elif move.upper() == State._MOVES[3]:
            tiles[i], tiles[i - 1] = tiles[i - 1], tiles[i]
        return State(tuple(tiles), self.path + move)

    def _count_inversions(self, ints: list[int]) -> tuple[list[int], int]:
        """
        Count the number of inversions in the given sequence of integers (ignoring zero), and return the sorted sequence along with the inversion count.

        This function is only intended to assist `is_solvable`.

        >>> _count_inversions([3, 7, 1, 4, 0, 2, 6, 8, 5])
        ([1, 2, 3, 4, 5, 6, 7, 8], 10)
        """
        if len(ints) <= 1:
            return ([], 0) if 0 in ints else (ints, 0)
        midpoint = len(ints) // 2
        l_side, l_inv = self._count_inversions(ints[:midpoint])
        r_side, r_inv = self._count_inversions(ints[midpoint:])
        inversions = l_inv + r_inv
        i = j = 0
        sorted_tiles = []
        while i < len(l_side) and j < len(r_side):
            if l_side[i] <= r_side[j]:
                sorted_tiles.append(l_side[i])
                i += 1
            else:
                sorted_tiles.append(r_side[j])
                inversions += len(l_side[i:])
                j += 1
        sorted_tiles += l_side[i:] + r_side[j:]
        return (sorted_tiles, inversions)