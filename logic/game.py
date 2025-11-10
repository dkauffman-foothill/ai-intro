class MineExplosionError(KeyboardInterrupt): pass


class HiddenBoard:

    def __init__(self, board: tuple[tuple[int, ...], ...]):
        self._rows = len(board)
        self._cols = len(board[0])
        self.explore = (lambda space:
            board[space // self._cols][space % self._cols]
            if board[space // self._cols][space % self._cols] >= 0
            else (_ for _ in ()).throw(
                MineExplosionError(f"KABOOM at [{space}]")
            )
        )

    def get_adjacent(self, space: int) -> set[int]:
        """
        Return a set of all spaces (represented as numerical indices) adjacent
        to the given space. Adjacent spaces include horizontal, vertical, and
        diagonal adjacency.
        """
        row = space // self._cols
        col = space % self._cols
        return set(
            i * self._cols + j
            for i in range(max(row - 1, 0), min(row + 2, self._rows))
            for j in range(max(col - 1, 0), min(col + 2, self._cols))
            if space != i * self._cols + j
        )
