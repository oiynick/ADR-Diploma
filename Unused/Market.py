import csv
import time
import pickle
import numpy as np
from General import Maths
import geopy


class DataFile:
    def __init__(self, opt):
        if opt == 'market':
            self.folder = 'market'
        elif opt == 'wealth':
            self.folder = 'wealth'
        elif opt == 'countries':
            self.folder = 'countries'

    def __setitem__(self, index, value):
        # SET DATA INTO FILE
        with open('Data/{}/{}.data'.format(self.folder, index), 'wb') as f:
            pickle.dump(value, f)

    def __getitem__(self, index):
        # READ DATA FROM FILE
        with open('Data/{}/{}.data'.format(self.folder, index), 'rb') as f:
            return pickle.load(f)


class Market:

    @staticmethod
    def country_data_prep():
        # Pickle the country data separated by the files with countrycode names
        # TO BE LAUNCHED IF ONLY RAW DATA IS AVAILABLE
        array = []
        country_list = []
        file = DataFile('wealth')
        with open('Raw_data/countries.csv', 'r') as cl:
            reader0 = csv.reader(cl)
            for row in reader0:
                country_list.extend(str(row[0]).lower)
        for code in country_list:
            with open('Raw_data/countries/{}.csv'.format(code), 'r') as s:
                reader = csv.reader(s)
                for row in reader:
                    array.append(row)
            file[code] = array

    def array_prep(scale):
        # Uploading the files of the population
        data = []
        carray = []
        if scale == 1:
            for i in range(5):
                data.append(np.loadtxt('Raw_data/pop_1/{}.asc'.format(i-1),
                                       skiprows=6).tolist())
        elif scale == 100:
            data.append(np.loadtxt('Raw_data/pop_100/0.asc',
                                   skiprows=6).tolist())
        with open('Raw_data/countries.csv', 'r') as countries:
            reader = csv.reader(countries)
            for row in reader:
                carray.append([str(row[0]), float(row[1]), float(row[2])])

        return [data, carray]

    def population(lat, lon, data, kscale, dscale):
        # Recieving the amoun of people living on the exact point of the map
        if lat < -60 or lat > 85:
            return 0
        file_num = (lat+180)//90 if lon > 0 else (lat + 180)//90 + 4
        file = 0 if kscale == 100 else file_num
        cell_v = data[file][int((lat+60)/dscale)][int((lon+180)/dscale)]
        return cell_v if cell_v != -9999 else 0

    def country(lat, lon, countries):
        # connecting the file containing the information about the countries &
        # Get the country and its parameters from longtitude and latitude
        # NAME, FAMILY SIZE, SHARING PROBABILITY
        null = object()
        madeit = False

        while not madeit:
            try:
                locator = geopy.geocoders.Yandex(timeout=10)
                madeit = True
            except:
                print('whoops!')
                time.sleep(60)

        # Yandex search API result structure
        prop = 'metaDataProperty'
        meta = 'GeocoderMetaData'
        par = 'Address'
        location = locator.reverse((lat, lon), exactly_one=True)

        address_raw = getattr(location, 'raw', null)
        if address_raw is null:
            country = 'oth'
        else:
            country = address_raw[prop][meta][par].get('country_code', 'oth')

        for c in countries:
            if c[0] == country:
                return c
        else:
            return ['oth', 3.4, 1]

    def stat(population, lat, lon, countries):
        # Get the Amount of the audience for the country
        # based on a dot value
        # The functions returns the static market volume (no market share or
        # price is taken into account)
        country = Market.country(lat, lon, countries)   # Take the country row

        fam_size = float(country[1])
        sharing = float(country[2])

        volume = population/(fam_size*sharing)

        return [volume, str(country[0])]

    def data_net(dscale=1, kscale=100):
        # TO BE LAUNCHED IF ONLY RAW DATA IS AVAILABLE OR GRID STEP CHANGE
        # Preparing arrays of population and market information
        data, countries = Market.array_prep(kscale)
        MarketFile = DataFile('market')
        CountriesFile = DataFile('countries')

        for lat in range(-60, 89, dscale):
            row_market = []
            row_country = []
            for lon in range(-180, 180, dscale):
                print((lat, lon))
                population = Market.population(lat, lon, data, kscale, dscale)
                if population > 0:
                    stat = Market.stat(population, lat, lon, countries)
                    print(stat[1])
                    row_market.extend([stat[0]])
                    row_country.extend([stat[1]])
                else:
                    row_market.extend([0])
                    row_country.extend(['none'])
                # Printing the status (NOT USED 'TILL LAT LON PAIR IS PRINTED)
                # print(100*(lat+90)/180)
            MarketFile[lat] = row_market
            CountriesFile[lat] = row_country

    def wealth(code, price, ppn=.1):
        # Takes the name of the country and goes to the stats
        # of the wealth distribution
        WealthFile = DataFile('wealth')
        # TODO: change 'oth' to the country name
        array = WealthFile['oth']
        penetration = Maths.Maths.smart_interp(array, price*12/ppn)
        # TODO: create wealth files
        return 1-penetration/100

    def get_data(price, lat, lon, share=.5):
        # Retrieving final amount of market data
        CountryFile = DataFile('countries')
        MarketFile = DataFile('market')
        code = CountryFile[lat][lon]
        if code != 'none':
            penetration = Market.wealth(code, price)
        else:
            penetration = 1
        return MarketFile[lat][lon]*penetration*share
