import numpy as np
from Classes.Helpers import Visualizations as viz
import plotly.offline as ply
import plotly.graph_objs as go
import plotly.io as pio
import pandas as pd


# Make colors
accent = '#FA7268'
dark = '#0A121F'
med = '#1B2B4C'
light = '#6A7B8F'


def step_data():
    step_select = viz.read_csv2np('./PP_Data/step_selection.csv')
    x_vals = []
    for i in step_select[1:, 0]:
        x_vals.append('{} sec.'.format(i))

    bar1 = go.Bar(x=x_vals, y=step_select[1:, 1],
                  name='Execution time on 1000 second',
                  marker=dict(color=dark))
    # Invisible one
    bar2 = go.Bar(x=x_vals, y=[0], hoverinfo='none',
                  showlegend=False)
    # Invisible one
    bar3 = go.Bar(x=x_vals, y=[0], yaxis='y2', hoverinfo='none',
                  showlegend=False)
    bar4 = go.Bar(x=x_vals, y=step_select[1:, 2],
                  name='Average maximum error on each step', yaxis='y2',
                  marker=dict(color=[accent, med, med, med, med]))
    scat1 = go.Scatter(x=x_vals, y=[25 for i in x_vals], yaxis='y2',
                       name='Considerable error', mode='lines',
                       marker=dict(color=med), line=dict(width=2))

    data = [bar1, bar2, bar3, bar4, scat1]

    layout = go.Layout(title='Time steps comparison',
                       barmode='group',
                       yaxis=dict(title='Time, sec.',
                                  showgrid=False,
                                  titlefont=dict(color=dark),
                                  tickfont=dict(color=dark)),
                       yaxis2=dict(title='Error, %',
                                   showgrid=False,
                                   titlefont=dict(color=med),
                                   tickfont=dict(color=med),
                                   side='right',
                                   overlaying='y'))
    fig = go.Figure(data=data, layout=layout)
    # ply.plot(fig, filename='Multiple axes')
    pio.write_image(fig, './Output/Charts and Images/step_selection.pdf')


def chunk_data():
    bar1 = go.Bar(x=[80, 315, 985, 1971, 3942, 7884, 15268],
                  y=[3, 5, 25, 50, 100, 100, 100],
                  name='Computational power used on 300K steps',
                  marker=dict(color=[dark, dark, dark, dark,
                                     accent, dark, dark]))
    layout = go.Layout(title='Chunk sizes comparison',
                       yaxis=dict(title='Power of 40 CPUs 3.2 GHz, %'),
                       xaxis=dict(title='Amount of steps'))
    data = [bar1]
    fig = go.Figure(data=data, layout=layout)
    ply.plot(fig)
    pio.write_image(fig, './Output/Charts and Images/chunk_selection.pdf')


def revenue_data():
    # WORKING WITH PANDAS HOOOORAYY!  NO:(
    data = viz.read_csv2np('20-05 03:55.csv')
    revenue = viz.sort_data(24*3600*7, data, 2)
    irevenue = viz.sort_data(24*3600*7, data, 3)

    scat1 = go.Scatter(x=revenue[:, 0], y=revenue[:, 1],
                       name='Revenue with no spare strategy', mode='lines',
                       marker=dict(color=dark), line=dict(width=2))
    scat2 = go.Scatter(x=irevenue[:, 0], y=irevenue[:, 1],
                       name='Ideal possible revenue', mode='lines',
                       marker=dict(color=med), line=dict(width=2))
    layout = go.Layout(title='Revenue revolution',
                       yaxis=dict(title=''),
                       xaxis=dict(title='Number of the week'))
    data = [scat1, scat2]
    py.plot()
    
# step_data()
chunk_data()
