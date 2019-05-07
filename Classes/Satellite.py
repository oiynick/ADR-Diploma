import numpy as np
import csv
mu = 398600   # KM^3/S^2 GRAVITATIONAL CONSTANT
R = 6378.137


class Satellite:
    # Satellite class

    def __init__(self, mass, vol, alfa, alt, cov):
        # Satellite parameters
        self.alfa = alfa   # Antenna FOV
        self.m = mass   # MASS OF THE SATELLITE
        self.vol = vol   # The satellite average volume
        self.alt = alt   # The satellite altitude
        self.dens = 0   # Debris density in the orbit
        self.cov = cov   # Coverage percentage for the sat

        # Price parameters
        self.cost = self.sat_cost('./Raw_data/sats/spacex.csv')
        self.launch_cost = self.launch_cost('./Raw_data/sats/spacex.csv')
        self.operational_cost = 20000   # US dollars per month of operation

    def collision(self):
        # Set the sandart distribution of the debris density
        lil = 1.146*10**(-6)*np.exp(-((self.alt - 856.9)/126.7)**2)   # R20.92
        med = 1.34*10**(-7)*np.exp(-((self.alt - 860.8)/153)**2)   # R20.83
        big = 3.016*10**(-8)*np.exp(-((self.alt - 847.1)/171.2)**2)   # R20.72

        density = lil + med + big
        # Collision probability
        # col = 1 - np.exp(-density*self.vol**(1/3)*t*12)
        return density

    def launch_cost(self, path):
        # Calculate launch cost based on SMAD model and specification
        # TODO: dynamic pricing
        with open(path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == 'DM':
                    Bus = 1064 + 35.5*float(row[1])**1.261
                    return 0.061*Bus   # SMAD ref. table 11.11 New SMAD
        raise Exception('BUS mass parameter has not been found')

    def sat_cost(self, path):
        # Calculate overall satellite cost based on SMAD model and specs
        # TODO: Standard deviation
        # DM - Bus dry weight
        # SM - Structure weight
        # TCM - Thermal control weight
        # AM - ADCS dry weight
        # EM - EPS weight
        # TM - TT&C weight
        # CM - CDH weight
        data = {}
        with open(path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                data[row[0]] = float(row[1])

        # Calculate cost specifics
        Bus = 1064 + 35.5*data['DM']**1.261
        Str = 407 + 19.3*data['SM'] + np.log(data['SM'])
        Thr = 335 + 5.7*data['TCM']**2
        ADC = 1850 + 11.7*data['AM']**2
        EPS = 1261 + 539*data['EM']**2
        PRO = 89 + 3*data['DM']**1.261
        TTC = 486 + 55.5*data['TM']**1.35
        CDH = 658 + 75*data['CM']**1.35

        Pay = 0.4*Bus
        IAT = 0.139*Bus
        Prg = 0.229*Bus
        Grn = 0.066*Bus

        return 0.2*(Bus + Str + Thr + ADC +
                    EPS + PRO + TTC + CDH) + (Pay + IAT + Prg + Grn)
