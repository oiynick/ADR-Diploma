import numpy as np
import csv
from General.Maths import Maths


class Satellite:
    # Class of the exact type of the satellite
    state = True   # STATES OF THE SATELLITE
    turn_t = 0
    mu = 398600   # KM^3/S^2 GRAVITATIONAL CONSTANT
    R = 6378.137   # KM RADIUS OF THE EARTH

    def __init__(self, u, alt, alfa, lt, ecc, Om,
                 inc, mass, vol, lams, ks, name):
        # Satellite parameters
        self.lt = lt   # LIFETIME OF THE SATELLITE IN YEARS
        self.u = u   # TRUE LONGTITUDE
        self.alfa = alfa   # Antenna FOV
        self.c_rate = (alt*np.tan(Maths.d2r(alfa)))**2*np.pi/5100000   # COVERAGE PERC % OF EARTH SURFACE BY 1 SAT
        self.m = mass   # MASS OF THE SATELLITE
        self.vol = vol

        # Orbit parameters
        self.ecc = ecc   # Eccentricity of the orbit
        self.Om = Om   # RAAN - def
        self.inc = inc   # INCLINATION - predefined
        self.alt = alt   # ALTITUDE - predefined

        # Price parameters
        self.details = Details(name)
        self.cost = self.details.cost
        self.launch_cost = self.details.launch_cost
        self.operational_cost = self.details.operational_cost

        # Orbit density and reliability
        self.density = Satellite.get_density(alt)
        self.rel = np.array([])

        for l, k in zip(lams, ks):
            r = lambda t: k/l*(t/l)**(k-1)*np.exp(-(t/l**k))
            self.rel.extend([r])

        self.col = lambda t: 1 - np.exp(-self.density*self.vol**(1/3)*t*12)   # Collision probability

    def get_cortez(self, om):
        # RETRIEVE THE CORTEZIAN COORDINATES AND VELOCITY OF THE EXACT SAT

        p = self.alt * (1 - self.ecc ** 2)  # GEOMETRIC PARAMETER OF THE ORBIT
        u = self.u
        Om = self.Om
        inc = self.inc
        ecc = self.ecc

        Rpqw = np.array([[p * np.cos(u) / (1 + ecc * np.cos(u))],
                         [p * np.sin(u) / (1 + ecc * np.cos(u))],
                         [0]])

        Vpqw = np.array([[(398600.4418 / p) ** .5 * np.sin(u)],
                         [(398600.4418 / p) ** .5 * (ecc + np.cos(u))],
                         [0]])
        R = Maths.R3(-Om) @ Maths.R1(-inc) @ Maths.R3(om) @ Rpqw
        V = Maths.R3(-Om) @ Maths.R1(-inc) @ Maths.R3(om) @ Vpqw

        return {'x': R[0, 0],
                'y': R[1, 0],
                'z': R[2, 0],
                'vx': V[0, 0],
                'vy': V[1, 0],
                'vz': V[2, 0]}

    def get_density(altitude):
        # Set the sandart distribution of the debris density
        lil = 1.146*10**(-6)*np.exp(-((altitude - 856.9)/126.7)**2)   # R2092
        med = 1.34*10**(-7)*np.exp(-((altitude - 860.8)/153)**2)   # R2083
        big = 3.016*10**(-8)*np.exp(-((altitude - 847.1)/171.2)**2)   # R2072

        return lil + med + big

    def get_reliability(self, time):
        # Retrieve final reliability
        reliability = 0

        for rel in self.rel:
            reliability = reliability + rel(time)

        return reliability + self.col(time)

    def coverage(self, Om, u):
        # Return the array of dots for the coverage area
        lat = np.asin(np.sin(self.u)*np.sin(self.inc))

        # Calculate elements to calculate longtitude
        one = np.cos(self.u)*np.cos(self.Om)
        two = np.sin(self.u)*np.sin(self.Om)*np.cos(self.inc)
        three = np.cos(self.u)*np.sin(self.Om)
        four = np.sin(self.u)*np.cos(self.Om)*np.cos(self.inc)

        # Calculate latitude
        lon = np.atan((one-two)/(three+four))
        # calculate the
        r = (self.alt - self.R)*np.tg(self.alfa)
        result = []
        for i in range(180):
            for j in range(90):
                if self.R*np.acos(np.sin(lon)*np.sin(i) +
                               np.cos(lon)*np.cos(i)*np.cos(lat-j)) <= r:
                    result.extend([(i, j)])
        return result


class Details:
    # Detailed information about the satellite
    # DM - Bus dry weight
    # SM - Structure weight
    # TCM - Thermal control weight
    # AM - ADCS dry weight
    # EM - EPS weight
    # TM - TT&C weight
    # CM - CDH weight
    def __init__(self, name):
        self.data = {}
        with open('Raw_data/sats/{}.csv'.format(name), 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                self.data[row[0]] = float(row[1])
# TODO: check the SMAD reference
                # TODO: cost model class
                # TODO: Standard Error
                # SMAD table reef 11.11 (new SMAD)
        Bus = 1064 + 35.5*self.data['DM']**1.261
        Str = 407 + 19.3*self.data['SM'] + np.log(self.data['SM'])
        Thr = 335 + 5.7*self.data['TCM']**2
        ADC = 1850 + 11.7*self.data['AM']**2
        EPS = 1261 + 539*self.data['EM']**2
        PRO = 89 + 3*self.data['DM']**1.261
        TTC = 486 + 55.5*self.data['TM']**1.35
        CDH = 658 + 75*self.data['CM']**1.35

        Pay = 0.4*Bus
        IAT = 0.139*Bus
        Prg = 0.229*Bus
        Grn = 0.066*Bus

        self.cost = 0.2*(Bus + Str + Thr + ADC +
                         EPS + PRO + TTC + CDH) + (Pay + IAT + Prg + Grn)
        self.launch_cost = 0.061*Bus
        self.operational_cost = 20000   # Cost per month
