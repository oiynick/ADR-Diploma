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

    # CPU data
    cpus = os.cpu_count()
    # Create an empty data array
    data = np.array([0, 0, 0, 0, 0, 0, 0])
    # Calculate the chunk size
    ch = int(np.floor(simtime/(step*cpus)))
    # Calculate the amount of steps
    steps = simtime/step
    # Create a pool object
    pool = mp.Pool()
    # Assign the chunked time array to the unprinting function
    res = [pool.apply_async(sim.part_sim,
                            (int(ch*i),
                             int(ch*(i+1)),)) for i in range(int(cpus-1))]
    # Assign the last function as printed and give it remaining elements
    res_print = pool.apply_async(sim.part_sim,
                                 (
                                         int(ch*(cpus-1)),
                                         int(cpus*ch + steps % cpus),
                                         True,
                                         ))
    # Close & join the pool to commit the operations on multiprocessing
    pool.close()
    pool.join()
    # Create the array of addition (to calculate the cumulatiive metrics)
    last = [0, 0, 0, 0, 0, 0, 0]
    for r in res:
        # Obtain the result of the calculations
        temp = r.get()
        # Append the results to the output array
        np.append(data, temp, axis=0)
    np.append(data, res_print.get(), axis=0)

    # Calculate the cumulative sum of metrics (except coverage and timestep)
    cum = np.cumsum(data[:, 2:], 0)
    result = np.concatenate((data[:, :2], cum), 1)
    # Export the file
    sim.export(result)
