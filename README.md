

## WMM Python module

![PyPI - Version](https://img.shields.io/pypi/v/wmm-calculator)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/wmm-calculator)
![PyPI - License](https://img.shields.io/pypi/l/wmm-calculator)
![PyPI - Downloads](https://img.shields.io/pypi/dm/wmm-calculator)

This is a Python implementation of the latest World Magnetic Model(WMM) by the Cooperative Institute For Research in Environmental Sciences (CIRES), University of Colorado.
The World Magnetic Model (WMM) is the standard model for navigation, attitude, and heading referencing systems that use the  geomagnetic field. 

A new version of the model is updated every five years to address changes in Earth’s magnetic field. The current version (WMM2025) was released on December 17, 2024, and will remain valid until late 2029. 

**For more information about the WMM model, please visit [WMM](https://www.ncei.noaa.gov/products/world-magnetic-model)**

## Installation

The recommended way to install wmm-calculator is via [pip](https://pip.pypa.io/en/stable/)

```
pip install wmm-calculator 
```


## WMM Python API Quick Start

WARNING: Input arrays of length 3,000,000 require ~ 16GB of memory. However, all input vectors must have the same length. 

Set up the time and latitude and longtitude and altitude for the WMM model

```python
from wmm import wmm_calc
model = wmm_calc()
lat = [23.35, 24.5]
lon = [40, 45]
alt = [21, 21]

year = [2025, 2026]
month = [12, 1]
day = [6, 15]

# set up time
model.setup_time(year, month, day)
# set up the coordinates
model.setup_env(lat, lon, alt)

print(model.get_all())
```

Get all of the geomagnetic elements

```python
mag_map = model.get_all()
```
It will return 

```python
{'x': array([33805.9794844 , 33492.10462007]), 'y': array([2167.06741335, 1899.8602046 ]), 'z': array([23844.95317237, 26150.62563705]), 'h': array([33875.36612457, 33545.94671013]), 'f': array([41426.10555998, 42534.52435243]), 'dec': array([3.6678175, 3.2466589]), 'inc': array([35.14180823, 37.93807267]), 'dx': array([ 9.91215814, 14.60583551]), 'dy': array([-2.63505666, -4.26437959]), 'dz': array([40.35078867, 34.39738965]), 'dh': array([ 9.72328589, 14.34088148]), 'df': array([31.17702034, 32.45814375]), 'ddec': array([-0.00552022, -0.00868461]), 'dinc': array([0.03789554, 0.02466632])}
```

### Get the uncertainty value of geomagnetic elements

```python
model = wmm_calc()
lat = [80.,  0., 80.]
lon = [  0., 120.,   0.]
alt = [0., 0., 0.]
dyear = [2025.,  2025.,  2027.5]

# set up time
model.setup_time(dyear=dyear)
# set up the coordinates
model.setup_env(lat, lon, alt)
print(model.get_uncertainty())

```

```python
{'x_uncertainty': 137, 'y_uncertainty': 89, 'z_uncertainty': 141, 'h_uncertainty': 133, 'f_uncertainty': 138, 'declination_uncertainty': array([3.98575493e-05, 6.55276509e-06, 3.99539341e-05]), 'inclination_uncertainty': 0.2}

```

## WMM Python API Reference

### Description of the components

- **‘dec’ - Declination (deg)** Angle between the horizontal magnetic field vector and true north, positive east, measured in degrees.
- **‘inc’ - Inclination (deg)**: The angle made by the Earth's magnetic field with the horizontal plane, positive down, measured in degrees.
- **‘h’ - H (nT)**: Horizontal intensity of the Earth's magnetic field, measured in nanoteslas (nT).
- **‘x’- X (nT)**: Northward component of the Earth's magnetic field, measured in nanoteslas (nT).
- **‘y’ - Y (nT)**: Eastward component of the Earth's magnetic field, measured in nanoteslas (nT).
- **‘z’ - Z (nT)**: Downward component of the Earth's magnetic field, measured in nanoteslas (nT).
- **F (nT)**: Total intensity of the Earth's magnetic field, measured in nanoteslas (nT).
- **ddec/dt (deg/year)**: Rate of change of declination over time, measured in degrees per year.
- **dinc/dt (deg/year)**: Rate of inclination change over time, measured in degrees per year.
- **dh/dt (nT/year)**: Rate of change of horizontal intensity over time, measured in nanoteslas per year.
- **dx/dt (nT/year)**: Rate of change of the northward component over time, measured in nanoteslas per year.
- **dy/dt (nT/year)**: Rate of change of the eastward component over time, measured in nanoteslas per year.
- **dz/dt (nT/year)**: Rate of change of the downward component over time, measured in nanoteslas per year.
- **df/dt (nT/year)**: Rate of change of the total intensity over time, measured in nanoteslas per year.


### Set up the time and coordinates for the WMM model

#### 1. Set up time 

**setup_time**(self, **year**: Optional[np.ndarray] = None, **month**: Optional[np.ndarray] = None, **day**: Optional[np.ndarray] = None,
                   **dyear**: Optional[np.ndarray] = None):

If users don't call or assign any value to setup_time(), the current time will be used to compute the model.
Either by providing year, month, day or deciaml year. When passing the decimal year, please pass the decimal year as float point or array to `dyear`
```python
from wmm import wmm_calc
model = wmm_calc()
model.setup_time(2024, 12, 30)
```
or 
```python
from wmm import wmm_calc
model = wmm_calc()
model.setup_time(dyear=2025.1)
```

User allow to assign the date from "2024-11-13" to "2030-01-01"

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
```python
from wmm import wmm_calc
model = wmm_calc()
lat, lon, alt = 50.3, 100.4, 0
model.setup_env(lat, lon, alt, unit="m", msl=True)
```

#### 3. Get the geomagnetic elements

**get_all()**

After setting up the time and coordinates for the WMM model, you can get all the geomagnetic elements by

```python
from wmm import wmm_calc
model = wmm_calc()
lat, lon, alt = 50.3, 100.4, 0
year, month, day = 2025, 3, 30
model.setup_env(lat, lon, alt, unit="m", msl=True)
model.setup_time(year, month, day)
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
from wmm import wmm_calc
model = wmm_calc()
lat, lon, alt = 50.3, 100.4, 0
year, month, day = 2025, 3, 30
model.setup_env(lat, lon, alt, unit="m", msl=True)
model.setup_time(year, month, day)
mag_map = model.get_Bh()
```

