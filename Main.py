import numpy as np

# Custom classes
import Classes
from Classes.Helpers import Measurements as mes
from Classes.Helpers import Visuals as viz
# from Preprocessing import population_grid
# Initiate the measurements class

# Multiprocessing tools
import multiprocessing as mp
import os

# Progress bar package
import tqdm

# Timing packages
from datetime import datetime as dt


print('Starting time is {}'.format(dt.now().strftime("%H:%M:%S")))
# Boundary conditions
# Satellite characteristics
mass = 400   # Kgs dry mass
vol = 0.1   # M3
alt = 1000   # km

# Constellation parameters
n = int(1600)

# Spare strategy
strat = 'none'

# Simulation parameters
step = int(500)   # seconds
simtime = int(157680500)   # seconds
tss = int(simtime/step)

# CREATE A NEW INSTANCE OF SIMULATION
sim = Classes.Simulation(mass, vol, 40, alt, 0.075,
                         n,
                         strat,
                         simtime, step, 1)

print('Prepared for simulation in {}'.format(dt.now().strftime("%H:%M:%S")))

# =============================================================================
# # Time measurements for one step of simulation
# time = mes.time_mes(sim, 1)
# =============================================================================

# =============================================================================
# # Selecting the best timestep
# mes.step_selection(sim)
# =============================================================================

if __name__ == '__main__':
    cpus = os.cpu_count()
    pl = mp.Pool(cpus)   # Create the pool object
    args = range(tss)   # The amount of steps as a step array

    data = []
    # Create a proress bar
    for i in tqdm.tqdm(pl.imap_unordered(sim.step_sim, args,
                                         int(tss/(2*cpus) + 1)), total=tss):
        data.append(i)

    # Close & join the pool to commit the operations on multiprocessing
    pl.close()
    pl.join
    out = np.array(data)

    # Sorting the array by the time axis
    sort = np.empty_like(out)
    ind = np.argsort(out[:, 0], axis=0)
    for i, ix in enumerate(ind):
        for j in range(len(out[0, :])):
            sort[i, j] = out[ix, j]

    # Calculate the cumulative sum of metrics (except coverage and timestep)
    cum = np.cumsum(sort[:, 2:], 0)
    result = np.concatenate((sort[:, :2], cum), 1)

    # Export the file
    print('Finish time is {}'.format(dt.now().strftime("%H:%M:%S")))
    sim.export(result)
