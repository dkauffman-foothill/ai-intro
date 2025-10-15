def interpret(program: str, size: int, max_steps = 1000) -> tuple[int, ...]:
    """
    Using a zeroed-out memory array of the given size, run the given
    program to update the integers in the array. If the program is
    ill-formatted or requires too many iterations to interpret, raise a
    RuntimeError.
    """
    p_ptr = 0
    a_ptr = 0
    count = 0
    i_map = _preprocess(program)
    memory = [0] * size
    while p_ptr < len(program):
        if program[p_ptr] == "[":
            if memory[a_ptr] == 0:
                p_ptr = i_map[p_ptr]
        elif program[p_ptr] == "]":
            if memory[a_ptr] != 0:
                p_ptr = i_map[p_ptr]
        elif program[p_ptr] == "<":
            if a_ptr > 0:
                a_ptr -= 1
        elif program[p_ptr] == ">":
            if a_ptr < len(memory) - 1:
                a_ptr += 1
        elif program[p_ptr] == "+":
            memory[a_ptr] += 1
        elif program[p_ptr] == "-":
            memory[a_ptr] -= 1
        else:
            raise RuntimeError
        p_ptr += 1
        count += 1
        if count > max_steps:
            raise RuntimeError
    return tuple(memory)


def _preprocess(program: str) -> dict[int, int]:
    """
    Return a dictionary mapping the index of each [ command with its
    corresponding ] command. If the program is ill-formatted, raise a
    RuntimeError.
    """
    i_map = {}
    stack = []
    for p_ptr in range(len(program)):
        if program[p_ptr] == "[":
            stack.append(p_ptr)
        elif program[p_ptr] == "]":
            if len(stack) == 0:
                raise RuntimeError
            i = stack.pop()
            i_map[i] = p_ptr
            i_map[p_ptr] = i
    if len(stack) != 0:
        raise RuntimeError
    return i_map