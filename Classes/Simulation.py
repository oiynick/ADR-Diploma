import numpy as np
import os
import datetime as dt
from random import choices as rnd
from geopy import distance

# Custom classes import
from Classes.Strategy import Strategy
from Classes.Maths import Trend
from Classes.Satellite import Satellite
R = 6378.137


class Simulation:
    # The class bringing the simulation object

    def __init__(self, mass, volume, alfa, alt, cov,   # Sat
                 n: int, price: float,   # Constellation and service
                 strat: str,   # Classes
                 simtime: int, step: int, acc: float):   # Simulation
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
        self.sat = Satellite(mass, volume, alfa, alt, cov)

        # Fill the atributes of the simulation with numbers
        self.n = n
        self.simtime = simtime
        self.step = step
        self.acc = acc
        self.steps = int(np.floor(simtime / step))

        # Spare strategy
        self.strat = Strategy(strat, self.sat, 0)
        # Price of the flat-service per step
        self.price = price/2592000*step

        # Upload files longitude, latitude of the undersat point on the Earth
        # money is for money grid, lifetime is for array of lifetimes
        self.lon = np.loadtxt('./PP_Data/lon.txt').T
        self.lat = np.loadtxt('./PP_Data/lat.txt').T
        self.money = np.loadtxt('./PP_Data/data.txt')
        self.states = self.status()

    def status(self):
        # Upload the matrix of the probabilities
        arr = np.empty((self.steps, self.n), dtype='object')
        p = []
        for i in range(self.steps):
            p.append((1 - np.exp(-(i/81088128)**.4521)))
        lt = rnd(range(self.steps), weights=p, k=self.n)
        for ts in range(self.steps):
            for i in range(self.n):
                if ts < lt[i]:
                    arr[ts, i] = 'o'
                elif ts == lt[i]:
                    if self.strat.str == 'none':
                        arr[ts, i] = 'f'
                    else:
                        arr[ts, i] = 'i'
                        new_lt = rnd(range(self.steps), weights=p, k=1)
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

    def coverage(sat, lon, lat, acc):
        # Return the array of dots for the coverage area
        # lat-lon is satellite antenna focus point on Earth

        r = (sat.alt)*np.tan(np.pi * (sat.alfa/2)/180)   # Coverage radius
        mdist = np.ceil(r/100)   # Maximum possible deviation in degrees

        # Iterate through coords around the focus point
        for i in np.arange(np.floor(lon-mdist), np.ceil(lon+mdist), acc):
            for j in np.arange(np.floor(lat-mdist), np.ceil(lat+mdist), acc):
                # Calculate the distance and decide whether the point is in
                # the circle or not
                if distance.distance((lat, lon), (j, i)).km <= r:
                    yield (i, j)

    def step_sim(self, ts):
        # CACLULATING A STEP OF SIMULATION
        # TODO: take market real numbers for trend
        m = Trend('lin', 0.0005, 0.15, 155520, 1)   # Trend object
        # Reset the parameters
        cov = 0   # Coverage
        rev = 0   # Overall revenue
        irev = 0   # Overall ideal revenue
        costs = 0   # Technical costs
        icosts = 0   # Ideal technical costs
        dens = 0   # Additional density on the altitude

        for i in range(self.n):
            # Assembling and launch
            if ts == 0:
                costs += self.sat.launch_cost + self.sat.cost

            # Get the satellite coverage as generator
            points = Simulation.coverage(self.sat, self.lon[ts, i],
                                         self.lat[ts, i], self.acc)
            # Check the satellite state for:
            # o -- operating
            # i -- interrupted
            # r -- on reparation
            # f -- failed
            # n -- not working
            if self.states[ts, i] == 'o':
                costs += self.sat.operational_cost/2592000*self.step
                cov += self.sat.coverage
                revenue = 0
                # Get the revenue for the coverage
                for p in points:
                    revenue = self.money[int(p[0]/self.acc),
                                         int(p[1]/self.acc)]*self.price
                rev += revenue*m[ts]
            elif self.states[ts, i] == 'i':
                costs += self.strat.replacement_cost
                costs += self.strat.day_cost/86400*self.step
            elif self.states[ts, i] == 'r':
                costs += self.strat.day_cost/86400*self.step
            elif self.states[ts, i] == 'f':
                dens += self.sat.vol

            irev += revenue*m[ts]
            icosts += self.sat.operational_cost/2592000*self.step
        # Output array
        return np.array([ts, cov, rev, irev, costs, icosts, dens], ndmin=2)

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
