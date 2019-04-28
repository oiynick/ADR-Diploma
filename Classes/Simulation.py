import numpy as np
import datetime as dt
import time
import os
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

        # Fill the atributes of the simulation with numbers
        self.n = n
        self.simtime = int(simtime)
        self.step = int(step)
        self.acc = acc
        self.steps = int(simtime / step)

        # Upload files longitude, latitude of the undersat point on the Earth
        # money is for money grid, lifetime is for array of lifetimes
        self.lon = np.loadtxt('./PP_Data/lon.txt').T
        self.lat = np.loadtxt('./PP_Data/lat.txt').T
        self.money = np.loadtxt('./PP_Data/data.txt')
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
        # Check if the simulation time step hits the EOL point of the sat
        cost = 0
        if states[index] > 0:
            if states[index] != 1:
                states[index] -= 1
            else:
                states[index] = - self.strat.time
                cost = self.strat.replacement_cost
        else:
            if states[index] != 0:
                states[index] += 1
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
                    states[i] = 9999999
                else:
                    states[i] = -state + start
        return states

    def part_sim(self, start, stop):
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
            # Current percentage and time
            cur_p = 100/self.steps*ts
            now_is = time.clock() - st
            # Show only new percentages and with .01 precision
            if stop == self.steps and (cur_p - complete) >= .01:
                print('{:.2f}% done, in {:.2f} seconds'.format(cur_p, now_is))
                complete = cur_p

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
