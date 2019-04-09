import General
import numpy as np

R = 6378.137   # EARTH RADIUS

# Boundary conditions
# Business
price = 75   # $ per month

# Orbital
spps = np.array([50, 50, 75, 75])   # Satellites per plane
alts = np.array([R + 1110, R + 1130, R + 1275, R + 1325])   # Altitudes
incs = np.array([53.8, 74, 81, 70])    # Inclinations
ppi = np.array([32, 8, 5, 6])   # Number of planes per inclination
eccs = np.array([0, 0, 0, 0])  # Eccentrisities

# Company details
hr = 10000   # Amount of employees in the company

# Satellite characteristics
mass = 400   # Kgs dry mass
vol = 0.1   # M3

# WeiBull probability
lams = np.array([])
ks = np.array([])

# Spare strategy
strat = 'none'
name = 'spacex'

# Time
mstart = np.array([0, 0, 0, 0, 0, 0])
step = 1
simtime = 1

# CREATE A NEW INSTANCE OF SIMULATION
Sim = General.Simulation(price, spps, incs, ppi, alts, eccs,
                         hr, vol, lams, ks, mass, strat, name)

Sim.simulate(mstart, step, simtime)

Sim.export()
