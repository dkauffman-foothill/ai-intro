import math
import random
from typing import Callable, Optional


def play(
    mcts: Callable[["BoardState", int], int],
    sims: int,
    debug: bool = False
) -> None:
    """
    Play a game of 3D Tic-Tac-Toe with the computer.

    If you lose, you lost to a machine.
    If you win, your implementation was bad.
    You lose either way.
    """
    state = BoardState.initial_state()
    while state.util is None:
        # human move
        print(state)
        state = state.get_successor(int(input("Move: ")))
        if state.util is not None:
            break
        # computer move
        move = mcts(state, sims)
        if debug:
            state.display_win_ratios()
        state = state.get_successor(move)
    print(state)
    if state.util == 1:
        print("MAX wins!")
    elif state.util == -1:
        print("MIN wins!")
    else:
        print("Tie game")




class BoardState:

    def __init__(self,
        player: int,
        occupied: dict[int, frozenset[int]],
        move: Optional[int],
        moves: frozenset[int]
    ):
        self._player = player
        self._occupied = occupied
        self.move = move
        self.moves = moves
        self.wins = 0
        self.sims = 0
        self.util = self._get_utility()  
        self.children = set() if self.util is None else None

    @staticmethod
    def initial_state() -> "BoardState":
        """
        Return an empty board to begin a game.
        MAX is always the first player.
        """
        player = 1
        occupied = {
            1: frozenset(),  # MAX
            -1: frozenset()  # MIN
        }
        move = None
        moves = frozenset(range(64))
        return BoardState(player, occupied, move, moves)

    def get_successor(self, move: int) -> "BoardState":
        """
        Return the BoardState resulting from applying the given move on the
        current BoardState.
        """
        for child in self.children:
            if child.move == move:
                return child
        occupied = {key: val for key, val in self._occupied.items()}
        occupied[self._player] |= frozenset([move])
        moves = self.moves - frozenset([move])
        return BoardState(-self._player, occupied, move, moves)

    def __eq__(self, other) -> bool:
        return hash(self) == hash(other)
    
    def __lt__(self, other) -> bool:
        return self.move < other.move

    def __hash__(self) -> int:
        return hash(tuple([self._occupied[1], self._occupied[-1]]))
    
    def __str__(self) -> str:
        s = ""
        for n_iter, row in enumerate(BoardState._get_rows()):
            if n_iter % 4 == 0:
                s += "\n"
            row = sorted(row)
            for space in row:
                if space in self._occupied[1]:
                    space = "X"
                elif space in self._occupied[-1]:
                    space = "O"
                s += f"{space:>4}"
            s += " " * 4
        return s + "\n"

    def display_win_ratios(self):
        """
        Print the number of wins and simulations (attempts) through each node
        that is a direct child of this node.
        """
        for child in sorted(self.children):
            ratio = child.wins / child.sims * 100
            print(
                f"[{child.move:>2}]:",
                f"{child.wins:>4}/{child.sims:>4}",
                f"{ratio:>5.1f}%"
            )
        print()
    
    def select(self, c: float) -> Optional["BoardState"]:
        """
        Return a child node if one is chosen by applying the Upper Confidence
        Bound (UCB) selection policy, which balances exploration with
        exploitation. The given `c` parameter is the exploration bias, with a
        higher value causing more exploration.

        Return None if no child is chosen - either because no child's UCB was
        high enough or this node has no expanded children.
        """
        if self.children:
            children = sorted(
                self.children,
                key=lambda child: self._get_ucb(child, c),
                reverse=True
            )
            best_child = children[0]
            threshold = c * math.sqrt(math.log(self.sims + 1))
            all_expanded = len(self.children) == len(self.moves)
            if all_expanded or self._get_ucb(best_child, c) >= threshold:
                return best_child

    def expand(self) -> Optional["BoardState"]:
        """
        If this node is not a terminal game state, add a random child node to
        this node's set of tracked child nodes and return it; otherwise return
        None.
        """
        #if self.children is not None:
        if self.util is None:
            child = self._get_random_successor()
            self.children.add(child)
            return child

    def simulate(self) -> Optional["BoardState"]:
        """
        If this node is not a terminal game state, return a random child node;
        otherwise return None.
        """
        if self.util is None:
            return self._get_random_successor()

    def update_outcome(self, winner: int) -> None:
        """
        Increment the number of simulations for this node. If the player who
        could have selected this node won the simulation, increment the number
        of wins as well.
        """
        if winner == -self._player:
            self.wins += 1
        self.sims += 1
    
    def _get_random_successor(self) -> "BoardState":
        move = random.choice(list(self.moves))
        return self.get_successor(move)

    def _get_ucb(self, child: "BoardState", c: float) -> float:
        exploit = child.wins / child.sims
        explore = c
        if self.sims > 0 and child.sims > 0:
            explore *= math.sqrt((math.log(self.sims)) / (child.sims))
        return exploit + explore

    def _get_utility(self) -> Optional[int]:
        for line in BoardState._get_winning_conditions():
            for player in (1, -1):
                has_won = len(line - self._occupied[player]) == 0
                if has_won:
                    return player
        if len(self._occupied[1] | self._occupied[-1]) == 64:
            return 0

    @staticmethod
    def _get_rows():
        for i in range(0, 16, 4):
            for j in range(i, 64, 16):
                yield set(range(j, j + 4))

    @staticmethod
    def _get_winning_conditions():
        size = 4
        to_scalar = lambda x, y, z: z * 16 + y * 4 + x

        # x axis (16 conditions)
        for row in BoardState._get_rows():
            yield row

        # y axis (16 conditions)
        for z in range(size):
            for x in range(size):
                yield set(to_scalar(x, y, z) for y in range(size))

        # z axis (16 conditions)
        for y in range(size):
            for x in range(size):
                yield set(to_scalar(x, y, z) for z in range(size))

        # x-y axes (8 conditions)
        for z in range(size):
            yield set(to_scalar(i, i, z) for i in range(size))
            yield set(to_scalar(size - 1 - i, i, z) for i in range(size))

        # x-z axes (8 conditions)
        for y in range(size):
            yield set(to_scalar(i, y, i) for i in range(size))
            yield set(to_scalar(size - 1 - i, y, i) for i in range(size))

        # y-z axes (8 conditions)
        for x in range(size):
            yield set(to_scalar(x, i, i) for i in range(size))
            yield set(to_scalar(x, size - 1 - i, i) for i in range(size))

        # x-y-z axes (4 conditions)
        yield set(to_scalar(i, i, i) for i in range(size))
        yield set(to_scalar(size - 1 - i, i, i) for i in range(size))
        yield set(to_scalar(i, size - 1 - i, i) for i in range(size))
        yield set(to_scalar(size - 1 - i, size - 1 - i, i) for i in range(size))
