import numpy as np
import csv
from aeronet import dataset as ds
import shapely
import pickle


def smart_interp(array, value):
    # Runs the linear interpolation if it is necessary
    # If there's any value that not follows the array - return Exception
    for i in range(len(array)):
        if value == array[i][0]:
            toggle = True
            return array[i][1]
        elif value > float(array[i][0]) and value < float(array[i+1][0]):
            y2 = float(array[i+1][1])
            y1 = float(array[i][1])
            x2 = float(array[i+1][0])
            x1 = float(array[i][0])

            new_y = value*(y2-y1)/(x2-x1) + (x1*y2-x2*y1)/(x1-x2)
            toggle = True
            return new_y

    if value > array[len(array)-1][0] or value < array[0][0] or ~toggle:
        raise Exception('Out of array range or smth else happened!')


def pop_array(path):
    # Preparing and reshaping the array of the population data
    pop_data = np.loadtxt(path, skiprows=6)   # Loading data from file
    # Rotating and transosing since the beginning of the data is no the
    # beginning of the array
    np.flip(pop_data, 0)
    pop_data = pop_data.T
    # Filling missing batches with zeros
    pop = np.zeros((360, 30))
    pop_finish = np.zeros((360, 5))
    # Gluing arrays up
    pop = np.append(pop, pop_data, 1)
    pop = np.append(pop, pop_finish, 1)
    return pop


def country(FeatureCollection, X, Y):
    # Determine the country by the coordinates
    # The poin with the coordinates
    Dot = shapely.geometry.Point(X, Y)
    # The grid boundary box
    Box = shapely.geometry.box(-180., -90., 180., 90.)
    # Determine which shape contains the point
    for Feature in FeatureCollection:
        geometry = Feature.shape
        if geometry.contains(Dot) and Box.contains(Dot):
            # Return the country code of the shape
            return str(Feature.geojson['properties']['ADM0_A3']).lower()
    # Otherwise return 'other' code
    return str('oth')


def gen_countries(f_json, acc):
    # Generate a country array based on coords
    # Open world geojson shape map
    fcol = ds.FeatureCollection.read(f_json)
    # Generate the empty array of a shape (360, 180)
    countries = np.empty((360, 180), dtype='object')

    # Iterate through coords
    for i in range(360):
        for j in range(180):
            # Determine the country and write its code to the array
            con = country(fcol, i - 180, j - 90)
            countries[i, j] = con

    # Save array to the text file
    np.savetxt('./PP_Data/countries_list.txt', countries, fmt='%s',
               header='xlt = -180, ylt = -90, step = {}'.format(acc))
    return countries


def country_data():
    # Households size from .csv
    # Calculate the number of rows in the CDV
    with open('./Raw_data/countries.csv', 'r') as hh:
        rd_0 = csv.reader(hh)
        rows = sum(1 for i in rd_0)
    # Open the file for reading
    with open('./Raw_data/countries.csv', 'r') as hh:
        rd_0 = csv.reader(hh)
        data = np.empty((5, rows), dtype='object')
        for i, row in enumerate(rd_0):
            if i > 0:
                data[0, i] = str(row[0]).lower()   # Read the country code
                data[1, i] = float(row[1])   # Read the hh size
                data[2, i] = float(row[3])   # Read the Gb ave price
                data[3, i] = float(row[4])   # Read the average consumption
                data[4, i] = 0.7
    return data


def rp(c_data):
    # Countries codes name list
    # names = hh_size[0, :]
    # TODO: names to be okay with rich-poor arrays
    names = ['oth']
    # Rich-poor curve parameters from .csv
    j = 0   # j -- for every name
    # Iterate through all the countries
    for name in names:
        i = 0   # i -- for every point of the curve
        data = []
        with open('./Raw_data/countries/{}.csv'.format(name), 'r') as rp:
            rd_1 = csv.reader(rp)
            # Create empty array of a shape
            rp_data = np.empty((2, len(names)), dtype='object')
            for row in rd_1:
                data_row = []   # Data array
                data_row.append(float(row[0]))   # Filling the key
                data_row.append(float(row[1]))   # Filling the value
                data.append(data_row)
                i += 1
            rp_data[0, j] = name   # Country code
            rp_data[1, j] = data   # Array of curve points data
        j += 1
    return rp_data


def static(pop, countries, c_data, rp_data, price, inter):
    # Generate a data-grid for the market
    # pop - array of population
    # countries - array of countries grid
    # c_data - array of country-related marketing and demographic info
    # rp_data - array of rich-poor curve data grid
    # price - service estimation price
    # inter - percentage of income spent on internet
    cash_data = np.empty((360, 180))

    for i in range(360):
        for j in range(180):
            if pop[i, j] > 0:
                name = countries[i, j]
                # Rich-poor
                # TODO: rich-poor name has to be okay
                # Find the data for rich-poor by the country code
                rp_i = np.where(rp_data == 'oth')
                # Find the data for households bu the country code
                cd_i = np.where(c_data == name)
                # If there's no data for country, take the generic one
                if ~isinstance(cd_i, int):
                    cd_i = np.where(c_data == 'oth')
                # Calculate the average price of the internet
                price = c_data[2, cd_i[1]] * c_data[3, cd_i[1]]
                # Interp it depending on the price given
                rp = 1 - smart_interp(rp_data[1, rp_i[1]][0],
                                      price*12/inter)/100
                # Assign the data to the cell
                cash_data[i, j] = pop[i, j]*rp*price*c_data[4, cd_i[1]]
            else:
                cash_data[i, j] = 0
    return cash_data


def pickles(sim):
    with open('./PP_Data/lon12.data', 'wb') as f:
        pickle.dump(sim.lon, f)
    with open('./PP_Data/lat12.data', 'wb') as f:
        pickle.dump(sim.lat, f)
    with open('./PP_Data/market.data', 'wb') as f:
        pickle.dump(sim.money, f)


def population_grid(sim):
    if sim.lat.shape[0] != 315361:
        lats = np.swapaxes(sim.lat, 0, 1)
        lons = np.swapaxes(sim.lon, 0, 1)
    else:
        lats = sim.lat
        lons = sim.lon

    data = np.stack((lats, lons), axis=2)

    for i in range(data.shape[0]//500):
        with open('./PP_Data/D/{}'.format(i*500), 'wb') as f:
            pickle.dump(data[i*500:(i+1)*500, :, :], f)

    with open('./PP_Data/D/{}'.format((i+1)*500), 'wb') as f:
            pickle.dump(data[(i+1)*500:, :, :], f)


# Generate an array of the population based on the .asc file
pop = pop_array('./Raw_data/pop_100/pop.asc')
# Prepare preliminary data
countries = np.loadtxt('./PP_Data/countries_list.txt',
                       skiprows=1, dtype='object')
# UNCOMMENT IF COUNTRY CODES GRID IS LOST AND NEEDS TO BE GENERATED AGAIN
# countries = gen_countries('../Raw_data/countries.geojson', 1)
c_data = country_data()
rp_data = rp(c_data)
# Generate data
data = static(pop, countries, c_data, rp_data, 100, 0.1)
# Save to the file
np.savetxt('./PP_Data/marketing_vals.txt', data,
           header='xlt = -180, ylt = -90, step = {}'.format(1), fmt='%f')
