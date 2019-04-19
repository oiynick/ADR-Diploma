import numpy as np
from Classes.Strategy import Strategy
from Classes.Maths import Maths
from Classes.Maths import Trend
from Classes.Satellite import Satellite


class Simulation:
    # The class bringing the simulation object
    coverage = []   # Coverage revolution
    revenue = []   # Money obtained on the service selling
    irevenue = []   # Ideal revenue (no sats lost)
    cost = []   # Special constellation-related costs
    time = []   # Time array

    def __init__(self, mass, volume, lams, ks, alfa, alt, cov,   # Sat
                 n, planes, price,   # Constellation and service
                 strat: str,   # Classes
                 simtime, step, acc):   # Simulation
        '''
        price -- service price estimation
        TODO: to be changed for model
        alt -- satellites altitude
        volume -- satellite volume
        lams -- lambdas for Weibull
        ks -- kef for Weibull
        mass -- satellite mass
        strat -- strategy name (none/ extra/ lod)
        alfa -- FOV of the satellite antenna
        simtime -- simulation time period in seconds
        step -- timestep size of the simulation in seconds
        acc -- step of the grid
        n -- number of satellites in the constellation
        planes -- number of planes in the constellation
        '''

        # Create a satellite class object with appropriate parameters
        self.sat = Satellite(mass, volume, lams, ks, alfa, alt, cov)

        # Fill the atributes with numbers
        self.n = n
        self.planes = planes
        self.simtime = simtime
        self.step = step
        self.acc = acc

        # Upload files
        self.lon = np.loadtxt('./PP_Data/lon.txt').T
        self.lat = np.loadtxt('./PP_Data/lat.txt').T
        self.money = np.loadtxt('./PP_Data/data.txt')

        # Create an empty state-array
        # The array takes a negative value that equaled to the replacement
        # time by the absolute, -9999 if the replacement is not taken into
        # account if the satellite state is "in operation" the number shows
        # the uptime of the satellite
        self.state = np.zeros(n)
        # Spare strategy
        self.strat = Strategy(strat, 0, 0, 0)
        # Price of the flat-service per step
        self.price = price/2592000*step
        # Output array
        # First column -- time in seconds
        # 2 -- coverage percentage
        # 3 -- revenue
        # 4 -- ideal revenue
        # 5 -- costs
        # 6 -- ideal costs
        # 7 -- debris density in the orbit
        self.metrics = np.zeros((int(simtime/step), 7))

    def switcher(self, state, ts):
        # Based on the probability switch the satellite on or off
        # Each ts according to Weibull func
        # Returns costs on switching
        cost = 0

        if state >= 0:
            if Maths.check_probe(self.sat.get_reliability(ts), 100):
                state = - self.strat.time
                cost = self.strat.replacement_cost
            else:
                state = state + 1
        else:
            state = state + 1
            cost = self.strat.day_cost/86400*self.step

        return cost

    def simulate(self):
        # CACLULATING THE SIMULATION

        i = 0
        m = Trend('poly05', 0.05, 0.3, 155520, 1)   # Trend object

        rev = 0   # Overall revenue
        irev = 0   # Overall ideal revenue
        costs = 0   # Technical costs
        icosts = 0   # Ideal technical costs
        dens = 0   # Additional density on the altitude

        for ts in range(int(self.simtime/self.step)):
            # Status in %
            print('{:.2f}'.format(ts*self.step/self.simtime*100))

            coverage = 0   # Coverage
            for i in range(self.n):
                # Tease for switching
                cost = self.switcher(self.state[i], ts)

                # Assembling and launch
                if ts == 0:
                    costs = self.sat.launch_cost + self.sat.cost

                # Get coverage points revenue
                points = self.sat.coverage(self.lon[ts, i],
                                           self.lat[ts, i], self.acc)
                revenue = 0
                for p in points:
                    revenue = self.money[int(p[0]/self.acc),
                                         int(p[1]/self.acc)]*self.price

                # Coverage and costs
                if self.state[i] >= 0:
                    coverage = coverage + self.sat.cov
                    costs = cost + self.sat.operational_cost/2592000*self.step
                    rev = rev + revenue*m[ts]
                else:
                    dens = dens + self.sat.vol

                irev = irev + revenue*m[ts]
                icosts = icosts + self.sat.operational_cost/2592000*self.step
                i += 1

            self.metrics[ts, 0] = ts*self.step
            self.metrics[ts, 1] = coverage
            self.metrics[ts, 2] = rev
            self.metrics[ts, 3] = irev
            self.metrics[ts, 4] = costs
            self.metrics[ts, 5] = icosts
            self.metrics[ts, 6] = dens

    def export(self):
        np.savetxt("output.csv", self.metrics, delimiter=',', fmt=':.3f',
                   header="t(s), cv(%), R(US$), iR(US$), C(US$), iC(US$), d")
