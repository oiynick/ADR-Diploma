import numpy as np
from scipy import optimize as op
from time import time as t
import csv
import plotly.offline as ply
import plotly.graph_objs as go
import plotly.io as pio
from Classes.Satellite import Satellite


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
        self.darkop = 'rgba(10, 18, 31, 0.3)'
        self.accop = 'rgba(250, 114, 104, 0.3)'
        self.medop = 'rgba(27, 43, 76, 0.3)'
        self.lightop = 'rgba(106, 123, 143, 0.3)'

    def t(x):
        return .2158*np.exp(-3.0716*np.exp(-.0000000354*x))

    def t1(x, a, b, c):
        return a*np.exp(b*np.exp(c*x))

    def t2(x, a, b, c, d):
        return a*x**3 + b*x**2 + c*x + d

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
        for i in x:
            if i % scale == 0:
                index = int(i)
                new_x_vals.append(x[index] / scale)
                new_y_vals.append(y[index])

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

    def ram_data(self):
        # Exporting the data over RAM usage
        s = self

        # Make the numbers
        x = [i for i in range(101)]
        y = [0.1, 0.3, 0.5, 0.7, 0.9, 1, 1, 1.5, 1.7, 2, 2, 2, 2, 2, 2, 5, 7,
             9, 13, 18, 27, 34, 38, 35, 34, 33, 30, 27, 25, 24, 23, 22, 21,
             21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7, 21.8, 21.9, 22]
        for i in range(101 - len(y)):
            y.extend([22])
        scat1 = go.Scatter(x=x, y=y, mode='lines',
                           name='Optimal usage',
                           marker=dict(color=s.dark))
        data = [scat1]
        layout = go.Layout(title='RAM usage during the simulation',
                           xaxis=dict(title='Overall time execution, %'),
                           yaxis=dict(title='Usage, GiB'),
                           font=dict(family='Times New Roman', size=24))
        fig = go.Figure(data=data, layout=layout)

        # Uncomment to view the figure
        # ply.plot(fig, filename='ram')

        # Write out the figure
        pio.write_image(fig, './Output/Charts and Images/ram.pdf',
                        width=1080, height=720)

    def step_data(self):
        # Create a bar chart of the step selection process
        # Import the step timing and power calculations .csv
        s = self
        step = s.read_csv2np('./PP_Data/step_selection.csv')

        # Create data for bar charts
        bar1 = go.Scatter(x=step[:, 0], y=step[:, 1],
                          text=step[:, 1], textposition='top center',
                          name='Execution time on 1000 sec',
                          marker=dict(color=s.dark))

        bar4 = go.Scatter(x=step[:, 0], y=step[:, 2],
                          text=step[:, 1], textposition='top center',
                          name='Average maximum error', yaxis='y2',
                          marker=dict(color=s.light))

        # Create a line
        scat1 = go.Scatter(x=step[:, 0], yaxis='y2',
                           y=[25 for i in step[:, 0]],
                           name='Considerable error', mode='lines',
                           marker=dict(color=s.med), line=dict(width=.5,
                                                               dash='dash'))

        data = [bar1, bar4, scat1]

        # Create figure layout
        layout = go.Layout(title='Time steps comparison',
                           barmode='group',
                           font=dict(family='Times New Roman', size=24),
                           xaxis=dict(title='Step size, s'),
                           yaxis=dict(title='Time, sec.',
                                      showgrid=False),
                           yaxis2=dict(title='Average maximum error, %',
                                       overlaying='y',
                                       side='right', showgrid=False))

        # Create the figure
        fig = go.Figure(data=data, layout=layout)

        # Uncomment to view the figure
        # ply.plot(fig, filename='step')

        # Output the figure
        pio.write_image(fig, './Output/Charts and Images/step_selection.pdf',
                        width=1080, height=720)

    def chunk_data(self):
        # Create the bar chart describing the chunk size selection
        s = self

        # Create data for the bar chart
        bar1 = go.Bar(x=[80, 315, 985, 1971, 3942, 7884, 15268],
                      y=[3, 5, 25, 50, 100, 100, 100],
                      name='Computational power used on 300K steps',
                      text=[3, 5, 25, 50, 100, 100, 100],
                      textposition='auto',
                      marker=dict(color=[s.dark, s.dark, s.dark, s.dark,
                                         s.accent, s.dark, s.dark]))

        # Create the layout for the figure
        layout = go.Layout(title='Chunk sizes comparison',
                           yaxis=dict(title='CPU activity, %'),
                           xaxis=dict(title='Amount of steps'),
                           font=dict(family='Times New Roman', size=24))
        data = [bar1]

        # Create the figure
        fig = go.Figure(data=data, layout=layout)

        # Uncomment to view the figure
        # ply.plot(fig, filename='chunk')

        # Write out the figure
        pio.write_image(fig, './Output/Charts and Images/chunk.pdf',
                        width=1080, height=720)

    def losses_data(self, step: str, wrong_ms_model=False):
        # Losses chart export
        s = self
        v = Visuals

        # Select the step size
        steps = {'year': 36*24*365,
                 'month': 36*24*30,
                 'week': 36*24*7,
                 'day': 36*24,
                 'hour': 36}

        # Import the data from the latest .csv
        no_adr = s.read_csv2np('./Output/none.csv')
        adr = s.read_csv2np('./Output/adr.csv')

        if wrong_ms_model:
            n_uncum = np.zeros((no_adr.shape[0], 3))
            a_uncum = np.zeros((adr.shape[0], 2))
            for i in range(no_adr.shape[0]):
                n_uncum[i, 0] = no_adr[i, 0]
                a_uncum[i, 0] = adr[i, 0]
                if i != 0:
                    n_uncum[i, 1] = no_adr[i, 2] - no_adr[i - 1, 2]
                    n_uncum[i, 2] = no_adr[i, 3] - no_adr[i - 1, 3]
                    a_uncum[i, 1] = adr[i, 2] - adr[i - 1, 2]
                else:
                    n_uncum[i, 1] = no_adr[i, 2]
                    n_uncum[i, 2] = no_adr[i, 3]
                    a_uncum[i, 1] = adr[i, 2]

            no_adr = np.zeros((n_uncum.shape[0], 3))
            adr = np.zeros((a_uncum.shape[0], 2))
            for i in range(n_uncum.shape[0]):
                no_adr[i, 0] = n_uncum[i, 0]
                adr[i, 0] = a_uncum[i, 0]
                if i == 0:
                    no_adr[i, 1] = 0
                    no_adr[i, 2] = 0
                    adr[i, 1] = 0
                else:
                    no_adr[i, 1] = n_uncum[i, 1]/(.00000127*i**.5)*v.t(i*500)
                    no_adr[i, 2] = n_uncum[i, 2]/(.00000127*i**.5)*v.t(i*500)
                    adr[i, 1] = a_uncum[i, 1]/(.00000127*i**.5)*v.t(i*500)

        # Prepare the sorted data
        a_revenue = s.sort_data(steps[step], adr, 2)
        n_revenue = s.sort_data(steps[step], no_adr, 2)
        i_revenue = s.sort_data(steps[step], no_adr, 3)

        # Modify the data for the relative view
        diff_n = (i_revenue[1:, 1] - n_revenue[1:, 1]) / i_revenue[1:, 1] * 100
        diff_a = (i_revenue[1:, 1] - a_revenue[1:, 1]) / i_revenue[1:, 1] * 100
        diff = (a_revenue[1:, 1] - n_revenue[1:, 1]) / a_revenue[1:, 1] * 100
        x = i_revenue[1:, 0]

        # Labels
        label = ['{:1.3f}'.format(diff[i - 1]) for i in range(x.size)]

        # Prepare bar charts for plotting
        bar1 = go.Scatter(x=x, y=diff_n, name='No strategy and benchmark',
                          marker=dict(color=s.dark))
        bar2 = go.Scatter(x=x, y=diff_a, name='ADR and benchmark',
                          marker=dict(color=s.dark), line=dict(dash='dash'))
        bar3 = go.Bar(x=x, y=diff, name='Losses of revenue, ADR', text=label,
                      marker=dict(color=s.medop), textposition='auto')

        # Preparing data
        data1 = [bar1, bar2, bar3]

        # Setting up the layout
        layout1 = go.Layout(title='Benchmark revenue losses',
                            yaxis=dict(title='Loss, %'),
                            font=dict(family='Times New Roman', size=24),
                            xaxis=dict(title='Number of the month'))
        fig1 = go.Figure(data=data1, layout=layout1)

        # Uncomment to view the figure
        # ply.plot(fig1, filename='loss')

        # Write out the figure
        pio.write_image(fig1, './Output/Charts and Images/losses.pdf',
                        width=1080, height=720)

    def revenue_data(self, step: str, wrong_ms_model=False):
        # Revenue chart export
        s = self
        v = Visuals

        # Select the step size
        steps = {'year': 36*24*365,
                 'month': 36*24*30,
                 'week': 36*24*7,
                 'day': 36*24,
                 'hour': 36}

        # Import the data from the latest .csv
        no_adr = s.read_csv2np('./Output/none.csv')
        adr = s.read_csv2np('./Output/adr.csv')

        if wrong_ms_model:
            n_uncum = np.zeros((no_adr.shape[0], 3))
            a_uncum = np.zeros((adr.shape[0], 2))
            for i in range(no_adr.shape[0]):
                n_uncum[i, 0] = no_adr[i, 0]
                a_uncum[i, 0] = adr[i, 0]
                if i != 0:
                    n_uncum[i, 1] = no_adr[i, 2] - no_adr[i - 1, 2]
                    n_uncum[i, 2] = no_adr[i, 3] - no_adr[i - 1, 3]
                    a_uncum[i, 1] = adr[i, 2] - adr[i - 1, 2]
                else:
                    n_uncum[i, 1] = no_adr[i, 2]
                    n_uncum[i, 2] = no_adr[i, 3]
                    a_uncum[i, 1] = adr[i, 2]

            no_adr = np.zeros((n_uncum.shape[0], 3))
            adr = np.zeros((a_uncum.shape[0], 2))
            for i in range(n_uncum.shape[0]):
                no_adr[i, 0] = n_uncum[i, 0]
                adr[i, 0] = a_uncum[i, 0]
                if i == 0:
                    no_adr[i, 1] = 0
                    no_adr[i, 2] = 0
                    adr[i, 1] = 0
                else:
                    no_adr[i, 1] = n_uncum[i, 1]/(.00000127*i**.5)*v.t(i*500)
                    no_adr[i, 2] = n_uncum[i, 2]/(.00000127*i**.5)*v.t(i*500)
                    adr[i, 1] = a_uncum[i, 1]/(.00000127*i**.5)*v.t(i*500)

        # Prepare the sorted data
        a_revenue = s.sort_data(steps[step], adr, 2)
        n_revenue = s.sort_data(steps[step], no_adr, 2)
        i_revenue = s.sort_data(steps[step], no_adr, 3)

        # Prepare data for the plots
        scat1 = go.Scatter(x=a_revenue[:, 0], y=a_revenue[:, 1],
                           name='Revenue with ADR', mode='lines',
                           marker=dict(color=s.dark),
                           line=dict(width=1, dash='dot'))
        scat2 = go.Scatter(x=i_revenue[:, 0], y=i_revenue[:, 1],
                           name='Ideal possible revenue', mode='lines',
                           marker=dict(color=s.light), line=dict(width=1))
        scat3 = go.Scatter(x=n_revenue[:, 0], y=n_revenue[:, 1],
                           name='Revenue with no spare strategy', mode='lines',
                           marker=dict(color=s.med), line=dict(width=1))

        # Prepare the layout for the figure
        layout2 = go.Layout(title='Revenue revolution',
                            yaxis=dict(title='Revenue, US$'),
                            xaxis=dict(title='Number of the week'),
                            font=dict(family='Times New Roman', size=24))
        data2 = [scat1, scat2, scat3]

        # Create the figure
        fig2 = go.Figure(data=data2, layout=layout2)

        # Uncomment to view the figure
        # ply.plot(fig2, filename='rev')

        # Write out the figure
        pio.write_image(fig2, './Output/Charts and Images/revenues.pdf',
                        width=540, height=720)

    def density_data(self, step: str, vol):
        # Density charts export
        s = self

        # Select the step size
        steps = {'year': 36*24*365,
                 'month': 36*24*30,
                 'week': 36*24*7,
                 'day': 36*24,
                 'hour': 36}

        # Prepare the data
        no_adr = s.read_csv2np('./Output/none.csv')
        adr = s.read_csv2np('./Output/adr.csv')

        # Set the sandart distribution of the debris density
        lil = 1.146*10**(-6)*np.exp(-((1000 - 856.9)/126.7)**2)   # R20.92
        med = 1.34*10**(-7)*np.exp(-((1000 - 860.8)/153)**2)   # R20.83
        big = 3.016*10**(-8)*np.exp(-((1000 - 847.1)/171.2)**2)   # R20.72
        overal = lil + med + big

        # Prepare the data
        n_dens = s.sort_data(steps[step], no_adr, 6)[:, 1]/1454977.081 + overal
        x = s.sort_data(steps[step], no_adr, 6)[:, 0]
        a_dens = s.sort_data(steps[step], adr, 6)[:, 1]/1454977.081 + overal

        # Check the probability of the collision
        n_col = []
        a_col = []
        adelay = 0
        ndelay = 0
        for i in range(len(x)):
            atime = (x[i] - adelay) * 100 * steps[step]
            ntime = (x[i] - ndelay) * 100 * steps[step]
            n_col.append(1 - np.exp(-n_dens[i]*vol**(2/3)*.000001*ntime*12))
            a_col.append(1 - np.exp(-a_dens[i]*vol**(2/3)*.000001*atime*12))

        # Prepare the data for plots of the density
        scat1 = go.Scatter(x=x, y=n_dens, mode='lines',
                           name='Density (alt: 1000 km, inc: 53), no ADR',
                           marker=dict(color=s.dark), line=dict(width=1))
        scat2 = go.Scatter(x=x, y=a_dens, mode='lines',
                           name='Density (alt: 1000 km, inc: 53), ADR',
                           marker=dict(color=s.light), line=dict(width=1))

        # Prepare the data for plots of the collision probability
        scat3 = go.Scatter(x=x, y=n_col, mode='lines', yaxis='y2',
                           name='Collision probability, no ADR',
                           marker=dict(color=s.dark),
                           line=dict(width=1, dash='dash'))
        scat4 = go.Scatter(x=x, y=a_col, mode='lines', yaxis='y2',
                           name='Collision probability with ADR',
                           marker=dict(color=s.light),
                           line=dict(width=1, dash='dash'))

        data = [scat1, scat2, scat3, scat4]

        # Create the layout
        layout = go.Layout(title='Debris density and probability of collision',
                           xaxis=dict(title='Number of the week'),
                           font=dict(family='Times New Roman', size=24),
                           yaxis=dict(title='Density',
                                      showgrid=False,
                                      titlefont=dict(color=s.dark),
                                      tickfont=dict(color=s.dark)),
                           yaxis2=dict(title='Collision probability',
                                       showgrid=False,
                                       titlefont=dict(color=s.light),
                                       tickfont=dict(color=s.light),
                                       side='right',
                                       overlaying='y'))
        fig = go.Figure(data=data, layout=layout)

        # Uncomment to view the figure
        # ply.plot(fig, filename='dens')

        # Write out the figure
        pio.write_image(fig, './Output/Charts and Images/density.pdf',
                        width=1080, height=720)

    def coverage_data(self, step):
        # Export coverage data as a figure
        s = self

        # Select the step size
        steps = {'year': 36*24*365,
                 'month': 36*24*30,
                 'week': 36*24*7,
                 'day': 36*24,
                 'hour': 36}

        # Import the data from the latest .csv
        no_adr = s.read_csv2np('./Output/none.csv')
        adr = s.read_csv2np('./Output/adr.csv')

        # Prepare the data
        n_c = s.sort_data(steps[step], no_adr, 1)
        a_c = s.sort_data(steps[step], adr, 1)

        n_cov = []
        a_cov = []
        x = n_c[:, 0]
        for i in range(len(x)):
            n_cov.append(n_c[i, 1]/0.75*0.5)
            a_cov.append(a_c[i, 1]/0.75*0.5)

        scat1 = go.Scatter(x=x, y=n_cov, mode='lines',
                           name='Coverage, no ADR',
                           marker=dict(color=s.dark))
        scat2 = go.Scatter(x=x, y=a_cov, mode='lines',
                           name='Coverage with ADR',
                           marker=dict(color=s.light),
                           line=dict(dash='dash'))
        data = [scat1, scat2]

        # Create the layout
        layout = go.Layout(title='Coverage rate revolution',
                           xaxis=dict(title='Number of the week'),
                           yaxis=dict(title='Coverage rate, %'),
                           font=dict(family='Times New Roman', size=24))
        fig = go.Figure(data=data, layout=layout)

        # Uncomment to view the figure
        # ply.plot(fig, filename='cov')

        # Write out the figure
        pio.write_image(fig, './Output/Charts and Images/coverage.pdf',
                        width=1080, height=720)

    def timing_data(self):
        # Export timings

        s = self

        # Prepare the data
        x = [0.083, 1, 3, 5]
        y = [0.25, 7.38, 15.27, 40]

        # Prepare the charts data
        bar1 = go.Bar(x=x, y=y, marker=dict(color=[s.dark, s.accent,
                                                   s.darkop, s.darkop]),
                      name='Execution time', text=y, textposition='auto')
        data = [bar1]
        layout = go.Layout(title='Timings for different simulation periods',
                           yaxis=dict(title='Time, h'),
                           xaxis=dict(title='Simulation period, years'),
                           font=dict(family='Times New Roman', size=24))
        fig = go.Figure(data=data, layout=layout)

        # Uncomment to view the figure
        # ply.plot(fig, filename='time')

        # Write out the figure
        pio.write_image(fig, './Output/Charts and Images/time.pdf',
                        width=1080, height=720)

    def sats_data(self):
        # Printing four charts with data over
        s = self

        x = [1000, 1600]

        # Import file
        data1 = s.read_csv2np('./Output/old.csv')
        data12 = s.read_csv2np('./Output/none.csv')
        data12a = s.read_csv2np('./Output/adr.csv')
        mo = data1.shape[0] - 1

        # Coverage information
        cov_n = [np.average(data1[:, 1]), np.average(data12[:mo, 1])*.67]
        cov_a = [np.average(data1[:, 1])*1.15, np.average(data12a[:mo, 1])*.67]

        # Costs sum info
        cos_n = [data1[mo, 4], data12[mo, 4]]
        cos_a = [data1[mo, 4]*1.15, data12a[mo, 4]]

        # Revenue sum info
        rev_n = [data1[mo, 2]/100, data12[mo, 2]]
        rev_a = [data1[mo, 3]/100, data12a[mo, 2]]

        # Losses data
        one = (data1[mo, 3] - data1[mo, 2]) / data1[mo, 3]*100
        two = (data12[mo, 3] - data12[mo, 2]) / data12[mo, 3]*100
        three = (data12a[mo, 3] - data12a[mo, 2]) / data12a[mo, 3]*100
        los_n = [one, two]
        los_a = [three, three]

        covn_l = ['{:1.2f}'.format(i) for i in cov_n]
        cova_l = ['{:1.2f}'.format(i) for i in cov_a]

        cosn_l = ['{:1.2f}'.format(i) for i in cos_n]
        cosa_l = ['{:1.2f}'.format(i) for i in cos_a]

        revn_l = ['{:1.2f}'.format(i) for i in rev_n]
        reva_l = ['{:1.2f}'.format(i) for i in rev_a]

        losn_l = ['{:1.2f}'.format(i) for i in los_n]
        losa_l = ['{:1.2f}'.format(i) for i in los_a]

        # Create bar charts
        bar1 = go.Bar(x=x, y=cov_n, marker=dict(color=s.dark),
                      name='No ADR', text=covn_l, textposition='auto')
        bar2 = go.Bar(x=x, y=cov_a, marker=dict(color=s.light),
                      name='ADR', text=cova_l, textposition='auto')
        bar3 = go.Bar(x=x, y=cos_n, marker=dict(color=s.dark),
                      name='No ADR', yaxis='y2', xaxis='x2',
                      showlegend=False, text=cosn_l, textposition='auto')
        bar4 = go.Bar(x=x, y=cos_a, marker=dict(color=s.light),
                      name='ADR', yaxis='y2', xaxis='x2',
                      showlegend=False, text=cosa_l, textposition='auto')
        bar5 = go.Bar(x=x, y=rev_n, marker=dict(color=s.dark),
                      name='No ADR', yaxis='y3', xaxis='x3',
                      showlegend=False, text=revn_l, textposition='auto')
        bar6 = go.Bar(x=x, y=rev_a, marker=dict(color=s.light),
                      name='ADR', yaxis='y3', xaxis='x3',
                      showlegend=False, text=reva_l, textposition='auto')
        bar7 = go.Bar(x=x, y=los_n, marker=dict(color=s.dark),
                      name='No ADR', yaxis='y4', xaxis='x4',
                      showlegend=False, text=losa_l, textposition='auto')
        bar8 = go.Bar(x=x, y=los_a, marker=dict(color=s.light),
                      name='ADR', yaxis='y4', xaxis='x4',
                      showlegend=False, text=losn_l, textposition='auto')

        data = [bar1, bar2, bar3, bar4, bar5, bar6, bar7, bar8]

        layout = go.Layout(title='Number of satellite influence',
                           barmode='group',
                           font=dict(family='Times New Roman', size=24),
                           xaxis=dict(domain=[0, 0.45],
                                      title='Number of sats'),
                           yaxis=dict(domain=[0, 0.45],
                                      title='Average coverage (1 mo), %'),
                           xaxis2=dict(domain=[0.55, 1],
                                       title='Number of sats'),
                           xaxis3=dict(domain=[0, 0.45], anchor='y3',
                                       title='Number of sats'),
                           xaxis4=dict(domain=[0.55, 1], anchor='y4',
                                       title='Number of sats'),
                           yaxis2=dict(domain=[0, 0.45], anchor='x2',
                                       title='Costs (end of 1 mo), US$'),
                           yaxis3=dict(domain=[0.55, 1],
                                       title='Revenue (end of 1 mo), US$'),
                           yaxis4=dict(domain=[0.55, 1], anchor='x4',
                                       title='Losses (end of 1 mo), %'))
        fig = go.Figure(data=data, layout=layout)

        # Uncomment to view the figure
        # ply.plot(fig, filename='sats')

        # Write out the figure
        pio.write_image(fig, './Output/Charts and Images/sats.pdf',
                        width=2160, height=1440)

    def replacement_data(self):
        # Replacement timing change
        s = self

        x = [20, 25, 30, 35, 40, 45, 50, 55, 60]
        adr = [3.767, 3.791, 3.836, 3.912, 4.11, 4.23, 4.33, 4.4, 4.567]

        bar = go.Bar(x=x, y=adr, showlegend=False,
                     marker=dict(color=[s.dark, s.dark, s.dark, s.dark,
                                        s.dark, s.dark, s.accent, s.dark,
                                        s.dark]), text=adr,
                     textposition='auto')

        data = [bar]

        layout = go.Layout(title='Losses over replacement time',
                           xaxis=dict(title='Time for reparation, days'),
                           yaxis=dict(title='Losses for the 1 mo period, %'),
                           font=dict(family='Times New Roman', size=24))

        fig = go.Figure(data=data, layout=layout)

        # Uncomment to view the figure
        # ply.plot(fig, filename='replace')

        # Write out the figure
        pio.write_image(fig, './Output/Charts and Images/replacement.pdf',
                        width=1080, height=720)

    def costs_data(self):
        # Display the costs distribution
        s = self

        # Create sat object
        sat = Satellite(400, 0.1, 40, 1000, 0.005)
        # Prepare the data
        no_adr = s.read_csv2np('./Output/none.csv')
        adr = s.read_csv2np('./Output/adr.csv')

        # Set the sandart distribution of the debris density
        lil = 1.146*10**(-6)*np.exp(-((1000 - 856.9)/126.7)**2)   # R20.92
        med = 1.34*10**(-7)*np.exp(-((1000 - 860.8)/153)**2)   # R20.83
        big = 3.016*10**(-8)*np.exp(-((1000 - 847.1)/171.2)**2)   # R20.72
        overal = lil + med + big

        # Prepare the data over Risks
        n_dens = no_adr[no_adr.shape[0] - 1, 6]/1454977.081 + overal
        a_dens = adr[adr.shape[0] - 1, 6]/1454977.081 + overal

        time = 315361 * 100
        n_prob = 1 - np.exp(-n_dens*sat.vol**(2/3)*.000001*time*12)
        a_prob = 1 - np.exp(-a_dens*sat.vol**(2/3)*.000001*time*12)

        n_risk = n_prob * 1600 * (sat.cost + sat.launch_cost) * 100
        a_risk = a_prob * 1600 * (sat.cost + sat.launch_cost) * 100

        n_cost = no_adr[no_adr.shape[0] - 1, 4]
        a_cost = adr[adr.shape[0] - 1, 4]

        n_spare = 0
        a_spare = adr[adr.shape[0] - 1, 4] - adr[adr.shape[0] - 1, 5]

        labels = ['Risk assessment', 'Regular costs', 'Spare costs']
        vals1 = [n_risk, n_cost, n_spare]
        vals2 = [n_risk, a_cost, a_spare]
        vals3 = [a_risk, a_cost, a_spare]
        colors = [s.accent, s.dark, s.light]

        pie1 = go.Pie(labels=labels, values=vals1, hole=0.4,
                      domain=dict(column=0),
                      marker=dict(colors=colors), textinfo='value+percent')
        pie2 = go.Pie(labels=labels, values=vals2, hole=0.4,
                      domain=dict(column=1),
                      marker=dict(colors=colors), textinfo='value+percent')
        pie3 = go.Pie(labels=labels, values=vals3, hole=0.4,
                      domain=dict(column=2),
                      marker=dict(colors=colors), textinfo='value+percent')

        data = [pie1, pie2, pie3]

        layout = go.Layout(title='Cost distributions',
                           grid=dict(rows=1, columns=3),
                           font=dict(family='Times New Roman', size=24))

        fig = go.Figure(data=data, layout=layout)

        # Uncomment to view the figure
        # ply.plot(fig, filename='cost')

        # Write out the figure
        pio.write_image(fig, './Output/Charts and Images/costs.pdf',
                        width=1080, height=720)

    def rev5_data(self, step: str):
        # Revenue chart export
        s = self

        # Select the step size
        steps = {'year': 36*24*365,
                 'month': 36*24*6,
                 'week': 36*24*7/5,
                 'day': 36*24/5,
                 'hour': 36/5}

        # Import the data from the latest .csv
        data = s.read_csv2np('./Output/3y.csv')

        uncum = np.zeros((data.shape[0], 3))
        for i in range(data.shape[0]):
            uncum[i, 0] = data[i, 0]
            if i != 0:
                uncum[i, 1] = data[i, 2] - data[i - 1, 2]
                uncum[i, 2] = data[i, 3] - data[i - 1, 3]
            else:
                uncum[i, 1] = data[i, 2]
                uncum[i, 2] = data[i, 3]

        new = np.zeros((uncum.shape[0], 3))
        for i in range(uncum.shape[0]):
            new[i, 0] = uncum[i, 0]
            if i == 0:
                new[i, 1] = 0
                new[i, 2] = 0
            else:
                new[i, 1] = uncum[i, 1]/(0.00000127*i**.5)*Visuals.t(i*500)
                new[i, 2] = uncum[i, 2]/(0.00000127*i**.5)*Visuals.t(i*500)

        cum = np.cumsum(new[:, 1:], 0)
        result = np.concatenate((new[:, :1], cum), 1)

        # Prepare the sorted data
        rev = s.sort_data(steps[step], result, 1)
        i_rev = s.sort_data(steps[step], result, 2)

        # Prepare data for the plots
        scat1 = go.Scatter(x=rev[:, 0], y=rev[:, 1], marker=dict(color=s.dark),
                           name='Revenue with ADR', mode='lines',
                           line=dict(width=1, dash='dash'))
        scat2 = go.Scatter(x=i_rev[:, 0], y=i_rev[:, 1],
                           name='Ideal possible revenue', mode='lines',
                           marker=dict(color=s.light), line=dict(width=1))

        # Prepare the layout for the figure
        layout2 = go.Layout(title='Revenue revolution',
                            yaxis=dict(title='Revenue, US$'),
                            xaxis=dict(title='Number of the {}'.format(step)),
                            font=dict(family='Times New Roman', size=24))
        data2 = [scat1, scat2]

        # Create the figure
        fig2 = go.Figure(data=data2, layout=layout2)

        # Uncomment to view the figure
        # ply.plot(fig2, filename='rev')

        # Write out the figure
        pio.write_image(fig2, './Output/Charts and Images/rev5ye.pdf',
                        width=540, height=720)

    def revnoncum_data(self, step: str):
        # Revenue chart export
        s = self
        v = Visuals

        # Select the step size
        steps = {'year': 36*24*365,
                 'month': 36*24*6,
                 'week': 7*24*7,
                 'day': 36*24/5,
                 'hour': 36/5}

        # Import the data from the latest .csv
        data = s.read_csv2np('./Output/3y.csv')

        uncum = np.zeros((data.shape[0], 3))
        for i in range(data.shape[0]):
            uncum[i, 0] = data[i, 0]
            if i != 0:
                uncum[i, 1] = data[i, 2] - data[i - 1, 2]
                uncum[i, 2] = data[i, 3] - data[i - 1, 3]
            else:
                uncum[i, 1] = data[i, 2]
                uncum[i, 2] = data[i, 3]

        new = np.zeros_like(uncum)
        for i in range(uncum.shape[0]):
            new[i, 0] = uncum[i, 0]
            if i == 0:
                new[i, 1] = 0
                new[i, 2] = 0
            else:
                new[i, 1] = uncum[i, 1]/(0.00000127*i**.5)*Visuals.t(i*500)
                new[i, 2] = uncum[i, 2]/(0.00000127*i**.5)*Visuals.t(i*500)

        ua_rev = s.sort_data(steps[step], new, 1)
        ui_rev = s.sort_data(steps[step], new, 2)

        x = ua_rev[:, 0]
        ua_rev = ua_rev[:, 1]*100
        ui_rev = ui_rev[:, 1]*100

        # Fit curves
        a_coef, oth1 = op.curve_fit(v.t2, x, ua_rev)
        i_coef, oth2 = op.curve_fit(v.t2, x, ui_rev)

        fit = np.zeros((x.shape[0], 2))
        for i in x:
            i = int(i)
            fit[i, 0] = Visuals.t2(i, *a_coef)
            fit[i, 1] = Visuals.t2(i, *i_coef)

        # Prepare data for the plots
        scat1 = go.Scatter(x=x, y=ua_rev, marker=dict(color=s.darkop),
                           name='Revenue with ADR', mode='lines',
                           line=dict(width=1))
        scat2 = go.Scatter(x=x, y=ui_rev, marker=dict(color=s.lightop),
                           name='Benchmark revenue', mode='lines',
                           line=dict(width=1))
        scat3 = go.Scatter(x=x, y=fit[:, 0], marker=dict(color=s.dark),
                           name='Revenue with ADR, approximation',
                           mode='lines', line=dict(width=1))
        scat4 = go.Scatter(x=x, y=fit[:, 1], marker=dict(color=s.light),
                           name='Benchmark revenue, approximation',
                           mode='lines', line=dict(width=1))

        # Prepare the layout for the figure
        layout2 = go.Layout(title='Non-cummulative revenue evolution',
                            yaxis=dict(title='Revenue, US$'),
                            xaxis=dict(title='Number of the {}'.format(step)),
                            font=dict(family='Times New Roman', size=24))
        data2 = [scat1, scat2, scat3, scat4]

        # Create the figure
        fig2 = go.Figure(data=data2, layout=layout2)

        # Uncomment to view the figure
        # ply.plot(fig2, filename='rev')

        # Write out the figure
        pio.write_image(fig2, './Output/Charts and Images/noncum_rev.pdf',
                        width=1080, height=720)

    def verification1_data(self):
        # Revenue chart export
        s = self

        # Import the data from the latest .csv
        data = s.read_csv2np('./Output/3y.csv')

        uncum = np.zeros((data.shape[0], 3))
        for i in range(data.shape[0]):
            uncum[i, 0] = data[i, 0]
            if i != 0:
                uncum[i, 1] = data[i, 2] - data[i - 1, 2]
                uncum[i, 2] = data[i, 3] - data[i - 1, 3]
            else:
                uncum[i, 1] = data[i, 2]
                uncum[i, 2] = data[i, 3]

        new = np.zeros((uncum.shape[0], 3))
        for i in range(uncum.shape[0]):
            new[i, 0] = uncum[i, 0]
            if i == 0:
                new[i, 1] = 0
                new[i, 2] = 0
            else:
                new[i, 1] = uncum[i, 1]/(0.00000127*i**.5)*Visuals.t(i*500)
                new[i, 2] = uncum[i, 2]/(0.00000127*i**.5)*Visuals.t(i*500)

        cum = np.cumsum(new[:, 1:], 0)
        result = np.concatenate((new[:, :1], cum), 1)

        # Prepare the sorted data
        rev = s.sort_data(36*24*365/5, result, 2)

        # Prepare data for the plots
        scat1 = go.Bar(x=rev[:, 0], y=rev[:, 1], marker=dict(color=s.med))

        # Prepare the layout for the figure
        layout2 = go.Layout(title='Revenue annual summ revolution',
                            yaxis=dict(title='Revenue, US$'),
                            xaxis=dict(title='Number of the year'),
                            font=dict(family='Times New Roman', size=24))
        data2 = [scat1]

        # Create the figure
        fig2 = go.Figure(data=data2, layout=layout2)

        # Uncomment to view the figure
        # ply.plot(fig2, filename='rev')

        # Write out the figure
        pio.write_image(fig2, './Output/Charts and Images/spacex.pdf',
                        width=1080, height=720)

    def verification2_data(self):
        # Revenue chart export
        s = self

        # Import the data from the latest .csv
        data = s.read_csv2np('./Output/3y.csv')

        uncum = np.zeros((data.shape[0], 3))
        for i in range(data.shape[0]):
            uncum[i, 0] = data[i, 0]
            if i != 0:
                uncum[i, 1] = data[i, 2] - data[i - 1, 2]
                uncum[i, 2] = data[i, 3] - data[i - 1, 3]
            else:
                uncum[i, 1] = data[i, 2]
                uncum[i, 2] = data[i, 3]

        new = np.zeros((uncum.shape[0], 3))
        for i in range(uncum.shape[0]):
            new[i, 0] = uncum[i, 0]
            if i == 0:
                new[i, 1] = 0
                new[i, 2] = 0
            else:
                new[i, 1] = uncum[i, 1]/(0.00000127*i**.5)*Visuals.t(i*500)
                new[i, 2] = uncum[i, 2]/(0.00000127*i**.5)*Visuals.t(i*500)

        cum = np.cumsum(new[:, 1:], 0)
        result = np.concatenate((new[:, :1], cum), 1)

        # Prepare the sorted data
        rev = s.sort_data(36*24*365/5, result, 2)

        # Make non-cumulative again
        n_rev = np.zeros((rev.shape[0], 2))
        for i in range(rev.shape[0]):
            n_rev[i, 0] = rev[i, 0]
            if i != 0:
                n_rev[i, 1] = rev[i, 1] - rev[i - 1, 1]
            else:
                n_rev[i, 1] = rev[i, 1]

        # Prepare data for the plots
        scat1 = go.Bar(x=n_rev[:, 0], y=n_rev[:, 1] / 75,
                       marker=dict(color=s.med))

        # Prepare the layout for the figure
        layout2 = go.Layout(title='Revenue annual summ revolution',
                            yaxis=dict(title='Revenue, US$'),
                            xaxis=dict(title='Number of the year'),
                            font=dict(family='Times New Roman', size=24))
        data2 = [scat1]

        # Create the figure
        fig2 = go.Figure(data=data2, layout=layout2)

        # Uncomment to view the figure
        # ply.plot(fig2, filename='rev')

        # Write out the figure
        pio.write_image(fig2, './Output/Charts and Images/iridium.pdf',
                        width=1080, height=720)

    def comparison_data(self):
        # Create a scatter polar plot of the comparison of different business
        # models
        s = self

        x = ['Model flexibility', 'Model reliability',
             'Customer attractiveness', 'Service supplier attractiveness',
             'Market acquisition rate', 'Investment attractiveness',
             'Cashflow stability', 'DCF growth rate']
        y1 = [3, 7, 10, 5, 6, 3, 1, 2]
        y2 = [5, 8, 4, 9, 6, 4, 10, 6]
        y3 = [7, 6, 8, 8, 6, 4, 9, 5]

        scat1 = go.Scatterpolar(r=y1, theta=x, marker=dict(color=s.dark),
                                line=dict(width=3), name='Pay-as-go')
        scat2 = go.Scatterpolar(r=y2, theta=x, marker=dict(color=s.light),
                                line=dict(width=3), name='Flat')
        scat3 = go.Scatterpolar(r=y3, theta=x, marker=dict(color=s.accent),
                                line=dict(width=3), name='Dynamic flat')
        data = [scat1, scat2, scat3]

        layout = go.Layout(polar=dict(radialaxis=dict(visible=True,
                                                      range=[0, 10])))
        fig = go.Figure(data=data, layout=layout)

        # Create a figure
        # ply.plot(fig)

        # Write out the figure
        pio.write_image(fig, './Output/Charts and Images/rose_comp.pdf',
                        width=1080, height=720)

    def satsdiff_data(self, step):
        # Revenue chart export
        s = self

        # Select the step size
        steps = {'year': 36*24*365,
                 'month': 36*24*6,
                 'week': 36*24*7/5,
                 'day': 36*24/5,
                 'hour': 36/5}

        # Import the data from the latest .csv
        data = s.read_csv2np('./Output/3y.csv')

        uncum = np.zeros((data.shape[0], 3))
        for i in range(data.shape[0]):
            uncum[i, 0] = data[i, 0]
            if i != 0:
                uncum[i, 1] = data[i, 2] - data[i - 1, 2]
                uncum[i, 2] = data[i, 3] - data[i - 1, 3]
            else:
                uncum[i, 1] = data[i, 2]
                uncum[i, 2] = data[i, 3]

        new = np.zeros((uncum.shape[0], 3))
        for i in range(uncum.shape[0]):
            new[i, 0] = uncum[i, 0]
            if i == 0:
                new[i, 1] = 0
                new[i, 2] = 0
            else:
                new[i, 1] = uncum[i, 1]/(0.00000127*i**.5)*Visuals.t(i*500)
                new[i, 2] = uncum[i, 2]/(0.00000127*i**.5)*Visuals.t(i*500)

        ua_rev = s.sort_data(steps[step], new, 1)
        ui_rev = s.sort_data(steps[step], new, 2)

        x = ua_rev[:, 0]

        # Fit curves
        a_coef, oth1 = op.curve_fit(Visuals.t1, x, ua_rev[:, 1])
        i_coef, oth2 = op.curve_fit(Visuals.t1, x, ui_rev[:, 1])

        print(a_coef, i_coef)
        fit = np.zeros((x.shape[0], 2))
        for i in x:
            i = int(i)
            fit[i, 0] = Visuals.t(i*500)
            fit[i, 1] = Visuals.t(i*500)

        # Prepare data for the plots
        scat1 = go.Scatter(x=x, y=ua_rev[:, 1], marker=dict(color=s.darkop),
                           name='One lost satellite', mode='lines',
                           line=dict(width=1, dash='dash'), fill='tozeroy')
        scat2 = go.Scatter(x=x, y=ui_rev[:, 1], marker=dict(color=s.lightop),
                           name='Two consequent satellites', mode='lines',
                           line=dict(width=1, dash='dash'), fill='tozeroy')

        # Prepare the layout for the figure
        layout2 = go.Layout(title='Non-cummulative revenue evolution',
                            yaxis=dict(title='Revenue, US$'),
                            xaxis=dict(title='Number of the seconds'),
                            font=dict(family='Times New Roman', size=24))
        data2 = [scat1, scat2]

        # Create the figure
        fig2 = go.Figure(data=data2, layout=layout2)

        # Uncomment to view the figure
        # ply.plot(fig2, filename='rev')

        # Write out the figure
        pio.write_image(fig2, './Output/Charts and Images/noncum_rev.pdf',
                        width=1080, height=720)

    def reward_data(self):
        s = self

        x = [i for i in range(13)]
        y = [0.72, 0.77, 0.81, 0.99, 1.12, 1.25, 1.33, 1.4, 1.47,
             1.53, 1.56, 1.58, 2]

        data = [go.Bar(x=x, y=y, showlegend=False, text=y, textposition='auto',
                       marker=dict(color=s.dark))]

        layout = go.Layout(title='Revenue revolution',
                           yaxis=dict(title='Base cost multiplier'),
                           xaxis=dict(title='Month of the 1st year'),
                           font=dict(family='Times New Roman', size=24))

        fig2 = go.Figure(data=data, layout=layout)
        pio.write_image(fig2, './Output/Charts and Images/reward.pdf',
                        width=1080, height=720)
