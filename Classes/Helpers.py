import numpy as np
from time import time as t
import csv
import plotly.offline as ply
import plotly.graph_objs as go
import plotly.io as pio
import pandas as pd


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


class Visuals:

    def __init__(self):
        # Make colors
        self.accent = '#FA7268'
        self.dark = '#0A121F'
        self.med = '#1B2B4C'
        self.light = '#6A7B8F'

    def sort_data(self, scale, array, parameter):
        # scale -- step size in seconds not less then 100 seconds
        # array -- output simulation array
        # parameter -- sorting parameter (num 1:6)
        # sim -- simulation class object

        if parameter < 1 and parameter > 6:
            raise Exception('Wrong parameter number!')

        # Take the parameter that needed for visualisation
        y = array[:, parameter]
        x = array[:, 0]

        # Create new values arrays
        new_x_vals = []
        new_y_vals = []

        # Calculate the scale
        for i in y:
            if i*100 % scale == 0:
                new_x_vals.append(x[i])
                new_y_vals.append(y[i] / scale)

        return np.array([new_x_vals, new_y_vals]).T

    def read_csv2np(self, path_to_the_file: str):
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

    def step_data(self):
        # Create a bar chart of the step selection process
        # Import the step timing and power calculations .csv
        s = self
        step_select = s.read_csv2np('./PP_Data/step_selection.csv')
        x_vals = []

        # Format the x axis
        for i in step_select[1:, 0]:
            x_vals.append('{} sec.'.format(i))

        # Create data for bar charts
        bar1 = go.Bar(x=x_vals, y=step_select[1:, 1],
                      name='Execution time on 1000 second',
                      marker=dict(color=s.dark))
        # Invisible one
        bar2 = go.Bar(x=x_vals, y=[0], hoverinfo='none',
                      showlegend=False)
        # Invisible one
        bar3 = go.Bar(x=x_vals, y=[0], yaxis='y2', hoverinfo='none',
                      showlegend=False)
        bar4 = go.Bar(x=x_vals, y=step_select[1:, 2],
                      name='Average maximum error on each step', yaxis='y2',
                      marker=dict(color=[s.accent, s.med,
                                         s.med, s.med, s.med]))

        # Create a line
        scat1 = go.Scatter(x=x_vals, y=[25 for i in x_vals], yaxis='y2',
                           name='Considerable error', mode='lines',
                           marker=dict(color=s.med), line=dict(width=2))

        data = [bar1, bar2, bar3, bar4, scat1]

        # Create figure layout
        layout = go.Layout(title='Time steps comparison',
                           barmode='group',
                           yaxis=dict(title='Time, sec.',
                                      showgrid=False,
                                      titlefont=dict(color=s.dark),
                                      tickfont=dict(color=s.dark)),
                           yaxis2=dict(title='Error, %',
                                       showgrid=False,
                                       titlefont=dict(color=s.med),
                                       tickfont=dict(color=s.med),
                                       side='right',
                                       overlaying='y'))

        # Create the figure
        fig = go.Figure(data=data, layout=layout)

        # Uncomment to view the figure
        # ply.plot(fig, filename='Multiple axes')

        # Output the figure
        pio.write_image(fig, './Output/Charts and Images/step_selection.pdf')

    def chunk_data(self):
        # Create the bar chart describing the chunk size selection
        s = self

        # Create data for the bar chart
        bar1 = go.Bar(x=[80, 315, 985, 1971, 3942, 7884, 15268],
                      y=[3, 5, 25, 50, 100, 100, 100],
                      name='Computational power used on 300K steps',
                      marker=dict(color=[s.dark, s.dark, s.dark, s.dark,
                                         s.accent, s.dark, s.dark]))

        # Create the layout for the figure
        layout = go.Layout(title='Chunk sizes comparison',
                           yaxis=dict(title='Power of 40 CPUs 3.2 GHz, %'),
                           xaxis=dict(title='Amount of steps'))
        data = [bar1]

        # Create the figure
        fig = go.Figure(data=data, layout=layout)

        # Uncomment to view the figure
        # ply.plot(fig)

        # Write out the figure
        pio.write_image(fig, './Output/Charts and Images/chunk_selection.pdf')

    def revenue_data(self, step: str):
        # Revenue chart export
        s = self

        # Select the step size
        steps = {'year': 36*24*365,
                 'month': 36*24*30,
                 'week': 36*24*7,
                 'day': 36*24,
                 'hour': 36}

        # Import the data from the latest .csv
        data = s.read_csv2np('20-05 03:55.csv')

        # Prepare the sorted data
        revenue = s.sort_data(steps[step], data, 2)
        irevenue = s.sort_data(24*3600*7, data, 3)

        # Prepare data for the plots
        scat1 = go.Scatter(x=revenue[:, 0], y=revenue[:, 1],
                           name='Revenue with no spare strategy', mode='lines',
                           marker=dict(color=s.dark), line=dict(width=2))
        scat2 = go.Scatter(x=irevenue[:, 0], y=irevenue[:, 1],
                           name='Ideal possible revenue', mode='lines',
                           marker=dict(color=s.med), line=dict(width=2))

        # Prepare the layout for the figure
        layout = go.Layout(title='Revenue revolution',
                           yaxis=dict(title=''),
                           xaxis=dict(title='Number of the week'))
        data = [scat1, scat2]

        # Create the figure
        fig = go.Figure(data=data, layout=layout)

        # Uncomment to view the figure
        # ply.plot(fig)

        # Write out the figure
        pio.write_image(fig, './Output/Charts and Images/revenues.pdf')
