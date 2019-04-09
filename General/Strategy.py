class Strategy:
    # The class of the spare strategy and the insurance strategy
    def __init__(self, time, satellite, service, strategy='none'):
        if strategy == 'none':   # No spare strategy, no insurance
            self.limit = 0   # Limit of satellites
            self.time = 0   # Time for spare
            self.replacement_cost = 0   # Money for action
            self.start_cost = 0   # Money in the beginning
            self.day = 0   # Money daily
        elif strategy == 'extra':   # Extra satellite in-orbit, no insurance
            self.limit = 3
            self.time = time
            self.replacement_cost = 0
            self.start_cost = 3 * (satellite.cost + satellite.launch_cost)
            self.day = satellite.operational_cost
        elif strategy == 'lod':   # Launch-on-demand, no insurance
            self.limit = 999999999
            self.time = time
            self.replacement_cost = satellite.cost + satellite.launch_cost + service
            self.start_cost = 0
            self.day = 0
