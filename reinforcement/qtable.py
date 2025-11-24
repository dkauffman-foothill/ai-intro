from typing import Callable

import numpy as np
import pandas as pd

import lander


class QTable:

    def __init__(self, max_alt: int) -> None:
        self._df = self._create_table(max_alt)

    def __repr__(self) -> str:
        return str(self._df)

    def set(self,
        state: lander.ModuleState,
        action: int,
        qvalue: float
    ) -> None:
        self._df.at[self._get_index(state), action] = qvalue

    def get_updated_qvalue(self,
        state: lander.ModuleState,
        action: int,
        reward: float,
        alpha: float,
        gamma: float
    ) -> float:
        max_qvalue = self._get_max_qvalue(state, action)
        return round(
            (1 - alpha) * self._get_qvalue(state, action)
            + alpha * (reward + gamma * max_qvalue),
        2)
    
    def greedy_select_action(self, state: lander.ModuleState) -> int:
        return max(
            state.actions, key=lambda action: self._get_qvalue(state, action)
        )

    def get_qfunction(self) -> Callable[[lander.ModuleState, int], float]:
        return lambda state, action: self._get_qvalue(state, action)

    def _create_table(self, max_alt: int):
        """
        Return a DataFrame to represent this table, with a MultiIndex of
        (Altitude, Velocity) and columns of Actions.
        """
        altitude_levels = np.arange(max_alt, -0.5, -0.5)
        velocity_levels = np.arange(5, -5.5, -0.5)
        multi_index = pd.MultiIndex.from_product(
            [altitude_levels, velocity_levels],
            names=["Altitude", "Velocity"]
        )
        df = pd.DataFrame(index=multi_index, columns=range(5), dtype=float)
        df.columns.name = "Actions"
        df = df.fillna(0.0)
        return df

    def _get_qvalue(self, state: lander.ModuleState, action: int) -> float:
        """
        Return the Q-value for the given state-action pair.
        """
        try:
            return self._df.at[self._get_index(state), action]
        except KeyError:
            return -np.inf

    def _get_max_qvalue(self, state: lander.ModuleState, action: int) -> float:
        """
        Return the maximum Q-value possible for the successor state reached by
        the given state-action pair.
        """
        successor = state.use_fuel(action)
        return max(
            self._get_qvalue(successor, next_a) for next_a in state.actions
        )

    def _get_index(self, state: lander.ModuleState) -> tuple[float, float]:
        """
        Return a state-representing key to index the table.
        """
        if 0 < state.altitude < 2:
            alt = max(0.5, round(state.altitude * 2) / 2)
        else:
            alt = round(state.altitude)
        vel = round(state.velocity * 2) / 2
        return (alt, vel)
