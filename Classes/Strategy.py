class Strategy:
    # The class of the spare strategy and the insurance strategy
    def __init__(self, strategy: str, sat, time: int):
        self.str = strategy   # Strategy type
        self.time = time   # Time for spare in seconds
        if strategy == 'none':   # No spare strategy, no insurance
            self.limit = 0   # Limit of satellites
            self.replacement_cost = 0   # Money for action
            self.start_cost = 0   # Money in the beginning
            self.day = 0   # Money daily
        elif strategy == 'extra':   # Extra satellite in-orbit, no insurance
            self.limit = 3
            self.replacement_cost = 0
            self.start_cost = 3 * (sat.cost + sat.launch_cost)
            self.day = sat.operational_cost
        elif strategy == 'lod':   # Launch-on-demand, no insurance
            self.limit = 999999999
            self.replacement_cost = sat.cost + sat.launch_cost
            self.start_cost = 0
            self.day = 0
