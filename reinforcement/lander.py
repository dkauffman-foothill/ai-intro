class ModuleState:

    def __init__(self,
        target: str,
        fuel: int,
        altitude: float,
        n_actions: int = 5,
        velocity: float = 0.0
    ):
        """
        An instance of ModuleState has the following attributes:
            fuel: int
                The amount of fuel (in liters) able to be used.
            altitude: float
                The distance (in meters) of the module from the surface of its
                target object.
            velocity: float
                The speed of the module, where a positive value indicates
                movement away from the target object and a negative value
                indicates movement toward it. Defaults to zero.
            n_actions: int
                The number of available fuel rates, where 0 indicates free-fall
                and the highest-valued action indicates maximum thrust away
                from the target object. Defaults to (0, 1, 2, 3, 4).
        """
        self.fuel = fuel
        self.altitude = altitude
        self.velocity = velocity
        self.target = target
        self.gforce = ModuleState.get_gforce(self.target)
        self.n_actions = n_actions
        self.actions = tuple(range(n_actions))
    
    def __repr__(self) -> str:
        if not self.altitude:
            return (
                "-" * 16 + "\n"
                + f" Remaining Fuel: {self.fuel:4} l\n"
                + f"Impact Velocity: {self.velocity:7.2f} m/s\n"
            )
        else:
            return (
                f"    Fuel: {self.fuel:4} l\n"
                + f"Altitude: {self.altitude:7.2f} m\n"
                + f"Velocity: {self.velocity:7.2f} m/s\n"
            )

    @staticmethod
    def get_gforce(target: str) -> float:
        return {
            "MOON": 0.1657,
            "MARS": 0.378,
            "VENUS": 0.905,
            "EARTH": 1.0,
        }[target]

    def use_fuel(self, rate: int) -> "ModuleState":
        """
        Return a ModuleState instance in which the fuel, altitude, and velocity
        are updated based on the fuel rate chosen.
        """
        if self.altitude == 0.0:
            return self
        rate = self._get_adjusted_rate(rate)
        fuel = max(0, self.fuel - rate)
        if not fuel:
            rate = 0
        acceleration = self._get_acceleration(rate)
        return ModuleState(
            self.target,
            fuel,
            altitude=self._get_altitude(acceleration),
            velocity=self._get_velocity(acceleration),
            n_actions=self.n_actions
        )

    def _get_adjusted_rate(self, rate: int) -> int:
        """
        Adjust to a fuel rate of zero if the lander is too high or moving too
        fast away from the target. Adjust to a maximum fuel rate if the lander
        is moving too fast toward the target.
        """
        if self.altitude > 100 or self.velocity > 5:
            return 0
        if self.velocity < -5:
            return self.actions[-1]
        return rate
    
    def _get_acceleration(self, rate: int) -> float:
        return self.gforce * 9.8 * 2 * rate / (self.n_actions - 1) - 1

    def _get_altitude(self, acceleration: float) -> float:
        return max(0.0, self.altitude + self.velocity + acceleration / 2)

    def _get_velocity(self, acceleration: float) -> float:
        return self.velocity + acceleration
