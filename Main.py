import Classes
import numpy as np
import multiprocessing as mp
import os

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

# Spare strategy
strat = 'none'

# Simulation parameters
step = 100   # seconds
simtime = 2592100   # seconds

print('Started!')

# CREATE A NEW INSTANCE OF SIMULATION
sim = Classes.Simulation(mass, vol, ls, ks, 40, alt, 0.075,
                         n, price,
                         strat,
                         simtime, step, 1)

print('Simulation class created, all the files have been loaded successfuly')

if __name__ == '__main__':

    cpus = 4   # Number of CPUs
    data = np.zeros((1, 7))   # Empty output array of shape
    steps = int(simtime / step)   # Amount of simulation steps
    ch = int(np.floor(steps / cpus))   # Chunk size
    pl = mp.get_context("spawn").Pool()   # Threading pool object

    print('chunk size is: {}, steps: {}, cpus: {}'.format(ch, steps, cpus))

    # Fill the pool with the functions
    res = []
    for i in range(cpus + 1):
        p = int((i // cpus) * (steps % cpus))   # Overchunked step parameter
        res.append(pl.apply_async(sim.part_sim, (ch*(i - 1), ch*i + p,)))

    # Close & join the pool to commit the operations on multiprocessing
    pl.close()
    pl.join()
    print('Pool has been closed, starting to process the results')

    # Create and fill the return array
    for r in res:
        np.append(data, r.get(), axis=0)

    # Calculate the cumulative sum of metrics (except coverage and timestep)
    cum = np.cumsum(data[:, 2:], 0)
    result = np.concatenate((data[:, :2], cum), 1)

    # Export the file
    sim.export(result)
