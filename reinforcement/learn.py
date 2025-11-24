from typing import Callable

import lander


class HighImpactVelocityError(BaseException): pass


def simulate(
    learn_q: Callable[[lander.ModuleState, int], float],
    n_iter: int,
    target: str,
    n_actions: int,
    debug: bool = False
) -> None:
    state = lander.ModuleState(
        target,
        fuel=100,
        altitude=100.0,
        n_actions=n_actions
    )
    q = learn_q(state, n_iter=n_iter)
    policy = lambda s: max(s.actions, key=lambda a: q(s, a))
    while state.altitude > 0:
        if debug:
            print(state)
        state = state.use_fuel(policy(state))
    print(state)
    if state.velocity < -1.0:
        raise HighImpactVelocityError(f"Impact Velocity: {state.velocity:.2f}")