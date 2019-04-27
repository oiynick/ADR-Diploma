import numpy as np
import datetime as dt
import time
from Classes.Strategy import Strategy
from Classes.Maths import Trend
from Classes.Satellite import Satellite


class Simulation:
    # The class bringing the simulation object

    def __init__(self, mass, volume, lams, ks, alfa, alt, cov,   # Sat
                 n, price,   # Constellation and service
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
        '''

        # Create a satellite class object with appropriate parameters
        self.sat = Satellite(mass, volume, lams, ks, alfa, alt, cov)

        # Fill the atributes with numbers
        self.n = n
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
        self.state = np.loadtxt('./PP_Data/lifetime.txt')
        # Spare strategy
        self.strat = Strategy(0, 0, 0, strat)
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

    def switcher(self, states, index, ts):
        # Based on the probability switch the satellite on or off
        # Each ts according to Weibull func
        # Returns costs on switching
        cost = 0

        if states[index] > 0:
            if states[index] != 1:
                states[index] = states[index] - 1
            else:
                states[index] = - self.strat.time
                cost = self.strat.replacement_cost
        else:
            if states[index] != 0:
                states[index] = states[index] + 1
                cost = self.strat.day_cost/86400*self.step
            else:
                states[index] = 2207521

        return cost

    def states_arr(self, start):
        # Create a states matrix
        states = self.state
        for i, state in enumerate(states):
            if state - start > 0:
                states[i] = state - start
            else:
                if state - start + self.strat.time < 0:
                    states[i] = state - start - self.strat.time
                else:
                    states[i] = -state + start - self.strat.time
        return states

    def part_sim(self, start, stop, write=False):
        # CACLULATING THE PART OF SIMULATION
        # including 'start' not including 'stop'

        # Starting time
        st = time.clock()
        # TODO: take market real numbers for trend
        m = Trend('lin', 0.0005, 0.15, 155520, 1)   # Trend object
        states = self.states_arr(start)   # Create states matrix for the part
        complete = 0   # Percentage of progress
        metrics = np.zeros((int(stop-start), 7))   # Output array

        for ts in range(start, stop):
            # Show the status in % and time passed if required
            if write:
                # Show only new percentages and with .01 precision
                if 100/(stop-start)*ts - complete > 0.005:
                    print('{:.2f}'.format(100/(stop-start)*ts))
                complete = 100/(stop-start)*ts
                # For some steps show the time passed
                if ts % 100 == 0:
                    print('time passed: {} seconds'.format(time.clock() - st))

            # Reset the parameters
            coverage = 0   # Coverage
            rev = 0   # Overall revenue
            irev = 0   # Overall ideal revenue
            costs = 0   # Technical costs
            icosts = 0   # Ideal technical costs
            dens = 0   # Additional density on the altitude
            for i in range(self.n):
                # Tease for switching off or on
                costs = costs + self.switcher(states, i, ts)

                # Assembling and launch
                if ts == 0:
                    costs += self.sat.launch_cost + self.sat.cost

                # Get coverage points revenue
                points = self.sat.coverage(self.lon[ts, i],
                                           self.lat[ts, i], self.acc)
                revenue = 0
                for p in points:
                    revenue = self.money[int(p[0]/self.acc),
                                         int(p[1]/self.acc)]*self.price

                # Coverage and costs
                if states[i] >= 0:
                    coverage += self.sat.cov
                    costs += self.sat.operational_cost/2592000*self.step
                    rev += revenue*m[ts]
                else:
                    dens += self.sat.vol

                irev += revenue*m[ts]
                icosts += self.sat.operational_cost/2592000*self.step

            metrics[ts, 0] = ts*self.step
            metrics[ts, 1] = coverage
            metrics[ts, 2] = rev
            metrics[ts, 3] = irev
            metrics[ts, 4] = costs
            metrics[ts, 5] = icosts
            metrics[ts, 6] = dens
        return metrics

    def export(self, *args):
        # file is the name of data file, that has to be exported
        cur = dt.datetime.now()
        now = cur.strftime("%d-%m %H:%M")
        if len(args) == 0:
            np.savetxt("./Output/{}.csv".format(now),
                       self.metrics, delimiter=',',
                       fmt='%1.3f',
                       header="t(s), cv(%), R($), iR($), C($), iC($), d")
        elif len(args) > 1:
            raise IndexError('Too much arguments have been passed. 1 expected')
        else:
            np.savetxt("./Output/{}.csv".format(now),
                       args[0], delimiter=',',
                       fmt='%1.3f',
                       header="t(s), cv(%), R($), iR($), C($), iC($), d")
