## Create the environment for developing WMMHR Python module

This is a Python implementation of the latest World Magnetic Model(WMM) by the Cooperative Institute For Research in Environmental Sciences (CIRES), University of Colorado. The software computes all the geomagnetic field components from the WMM model for a specific date and location. 
For more information about the WMM model, please visit [WMM](https://www.ncei.noaa.gov/products/world-magnetic-model)


## WMM Python API Quick Start

Set up the time and latitude and longtitude and altitude for the WMM model

```python
from wmm import wmm_calc
model = wmm_calc()
lat = np.array([23.35, 24.5])
lon = np.array([40, 45])
alt = np.ones(len(lat))*21

year = np.array([2025, 2026]).astype(int)
month = np.array([12, 1]).astype(int)
day = np.array([6, 15]).astype(int)

model.setup_time(year, month, day)

model.setup_env(lat, lon, alt)

print(model.get_all())
```

Get all of the geomagnetic elements

```python
mag_map = model.get_all()
```
It will return 

```python

{'x': array([-17603.28858822, -15601.9029994 ]), 'y': array([3376.51054331, 3514.84345219]), 'z': array([57927.51624799, 59035.4644569 ]), 'h': array([17924.190151  , 15992.92036172]), 'f': array([60637.23057026, 61163.38418808]), 'dec': array([169.1418996 , 167.30418427]), 'inc': array([72.80665382, 74.8421807 ]), 'dx': array([295.42592776, 316.74492718]), 'dy': array([-9.42710882, -8.374395  ]), 'dz': array([-25.54450249, -27.87657315]), 'dh': array([-291.91269179, -310.841185  ]), 'df': array([-110.69153579, -108.18506608]), 'ddec': array([ -8.89792466, -13.20742715]), 'dinc': array([15.38195593, 16.45360138])}
```

### Get the uncertainty value of geomagnetic elements

```python
from wmm import wmm_calc

model = wmm_calc()

# set up time
dyear_in = np.array([2025.1, 2026.9])
model.setup_time(dyear=dyear_in)
# set up the coordinates
model.setup_env(lat, lon, alt)
# get the uncertainty value
print(model.get_uncertainty())
```

```python
{'x_uncertainty': 137, 'y_uncertainty': 89, 'z_uncertainty': 141, 'h_uncertainty': 133, 'f_uncertainty': 138, 'declination_uncertainty': array([1.43123270e-05, 1.65339971e-05]), 'inclination_uncertainty': 0.2}
```

## WMM Python API Reference

### Description of the components

- **‘Dec’ - Declination (deg)** Angle between the horizontal magnetic field vector and true north, positive east, measured in degrees.
- **‘Inc’ - Inclination (deg)**: The angle made by the Earth's magnetic field with the horizontal plane, positive down, measured in degrees.
- **‘h’ - H (nT)**: Horizontal intensity of the Earth's magnetic field, measured in nanoteslas (nT).
- **‘x’- X (nT)**: Northward component of the Earth's magnetic field, measured in nanoteslas (nT).
- **‘y’ - Y (nT)**: Eastward component of the Earth's magnetic field, measured in nanoteslas (nT).
- **‘z’ - Z (nT)**: Downward component of the Earth's magnetic field, measured in nanoteslas (nT).
- **F (nT)**: Total intensity of the Earth's magnetic field, measured in nanoteslas (nT).
- **dD/dt (deg/year)**: Rate of change of declination over time, measured in degrees per year.
- **dI/dt (deg/year)**: Rate of inclination change over time, measured in degrees per year.
- **dH/dt (nT/year)**: Rate of change of horizontal intensity over time, measured in nanoteslas per year.
- **dX/dt (nT/year)**: Rate of change of the northward component over time, measured in nanoteslas per year.
- **dY/dt (nT/year)**: Rate of change of the eastward component over time, measured in nanoteslas per year.
- **dZ/dt (nT/year)**: Rate of change of the downward component over time, measured in nanoteslas per year.
- **dF/dt (nT/year)**: Rate of change of the total intensity over time, measured in nanoteslas per year.


### Set up the time and coordinates for the WMM model

#### 1. Set up time 

**setup_time**(self, **year**: Optional[np.ndarray] = None, **month**: Optional[np.ndarray] = None, **day**: Optional[np.ndarray] = None,
                   **dyear**: Optional[np.ndarray] = None):

If users don't call or assign any value to setup_time(), the current time will be used to compute the model.
Either by providing year, month, day or deciaml year.
```python
from wmm import wmm_calc
model = wmm_calc()
model.setup_time(2024, 12, 30)
```
or 
```python
model = wmm_calc()
model.setup_time(dyear=2025.1)
```

User allow to assign the date from "2024-12-17" to "2030-01-01"

#### 2. Set up the coordinates

**setup_env**(self, **lat**: np.ndarray, **lon**: np.ndarray, **alt**: np.ndarray, **unit**: str = "km", **msl**: bool = False)
```python
from wmm import wmm_calc
model = wmm_calc()
lat, lon, alt = 50.3, 100.4, 0
model.setup_env(lat, lon, alt, unit="m")
```

The default unit and type of altitude is km and default in GPS(ellipsoid height). 
Assign the parameter for unit and msl, if the latitude is not in km or in mean sea level.
"m" for meter and "feet" for feet. For example,
```
model.setup_env(lat, lon, alt, unit="m", msl=True)
```

#### 3. Get the geomagnetic elements

After setting up the time and coordinates for the WMM model, you can get all the geomagnetic elements by

```
mag_map = model.get_all()
```

which will return all magnetic elements in dict type.

or get single magnetic elements by calling

- `get_Bx()`
- `get_By()`
- `get_Bz()`
- `get_Bh()`
- `get_Bf()`
- `get_Bdec()`
- `get_Binc()`
- `get_dBx()`
- `get_dBy()`
- `get_dBz()`
- `get_dBh()`
- `get_dBf()`
- `get_dBdec()`
- `get_dBinc()`

for example,
```python
Bh = model.get_Bh()
```

