## Create the environment for developing wmm Python module


## WMM Python API Quick Start

Set up the time and latitude and longtitude and altitude for WMM model

```python
from wmm import wmm_calc

model = wmm_calc()
lat, lon, alt = 23.35, 40, 21.0

model.setup_time(2024, 9, 20)

model.setup_env(lat, lon, alt)
```

Get all of magnetic elements

```python
mag_map = model.get_all()
```
It will return 

```python
{'x': 33794.99979072497, 'y': 2259.9561008893347, 'z': 23918.715487668323, 
 'h': 33870.47995575274, 'f': 41464.61579483249, 'dec': 3.8258158337337047, 'inc': 35.22904145081409, 
 'dx': 9.626049027096451, 'dy': 24.214119374622555, 'dz': 76.85040189603315, 
 'dh': 11.220247606796214, 'df': 53.496168412711995, 
 'ddec': 2.386990047280268, 'dinc': 4.667974602946641}
```

## WMM Python API Reference

### Set up the environment for WMM model

#### Set up time 

**setup_time(year**=None, **month**=None, **day**=None, **dyear** = None)

If users don't call or assign any value to setup_time(), it will use the current time to compute the model.
Either by providing year, month, day
```python
from wmm import wmm_calc
model = wmm_calc()
model.setup_time(2024, 12, 30)
```
or 
```python
model = wmm_calc()
model.setup_time(dyear=2024.9)
```

User allow to assign the date from "2019-11-17" to "2025-01-01"

#### Set up the coordinates

**setup_env(lat**, **lon**, **alt**, **unit**="km", **msl**=True)
```python
from wmm import wmm_calc
model = wmm_calc()
lat, lon, alt = 50.3, 100.4, 0
model.setup_env(lat, lon, alt, unit="m")
```

The default unit and type of altitude is km and mean sea level. 
Assign the parameter for unit and msl, if the latitude is not in km or ellipsoid height.
"m" for meter and "feet" for feet. For example,
```
model.setup_env(lat, lon, alt, unit="m", msl=False)
```

#### Get the magnetic elements

After setting up the time and coordinates for WMM model, you can get the all magnetic elements by

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

