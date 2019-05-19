import numpy as np
import os
import _pickle as pickle
from time import time as t
from numpy.random import choice as rnd
# from time import time as tt
import datetime as dt
# from geopy import distance

# Custom classes import
from Classes.Helpers import Strategy
from Classes.Helpers import Trend
from Classes.Satellite import Satellite
R = 6378.137


class Simulation:
    # The class bringing the simulation object

    def __init__(self, mass, volume, alfa, alt, cov,   # Sat
                 n: int,   # Constellation and service
                 strat: str,   # Classes
                 simtime: int, step: int, acc: float):   # Simulation
        '''
        price -- service price estimation
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
        self.sat = Satellite(mass, volume, alfa, alt, cov)

        # Fill the atributes of the simulation with numbers
        self.n = n
        self.simtime = simtime
        self.step = step
        self.acc = acc
        self.steps = int(np.floor(simtime / step))

        # Spare strategy
        self.strat = Strategy(strat, self.sat, 0)

        # Upload files longitude, latitude of the undersat point on the Earth
        # money is for money grid, lifetime is for array of lifetimes
# =============================================================================
#         with open('./PP_Data/lon12.data', 'rb') as f:
#             self.lon = pickle.load(f)
#         with open('./PP_Data/lat12.data', 'rb') as f:
#             self.lat = pickle.load(f)
# =============================================================================
        with open('./PP_Data/market.data', 'rb') as f:
            self.money = pickle.load(f)
        st = t()
        self.states = self.status()
        print('States array took {}s'.format(t() - st))

    def status(self):
        # Upload the matrix of the probabilities
        arr = np.empty((self.steps, self.n), dtype='object')
        p = [.15]
        for i in range(1, 2207520):
            p.append(.000120114*np.exp(-.000265681*i**.4521)/i**.5479)
        p.append(1 - sum(p))
        lt = rnd(range(len(p)), size=self.n, p=p)
        for ts in range(self.steps):
            for i in range(self.n):
                if ts < lt[i]:
                    arr[ts, i] = 'o'
                elif ts == lt[i]:
                    if self.strat.str == 'none':
                        arr[ts, i] = 'f'
                    else:
                        arr[ts, i] = 'i'
                        new_lt = rnd(range(2207521), size=1, p=p)
                        lt[i] += new_lt + self.strat.time
                elif ts < lt[i] + self.strat.time:
                    if self.strat.str == 'none':
                        arr[ts, i] = 'n'
                    else:
                        arr[ts, i] = 'r'
                elif ts >= lt[i] + self.strat.time:
                    if self.strat.str == 'none':
                        arr[ts, i] = 'n'
                    else:
                        arr[ts, i] = 'o'
        return arr

    def coverage(self, sat, lon, lat, acc):
        # Return the array of dots for the coverage area
        # lat-lon is satellite antenna focus point on Earth

        r = (sat.alt)*np.tan(np.pi * (sat.alfa/2)/180)   # Coverage radius
        mdist = np.ceil(r/111)   # Maximum possible deviation in degrees
        res = []
        # Iterate through coords around the focus point
        for i in np.arange(np.floor(lon-mdist), np.ceil(lon+mdist), acc):
            for j in np.arange(np.floor(lat-mdist), np.ceil(lat+mdist), acc):
                # Calculate the distance and decide whether the point is in
                # the circle or not

                # dist = distance.great_circle((lat, lon), (j, i)).km

                rlat = np.deg2rad(lat)
                rlon = np.deg2rad(lon)
                ri = np.deg2rad(i)
                rj = np.deg2rad(j)
                dist = R*np.arccos(np.sin(rlat)*np.sin(rj) +
                                   np.cos(rlat)*np.cos(rj)*np.cos(rlon-ri))
                if dist <= r:
                    res.append((i, j))
        return res

    def step_sim(self, ts):
        # CACLULATING A STEP OF SIMULATION
        m = Trend('poly05', 0, 0.15, 946080, 1)   # Trend object
        # Reset the parameters
        cov = 0   # Coverage
        rev = 0   # Overall revenue
        irev = 0   # Overall ideal revenue
        costs = 0   # Technical costs
        icosts = 0   # Ideal technical costs
        dens = 0   # Additional density on the altitude
        rpts = []
        irpts = []

        # Upload the right files with a lons and lats
        num = ts // 500
        with open('./PP_Data/D/{}'.format(num*500), 'rb', os.O_NONBLOCK) as f:
            d = pickle.load(f)

        for i in range(self.n):
            # Assembling and launch
            if ts == 0:
                costs += self.sat.launch_cost + self.sat.cost

            # Get the satellite coverage as generator
            points = self.coverage(self.sat, d[ts - num*500, i, 1],
                                   d[ts - num*500, i, 0], self.acc)
            # Check the satellite state for:
            # o -- operating
            # i -- interrupted
            # r -- on reparation
            # f -- failed
            # n -- not working
            if self.states[ts, i] == 'o':
                rpts.extend(points)
                costs += self.sat.operational_cost/2592000*self.step
                cov += self.sat.coverage
            elif self.states[ts, i] == 'i':
                costs += self.strat.replacement_cost
                costs += self.strat.day_cost/86400*self.step
            elif self.states[ts, i] == 'r':
                costs += self.strat.day_cost/86400*self.step
            elif self.states[ts, i] == 'f':
                dens += self.sat.vol

            irpts.extend(points)
            icosts += self.sat.operational_cost/2592000*self.step

        # Get the revenue for the coverage
        for p in set(rpts):
            rev += self.money[int(p[0]/self.acc),
                              int(p[1]/self.acc)]
        for p in set(irpts):
            irev += self.money[int(p[0]/self.acc),
                               int(p[1]/self.acc)]
        # Output array
        return [ts, cov, rev*m[ts], irev*m[ts], costs, icosts, dens]

    def export(self, *args):
        # Take the array to be exported, or nothing
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
