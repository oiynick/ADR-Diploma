import Classes
import numpy as np
import os
import tqdm
import multiprocessing as mp
from datetime import datetime as dt
import time

print('Starting time is {}'.format(dt.now().strftime("%H:%M:%S")))
# Boundary conditions
# Business
price = 100   # $ per month

# Satellite characteristics
mass = 400   # Kgs dry mass
vol = 0.1   # M3
alt = 1000   # km

# Constellation parameters
n = int(1000)

# Spare strategy
strat = 'none'

# Simulation parameters
step = int(100)   # seconds
simtime = int(2592100)   # seconds
steps = int(simtime/step)

# CREATE A NEW INSTANCE OF SIMULATION
sim = Classes.Simulation(mass, vol, 40, alt, 0.075,
                         n, price,
                         strat,
                         simtime, step, 1)

print('Prepared for simulation in {}'.format(dt.now().strftime("%H:%M:%S")))

# =============================================================================
# # Time check
# start = time.time()
# rtrn = sim.step_sim(1)
# =============================================================================

if __name__ == '__main__':
    cpus = os.cpu_count()
    pl = mp.Pool()   # Create the pool object
    args = range(int(simtime/step))   # The amount of steps as a step array

    data = np.zeros((1, 7))
    # Create a proress bar
    for _ in tqdm.tqdm(pl.imap_unordered(sim.step_sim, args,
                                         int(cpus + 1)), total=steps):
        print(_)
        np.append(data, _, axis=0)

    # UNCOMMENT FOR RUNNING FOR SHORTER (LONGER?) INTERVALS
# =============================================================================
#     for _ in tqdm.tqdm(pl.imap_unordered(sim.step_sim, args),
#                        total=len(args),
#                        miniters=1, mininterval=0.1):
#         np.append(data, _, axis=0)
# =============================================================================

    # Close & join the pool to commit the operations on multiprocessing
    pl.close()
    pl.join

    # Calculate the cumulative sum of metrics (except coverage and timestep)
    # cum = np.cumsum(data[:, 2:], 0)
    # result = np.concatenate((data[:, :2], cum), 1)

    # Export the file
    print('Finish time is {}'.format(dt.now().strftime("%H:%M:%S")))
    sim.export(data)
# =============================================================================
# if __name__ == '__main__':
#
#     cpus = os.cpu_count()   # Number of CPUs
#     data = np.zeros((1, 7))   # Empty output array of shape
#     steps = int(simtime / step)   # Amount of simulation steps
#     ch = int(np.floor(steps / cpus))   # Chunk size
#     # pl = mp.get_context("spawn").Pool()   # Threading pool object (context)
#     pl = mp.Pool()   # Threading pool object (no context)
# 
#     print('chunk size is: {}, steps: {}, cpus: {}'.format(ch, steps, cpus))
# 
#     # Fill the pool with the functions
#     res = []
#     for i in range(cpus + 1):
#         p = int((i // cpus) * (steps % cpus))   # Overchunked step parameter
#         res.append(pl.apply_async(sim.part_sim, (ch*(i - 1), ch*i + p,)))
# 
#     # Close & join the pool to commit the operations on multiprocessing
#     pl.close()
#     pl.join()
#     print('Pool has been closed, starting to process the results')
# 
#     # Create and fill the return array
#     for r in res:
#         np.append(data, r.get(), axis=0)
# 
#     # Calculate the cumulative sum of metrics (except coverage and timestep)
#     cum = np.cumsum(data[:, 2:], 0)
#     result = np.concatenate((data[:, :2], cum), 1)
# 
#     # Export the file
#     sim.export(result)
# =============================================================================
