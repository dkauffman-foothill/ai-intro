import random


class ProgramString:

    @staticmethod
    def crossover(
        ps_x: "ProgramString", 
        ps_y: "ProgramString"
    ) -> tuple["ProgramString", "ProgramString"]:
        min_len = min(len(ps_x), len(ps_y))
        if min_len < 2:
            return ps_x, ps_y
        l_i = (ps_x.sequence.find("["), ps_y.sequence.find("["))
        r_i = (ps_x.sequence.find("]"), ps_y.sequence.find("]"))
        if l_i == (-1, -1) and r_i == (-1, -1):
            point = random.randrange(1, min_len)
        else:
            all_i = list(range(1, min_len))
            choices = (all_i[:min(l_i)] +
                    all_i[max(l_i):min(r_i)] +
                    all_i[max(r_i):])
            if len(choices) == 0:
                return ps_x, ps_y
            point = random.choice(choices)
        return (
            ProgramString(ps_x.sequence[:point] + ps_y.sequence[point:]),
            ProgramString(ps_y.sequence[:point] + ps_x.sequence[point:])
        )

    @staticmethod
    def _create(max_len: int, size: int, with_halt: bool) -> "ProgramString":
        commands = "<>+-"
        if with_halt:
            commands += "!"
        if size == 0:
            if max_len > 0:
                min_len = 8  # +>[+<->] min len of program to use iter
                size = random.randrange(min_len, max_len)
            else:
                size = random.randrange(1, 50)
        sequence = "".join(random.choices(commands, k=size))
        if max_len > 0:
            sequence = ProgramString._add_jumps(sequence)
        return sequence

    @staticmethod
    def _add_jumps(sequence: str) -> str:
        i = random.randint(2, len(sequence) - 4)
        j = random.randint(i + 4, len(sequence))
        return sequence[:i] + "[" + sequence[i:j] + "]" + sequence[j:]

    def __init__(self,
        sequence: str = "",
        max_len: int = 0,
        size: int = 0,
        with_halt: bool = False
    ) -> "ProgramString":
        if sequence:
            self.sequence = sequence
        else:
            self.sequence = ProgramString._create(max_len, size, with_halt)
        self.score = -1

    def mutate(self, probas: dict[str, float] = {}) -> None:
        if len(set(probas.keys()) - set(("insert", "change", "delete"))) > 0:
            raise KeyError("Mutation can only be insert, change, or delete.")
        mutated = ""
        r_val = random.random()
        if self.sequence == "" and r_val > 0.2:
            return random.choice("<>+-")
        for i in range(len(self.sequence)):
            if self.sequence[i] in "[]":
                mutated += self.sequence[i]
            else:
                if r_val > probas.get("delete", 0.5):
                    pass
                elif r_val > probas.get("insert", 0.5):
                    mutated += self.sequence[i] + random.choice("<>+-")
                elif r_val > probas.get("change", 0.5):
                    options = "<>+-".replace(self.sequence[i], "")
                    mutated += random.choice(options)
                else:
                    mutated += self.sequence[i]
        self.sequence = mutated
        self.score = -1

    def __eq__(self, other: "ProgramString") -> bool:
        return self.sequence == other.sequence

    def __len__(self) -> int:
        return len(self.sequence)

    def __hash__(self) -> int:
        return hash(self.sequence)

    def __repr__(self) -> str:
        return self.sequence