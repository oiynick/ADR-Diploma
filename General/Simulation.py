import numpy as np
import Orbital
from General.Strategy import Strategy
from General.Company import Company
from General.Market import Market
from General.Maths import Maths
from General.Maths import Trend


class Simulation:
    # The class bringing all the simulation object
    state = []
    coverage = []   # Coverage revolution
    revenue = []   # Money obtained on the service selling
    irevenue = []   # Ideal revenue (no sats lost)
    cost = []   # Special constellation-related costs
    time = []   # Time array

    def __init__(self, price, spps, incs, ppi, alts, eccs,
                 hr, volume, lams, ks, mass, strat: str, name: str,
                 sat_alfa=50, lifetime=5, simtime, step):
        self.constellation = []   # Create the array of satellites

        # Fill the array with the Satellite objects
        for i in range(len(alts)):
            dOm = 180/ppi[i]   # ANGULAR DIFFERENCE BETWEEN ORBITS IN RAAN
            du = 360/spps[i]   # ANGULAR DIFFERENCE BETWEEN SATELLITES IN ORBIT
            for j in range(ppi[i]):
                for k in range(spps[i]):
                    # Create an instance of the satellite class
                    self.constellation.append(Orbital.Satellite(du*k,
                                                                alts[i],
                                                                sat_alfa,
                                                                lifetime,
                                                                eccs[i],
                                                                dOm*j,
                                                                incs[i],
                                                                mass,
                                                                volume,
                                                                lams, ks,
                                                                name))
        
        
        for i in itera:
            
        # Spare strategy
        self.strat = Strategy(strat, 0, 0, 0)
        # Price of the flat-service
        self.price = price
        # Create an instance of the company
        self.spacex = Company(hr, 2, 0.6)
        # Output array
        self.metrics = np.zeros((simtime/step, 6))

    def switcher(self, costs, sat, ts, scale):
        # Based on the probability switch the satellite on or off
        # Each day
        if sat.state:
            if ts % 86400/scale != 0:
                self.state.append(True)
            elif Maths.check_probe(sat.get_reliability(ts), 1000):
                if Maths.check_probe(sat.density):
                    change = (4/3*np.pi*(sat.alt+10)**3 -
                              4/3*np.pi*(sat.alt-10)**3)*sat.density
                    change = change + sat.vol
                    sat.density = sat.density + change
                self.state.append(False)
                sat.state = False
                sat.turn_t = self.strat.time
                costs = costs + self.strat.replacement_cost
            else:
                self.state.append(True)

        else:
            if sat.turn_t == 1:
                sat.turn_t = 0
                sat.state = True
                self.state.append(True)
            elif sat.turn_t == 0:
                self.state.append(False)
            else:
                self.state.append(False)
                sat.turn_t = sat.turn_t - 1
                costs = costs + self.strat.day_cost

    def simulate(self, mstart, step, simtime):
        # CACLULATING THE SIMULATION
        # Creating classes instances
        endt = Maths.jtime(self.spacex.maxmarkt,
                           0, 0, 0, 0, 0)/step
        m = Trend('lin', 0.3, self.spacex.maxmark, 1, endt)

        step = Maths.jtime(0, 0, 0, step, 0, 0)
        lifet = Maths.jtime(0, simtime, 0, 0, 0, 0)

        itera = np.nditer(metrics, flags="multi_index", op_flags="readwrite")

        for i in itera:
            rev = 0   # Overall revenue
            irev = 0   # Overall ideal revenue
            costs = 0   # Technical costs
            coverage = 0   # Coverage
            for sat in self.constellation:
                # Tease for switching
                self.switcher(costs, sat, ts, step)

                # Assembling and launch
                if ts == 0:
                    costs = sat.launch_cost + sat.cost

                # Calculate the change in coordinates
                sat.Om = sat.Om + 7.3*ts*step
                sat.u = sat.u + sat.mu**.5/sat.alt**1.5*ts*step

                # Get coverage points revenue
                points = sat.coverage(sat.Om, sat.u)
                for p in points:
                    revenue = Market.get_data(self.price,
                                              p[0], p[1])
                    rev = rev + revenue*int(sat.state)*m[ts]
                    irev = irev + revenue*m[ts]

                # Coverage and costs
                if sat.state:
                    coverage = coverage + sat.covarage_rate
                    costs = costs + sat.operational_cost*ts/720

            costs = self.spacex[ts*step]
            self.revenue.extend([rev])
            self.irevenue.extend([irev])
            self.costs.extend([costs])
            self.coverage.extend([coverage])
            self.time.extend([ts])
            print(ts*step/lifet*100)

    def export(self):
        np.savetxt("output.csv", self.metrics, delimiter=',',
                   header="state, coverage, revenue, irevenue, cost, time")