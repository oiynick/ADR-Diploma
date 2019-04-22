import numpy as np
import random
R = 6378.137


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


class Maths:
    # The Abstrct class bringing all the mathematical functions
    def R1(x):
        # REVERSE MATRIX 1 (X)
        return np.array([[1, 0, 0],
                         [0, np.cos(x), np.sin(x)],
                         [0, -np.sin(x), np.cos(x)]])

    def R2(x):
        # REVERSE MATRIX 2 (Y)
        return np.array([[np.cos(x), 0, -np.sin(x)],
                         [0, 1, 0],
                         [np.sin(x), 0, np.cos(x)]])

    def R3(x):
        # REVERSE MATRIX 3 (Z)
        return np.array([[np.cos(x), np.sin(x), 0],
                         [-np.sin(x), np.cos(x), 0],
                         [0, 0, 1]])

    def jtime(yr, mon, day, h, mint, sec):
        # TRANSFERING USUAL DATE INTO JULIAN
        year = 367.0 * yr
        m1 = 7*(yr + np.floor((mon + 9)/12.0))*0.25
        m2 = np.floor(275 * mon/9.0)
        t = ((sec/60.0 + mint)/60.0 + h)/24.0
        return year - np.floor(m1 + m2 + day + 1721013.5 + t)

    def check_probe(reliability, iterations):
        # CHECK IF THE PROBABILITY WORKED FOR THE EXACT SAT

        # RUN THE MONTE-CARLO TYPE METHOD
        summy = 0
        for index in range(iterations-1):
            summy = summy + random.randint(0, 100)
        average = summy/iterations

        # GIVE THE VERDICT
        if average < reliability:
            return True
        else:
            return False

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
