import numpy as np
from time import time as t
import csv


class Strategy:
    # The class of the spare strategy and the insurance strategy
    def __init__(self, strategy: str, sat, time: int):
        self.str = strategy   # Strategy type
        self.time = time   # Time for spare in seconds
        if strategy == 'none':   # No spare strategy, no insurance
            self.replacement_cost = 0   # Money for action
            self.start_cost = 0   # Money in the beginning
            self.day = 0   # Money daily
        elif strategy == 'lod':   # Launch-on-demand, no insurance
            self.replacement_cost = sat.cost + sat.launch_cost
            self.start_cost = 0
            self.day = 0


class Trend:

    def __init__(self, ttype, st, en, ent, maxm):
        st = st/maxm
        en = en/maxm
        self.start = st
        self.end = en
        self.endt = ent
        if ttype == 'lin':
            self.res = lambda t: (en-st)/ent*t + st
        elif ttype == 'poly2':
            self.res = lambda t: (en-st)/(en*ent)*t**2 + st
        elif ttype == 'expo':
            self.res = lambda t: st + np.exp(t*np.log(en-st)/ent)
        elif ttype == 'poly05':
            self.res = lambda t: (en-st)/(en*ent)*t**.5 + st
        else:
            raise TypeError('Wrong type!')

    def __getitem__(self, index: int):
        if index > self.endt:
            return self.end
        else:
            return self.res(index)


class Measurements:

    def __init__(self):
        pass

    def step(sim, step):
        sim.step = step
        start = t()
        sim.step_sim(step)
        return t() - start

    def step_selection(sim):
        sim.step = 1
        ideals = []

        # Create an output array
        results = np.zeros((6, 3))
        start_time = t()

        # Calculate the ideal numbers for comparison (step=1)
        for i in range(1001):
            if i != 0:
                ideals.append(ideals[i-1] + sim.step_sim(i)[3])
            else:
                ideals.append(sim.step_sim(i)[3])

        # Write down the timing results
        results[0, 1] = t() - start_time
        results[0, 0] = sim.step
        results[0, 2] = 0

        current = []
        for i in range(1, 6):
            sim.step = i*100
            start_time = t()

            # Run the sim with selected step in range of 1000
            for j in range(0, int(1000/sim.step) + 1):
                if j != 0:
                    current.append(current[j-1] + sim.step_sim(j*sim.step)[3])
                else:
                    current.append(sim.step_sim(j*sim.step)[3])

            # Write down the timing results
            results[i, 1] = t() - start_time
            results[i, 0] = sim.step

            # Calculate the average deviation & write in the results array
            summ = 0
            for k in range(1, int(1000/sim.step) + 1):
                ofi = int(k*sim.step)
                summ += np.abs(current[k] - ideals[ofi])/ideals[ofi]*100

            results[i, 2] = summ/(k + 1)

        # Export the results to the text file
        np.savetxt('./Step_selection.csv', results, delimiter=',', fmt='%1.3f',
                   header='step size (seconds), calc time(s), deviation (%)')


class Visualizations:

# =============================================================================
#     def sort_data(scale, array, parameter):
#         # scale -- step size in seconds not less then 100 seconds
#         # array -- output simulation array
#         # parameter -- sorting parameter (num 1:6)
#         # sim -- simulation class object
# 
#         if parameter < 1 and parameter > 6:
#             raise Exception('Wrong parameter number!')
# 
#         # Take the parameter that needed for visualisation
#         new_array = array[:, parameter]
# 
#         # Create new values arrays
#         results = np.zeros(())
#             
#         # Calculate the scale
#         for i in range(new_array.shape[0]):
#             if i*100 % scale == 0:
#                 new_x_vals.append(new_array[i, 0] / scale)
#                 new_y_vals.append(new_array[i, 1])
#                 
#                 max_val = np.amax(new_array[:, 1])
# 
#         order = 0
#         x = max_val
#         while x // 10 == 0:
#             order += 1
#             x = x // 10
# 
#         if order < 3:
#             # for i in new_arr
#         elif order >= 3 and order < 6:
#             
#         elif order >= 6 and order < 9:
#             
#         elif order >= 9:
# =============================================================================

    def read_csv2np(path_to_the_file: str):
        # Reading csv to the numpy array
        # Read the number of rows and columns
        with open(path_to_the_file, 'r') as file:
            reader = csv.reader(file)
            next(reader, None)
            rows = 0
            for row in reader:
                cols = len(row)
                rows += 1

        # Create an output array
        results = np.zeros((rows, cols))

        # Fill in the array
        with open(path_to_the_file, 'r') as file:
            reader = csv.reader(file)
            next(reader, None)
            for i, row in enumerate(reader):
                for j, val in enumerate(row):
                    results[i, j] = val

        # Return the array
        return results
                    
