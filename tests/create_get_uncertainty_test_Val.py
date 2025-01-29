import time
import random
import numpy as np
import warnings
import pytest

from wmm import wmm_calc

def get_test_val(path= "/Users/coka4389/Library/CloudStorage/OneDrive-UCB-O365/Desktop/testWMM_Numpy/wmm/wmm/WMMHR2025_TEST_VALUE_TABLE_FOR_REPORT.txt"):
    lat = []
    lon = []
    alt = []
    time = []
    test_X = []
    test_dec = []
    test_H = []
    test_ydot = []
    with open(path, 'r') as infile:
        for line in infile:
            values = line.split()
            if(values[0] == '#'):
                continue
            values = values
            lat.append( np.float64(values[2]))
            lon.append( np.float64(values[3]))
            alt.append( np.float64(values[1]))
            time.append( np.float64(values[0]))
            test_X.append( np.float64(values[4]))
            test_H.append( np.float64(values[7]))
            test_dec.append(np.float64(values[10]))
            test_ydot.append( np.float64(values[13]))

    return np.array(lat), np.array(lon), np.array(alt), np.array(time), np.array(test_X), np.array(test_dec), np.array(test_H), np.array(test_ydot)

def main():
    path = 'your path'
    lat, lon, alt, dyear, a,b,c,d = get_test_val() 
    print('do thing')
    model =  wmm_calc()
    model.setup_env(lat,lon,alt)
    model.setup_time()
    uncertainties = model.get_uncertainty()
    #TODO write uncertainties out to a file to send back to me
    

if __name__ == "__main__":
    main()