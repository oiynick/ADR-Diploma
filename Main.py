import Classes
import numpy as np

# Boundary conditions
# Business
price = 100   # $ per month

# Satellite characteristics
mass = 400   # Kgs dry mass
vol = 0.1   # M3
alt = 1000   # km

# WeiBull probability, numbers from article
# https://doi.org/10.1016/j.ress.2009.05.004
ls = np.array([0.4521])
ks = np.array([2607])

# Constellation parameters
n = 1000
planes = 36

# Spare strategy
strat = 'none'

# Simulation parameters
step = 100   # seconds
simtime = 2592100   # seconds

# CREATE A NEW INSTANCE OF SIMULATION
sim = Classes.Simulation(mass, vol, ls, ks, 40, alt, 0.075,
                         n, planes, price,
                         strat,
                         simtime, step, 1)


sim.simulate()

sim.export()
