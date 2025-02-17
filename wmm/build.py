import os
import warnings
import math
import datetime as dt
from typing import Optional, Tuple, Union
import numpy as np

from geomaglib import util, legendre, magmath, sh_vars, sh_loader
from wmm import load
from wmm import uncertainty

def convert_to_ndarray(num: Union[int, float, list, np.ndarray]):
    if np.isscalar(num):
        return np.array([num])
    elif isinstance(num, list):
        return np.array(num)
    elif isinstance(num, np.ndarray):
        return num
    else:
        
        raise ValueError(f"Input data is not a supported type: {type(num), num}")
def fill_timeslot(year: Optional[int], month: Optional[int], day: Optional[int]) -> Tuple:
    """
    Fill out the missing year, month or day with the current time.

    Inputs:
    :param year: int or None type
    :param month: int or None type
    :param day: int or None type

    Outputs:
    :return: year, month, day
    """
    curr_time = dt.datetime.now()

    if year is None:
        year = curr_time.year
    if month is None:
        month = curr_time.month
    if day is None:
        day = curr_time.day

    return year, month, day


class wmm_elements(magmath.GeomagElements):

    def __init__(self, Bx: np.ndarray, By: np.ndarray, Bz: np.ndarray, dBx: Optional[np.ndarray] = None, dBy: Optional[np.ndarray] = None,
                 dBz: Optional[np.ndarray] = None):
        """

        The class is used to compute the magnetic elements for
        Bx, By, Bz, Bh, Bf, Bdec, Binc
        dBx, dBy, dBz, dBh, dBf, dBdec, dBinc


        :param Bx: Magnetic elements Bx in geodetic degree
        :param By: Magnetic elements By in geodetic degree
        :param Bz: Magnetic elements Bz in geodetic degree
        :param dBx: allow None or Magnetic elements dBx in geodetic degree
        :param dBy: allow None or Magnetic elements dBy in geodetic degree
        :param dBz: allow None or Magnetic elements dBz in geodetic degree
        """
        super().__init__(Bx, By, Bz, dBx, dBy, dBz)


    def get_dBdec(self) -> float:
        """
        Get magnetic elemnts delta declination(dBdec). The dBdec need to be multiplied with 60 for argmin.
        :return: delta declination
        """
        ddec = super().get_dBdec()
        ddec = ddec * 60.0

        if (ddec > 180): ddec-=360

        if (ddec <= -180): ddec += 360

        return ddec

    def get_dBinc(self) -> float:
        """
            Get magnetic elemnts delta inclination(dBdec). The dBinc need to be multiplied with 60 for argmin.
            :return: delta inclination
        """
        ddec = super().get_dBinc()

        return ddec * 60.0

    def get_all(self) -> dict[str, float]:
        """
            Get all of magnetic elemnts for
             Bx, By, Bz, Bh, Bf, Bdec, Binc
            dBx, dBy, dBz, dBh, dBf, dBdec, dBinc

            :return: delta inclination
        """
        mag_map = super().get_all()

        mag_map["ddec"] = mag_map["ddec"] * 60.0
        mag_map["dinc"] = mag_map["dinc"] * 60.0

        return mag_map

    def get_uncertainity(self, err_vals):

        h = self.get_Bh()

        decl_variable = err_vals["D_OFFSET"] / h
        decl_constant = int(err_vals["D_OFFSET"])
        uncert_decl = np.sqrt(decl_constant*decl_constant + decl_variable*decl_variable)

        uncert_decl = np.where(uncert_decl > 180, 180, uncert_decl)


        uncerMap = {}
        uncerMap["x_uncertainty"] = err_vals["X"]
        uncerMap["y_uncertainty"] = err_vals["Y"]
        uncerMap["z_uncertainty"] = err_vals["Z"]
        uncerMap["h_uncertainty"] = err_vals["H"]
        uncerMap["f_uncertainty"] = err_vals["F"]
        uncerMap["declination_uncertainty"] = uncert_decl
        uncerMap["inclination_uncertainty"] = err_vals["I"]

        return uncerMap

class wmm_calc():

    def __init__(self):
        """
        The WMM model class for computing magnetic elements
        """

        self.nmax = 12
        self.max_year = 2030.0
        self.max_sv = 12
        self.coef_file = "WMM.COF"
        self.err_vals = uncertainty.err_model
        self.min_date = ""
        self.dyear = None
        self.coef_dict = {}
        self.timly_coef_dict = {}
        self.lat = None
        self.lon = None
        self.alt = None
        self.r = None
        self.theta = None
        self.sph_dict = {}
        self.Leg = []

    def get_coefs_path(self, filename: str) -> str:
        """
        Get the path of coefficient file
        :param filename: Provide the file name of coefficient file. The coefficient file should saved in wmm/wmm/coefs
        :return: The path to the coefficient file
        """

        currdir = os.path.dirname(__file__)

        coef_file = os.path.join(currdir, "coefs", filename)
        
        return coef_file

    def load_coeffs(self) -> dict:
        """
        load the WMM model coefficients and meta data like max degree, minimal and maximum date
        :return: the dict type of object including g, h, g_sv and h_sv coefficients and max degree, minimal and maximum date
        """

        wmm_coeffs = self.get_coefs_path(self.coef_file)

        return load.load_wmm_coef(wmm_coeffs, skip_two_columns=True)


    def to_km(self, alt: np.ndarray, unit: str) -> float:
        """
        Transform the meter or feet to km
        :param alt: the altitude in meter or feet or km
        :param unit: "m" for meter and "feet" or feet, "km" for kilometer

        :return: the altitude absed on km
        """

        if unit == "km":
            return alt

        elif unit == "m":
            return alt * 1000
        elif unit == "feet":
            return alt * 0.0003048
        else:
            raise ValueError ("Get unknown unit. Please provide km, m or feet.")

        

    def setup_env(self, lat: Union[int, float, list, np.ndarray], lon: Union[int, float, list, np.ndarray], alt: Union[int, float, list, np.ndarray], unit: str = "km", msl: bool = False):
        """
        The function will initialize the radius, geocentric latitude in degree,
        spherical harmonic terms, maximum degree and legendre function for users.If user is not
        provide time before calling the function, it will use current time by default.


        :param lat: latitude in degree
        :param lon: longtitude in degree
        :param alt: altitude in km, meter or feet
        :param unit: default is kilometer. assign "m" for meter or "feet" if your altitude is not based on km.
        :param msl: default is True. set it to False if the altitude is ellipsoid height.

        """
        lat = convert_to_ndarray(lat)
        lon = convert_to_ndarray(lon)
        alt = convert_to_ndarray(alt)
        
        need_broadcasting = False
        
        if(not(self.dyear is None)):
            
            lat_size,lon_size, alt_size, dyear_size= np.size(lat),np.size(lon),np.size(alt), np.size(self.dyear)
            sizes = np.array([lat_size,lon_size, alt_size, dyear_size])
        
            if(len(np.unique(sizes))>2 ):
                raise ValueError(f"The input time and space vectors have different sizes of time size: {dyear_size}, position sizes: {lat_size,lon_size, alt_size}, input scalars, or vectors of matching length")
            if(len(np.unique(sizes)) == 2 and np.min(sizes) != 1):
                
                raise ValueError(f"The input time and space vectors have different sizes of time size: {dyear_size}, position sizes: {lat_size,lon_size, alt_size}, input scalars, or vectors of matching length")
            if(np.any(dyear_size != np.array([lat_size,lon_size, alt_size]))):
                need_broadcasting = True
        else:
            
            lat_size,lon_size, alt_size = np.size(lat),np.size(lon),np.size(alt)
            sizes = np.array([lat_size,lon_size, alt_size])
            
            if(len(np.unique(sizes))>2):
                raise ValueError (f'The input position (lat,lon,alt) have different shapes{sizes}. Input positions must have the same shape or 1 (i.e. valid combinations for input lengths are (10,10,10) or (10,10,1))')
            if(len(np.unique(sizes)) == 2 and np.min(sizes) != 1):
            
                raise ValueError (f'The input position (lat,lon,alt) have different shapes{sizes}. Input positions must have the same shape or 1 (i.e. valid combinations for input lengths are (10,10,10) or (10,10,1))')
        #if any of lat,lon, and alt have different shapes
        if(lat_size != lon_size or lat_size != alt_size or alt_size != lon_size or need_broadcasting):
                
                #If all values are either max size, or broadcast to match the shape\n of vector inputs')
                broadcast_template = np.ones(np.max(sizes))
                if(lat_size == 1):
                #Broadcast scalar variable to vector length
                    lat = broadcast_template*lat[0] 
                if(lon_size == 1):
                #Broadcast scalar variable to vector length
                    lon = broadcast_template*lon[0] 
                if(alt_size == 1):
                #Broadcast scalar variable to vector length
                    alt = broadcast_template*alt[0] 
            #Check if time exists and potentially broadcast it
        """beginning to set up case 2 w time/space"""
        # if(self.dyear is not None):
        #     all_position_are_scalar = np.max(sizes) == 1
        #     time_is_scalar = len(self.dyear) == 1
        #     #If position is scalar and time is scalar
        #     if(all_position_are_scalar and time_is_scalar):
        #         #No variables need to be broadcast
        #         pass
        #     #If position is scalar and time is vector
        #     if(all_position_are_scalar and not time_is_scalar):
        #         #Broadcast position to the length of time
        #         #This case could be unnecessary. AKA Numpy could do this under the hood


        #     #If position is vector and time is scalar

        #     #If position is vector and time is vector
        #     if(not all_position_are_scalar and not time_is_scalar):
        #         #Only ok if vectors have same length
        #         if(np.max(sizes) == len(self.dyear)):
        #             #broadcast any leftover scalars
        # else:
        """Finishign weird time stuff"""
        alt = self.to_km(alt, unit)
        if msl:
            self.alt = util.alt_to_ellipsoid_height(alt, lat, lon)

        self.check_coords(lat, lon, alt)
        #If self values don't match the size of setup_env values
        #is not None protects from first iteration where self.lat/lon/alt are empty
        if self.lat is not None and self.lon is not None and self.alt is not None:
            if (lat.size != self.lat.size or lon.size != self.lon.size or alt.size != self.alt.size):
                
                self.r, self.theta = util.geod_to_geoc_lat(lat, alt)
                self.r = np.array(self.r)
                self.theta = np.array(self.theta)
                self.alt = alt
                self.lon = lon
                self.lat = lat
                self.sph_dict = sh_vars.comp_sh_vars(lon, self.r, self.theta, self.nmax)
        #Set r and theta values
        if (np.any(lat != self.lat) or np.any(lon != self.lon) or np.any(alt != self.alt)):

            self.r, self.theta = util.geod_to_geoc_lat(lat, alt)
            self.r = np.array(self.r)
            self.theta = np.array(self.theta)
            self.sph_dict = sh_vars.comp_sh_vars(lon, self.r, self.theta, self.nmax)

        self.lat = np.array(lat)
        self.lon = np.array(lon)
        self.alt = np.array(alt)
        cotheta = 90.0 - self.theta



        self.Leg = legendre.Flattened_Chaos_Legendre1(self.nmax, cotheta)

    def setup_time(self, year: Union[int, float, list, np.ndarray] = None, month: Union[int, float, list, np.ndarray] = None, day: Union[int, float, list, np.ndarray] = None,
                   dyear: Union[int, float, list, np.ndarray] = None):
        """
        It will load the coefficients and adjust g and h with the decimal year. The maximum and minimum year of the model
        will also be initialized at here.
        :param year: None or int type
        :param month: None or int type
        :param day: None or int type
        :param decyear: None or int type

        """
        #convert true scalars to numpy arrays


        if(dyear is not None): 
            dyear = convert_to_ndarray(dyear)

        elif (year is not None) and (month is not None) and (day is not None):
            year = convert_to_ndarray(year)
            month = convert_to_ndarray(month)
            day = convert_to_ndarray(day)

        if dyear is None:
        #If no time has been input
            if year is None or month is None or day is None:
                year, month, day = fill_timeslot(year, month, day)
                year = np.array([year])
                month = np.array([month])
                day = np.array([day])
            #Make year, month, day the same length if they aren't
            year_size, month_size, day_size = np.size(year), np.size(month), np.size(day)
            sizes = np.array([year_size, month_size, day_size])
            #Inputs may only be scalar or vector of consistent size
            if(len(np.unique(sizes))>2):
                raise ValueError (f'The input position (year,month,day) have different shapes{sizes}. Input dates must have the same shape or 1 (i.e. valid combinations for input lengths are (10,10,10) or (10,10,1))')
            #If position has already been set:
            if(year_size != month_size or year_size != day_size or day_size != month_size):
                
                #If all values are either max size, or broadcast to match the shape\n of vector inputs')
                broadcast_template = np.ones(np.max(sizes), dtype = int)
                if(year_size == 1):
                #Broadcast scalar variable to vector length
                    year = broadcast_template*year[0] 
                if(month_size == 1):
                #Broadcast scalar variable to vector length
                    month = broadcast_template*month[0] 
                if(day_size == 1):
                #Broadcast scalar variable to vector length
                    day = broadcast_template*day[0] 
            curr_dyear = util.calc_dec_year_array(year, month, day)
            
        else:
            curr_dyear = dyear
        sizes = np.size(dyear)
        if(sizes > 1):#if dyear is vector
            is_none_type = self.lat is None
            
            if(not is_none_type):
                lat_size,lon_size, alt_size= np.size(self.lat),np.size(self.lon),np.size(self.alt)
                pos_sizes = np.array([lat_size,lon_size, alt_size])
                
                #Check if position is vector:
                if(len(np.unique(pos_sizes)) > 1 or (np.max(pos_sizes)!= sizes and np.max(pos_sizes) != 1)):
                    #If it is a vector 
                    #If vectors have different lengths
                    if(np.max(pos_sizes) != np.max(sizes)):
                        raise ValueError(f"The input time and space vectors have different sizes of time size: {np.max(sizes)}, position size: {np.max(pos_sizes)}, input scalars, or vectors of matching length")
                else:#position is scalar
                    #broadcast position
                    
                    broadcast_template = np.ones(np.max(sizes))
                    self.lat = broadcast_template*self.lat
                    self.lon = broadcast_template*self.lon
                    self.alt = broadcast_template*self.alt
                    
                    self.setup_env(self.lat, self.lon, self.alt)
                    lat_size,lon_size, alt_size= np.size(self.lat),np.size(self.lon),np.size(self.alt)
                    pos_sizes = np.array([lat_size,lon_size, alt_size])
                    self.r, self.theta = util.geod_to_geoc_lat(self.lat,self.alt)
                    self.r = np.array(self.r)
                    self.theta = np.array(self.theta)
                    self.sph_dict = sh_vars.comp_sh_vars(self.lon, self.r, self.theta, self.nmax)
                    
        if not self.coef_dict:
            self.coef_dict = self.load_coeffs()
        elif self.coef_dict == {}:
            self.coef_dict = self.load_coeffs()
        
        self.max_year = self.coef_dict["epoch"] + 5.0
        self.min_date = self.coef_dict["min_date"]


        if np.any(curr_dyear < self.coef_dict["min_year"]) or np.any(curr_dyear >= self.max_year):
            max_year = round(self.max_year, 1)
            raise ValueError(f"Invalid year. Please provide date from {self.min_date} to [{int(max_year)}]-[01]-[01] 00:00")

        if np.any(curr_dyear != self.dyear):
            self.dyear = curr_dyear
            self.timly_coef_dict = load.timely_modify_magnetic_model(self.coef_dict, self.dyear, self.max_sv)

    def check_coords(self, lat: np.ndarray, lon: np.ndarray, alt: np.ndarray):
        """
        Validify the coordinate provide from user
        :param lat: latitude in degree
        :param lon: longtitude in degree
        :param alt: altitude in degree
        :return:
        """

        if np.any(lat > 90.0) or np.any(lat < -90.0):
            raise ValueError("latitude should between -90 to 90")

        if np.any(lon > 360.0) or np.any(lon < -180.0):
            raise ValueError("lontitude should between -180 to 360")

        if np.any(alt < -1) or np.any(alt > 1900):
            link = "\033[94mhttps://www.ncei.noaa.gov/products/world-magnetic-model/accuracy-limitations-error-model\033[0m"  # Blue color
            warnings.warn(f"Warning: WMM will not meet MilSpec at this altitude. For more information see {link}")

    def check_blackout_zone(self, Bx: np.ndarray, By: np.ndarray, Bz: np.ndarray):
        """
        Return warning if the location is in balckout zone
        :param Bx: magnetic elements Bx
        :param By: magnetic elements By
        :param Bz: magnetic elements Bz

        """

        wmm_calc = wmm_elements(Bx, By, Bz)
        h = wmm_calc.get_Bh()
        if np.any(h <= 2000.0):
            problem_index = np.where(h <= 2000.0)
            warnings.warn(
                f"Warning: (lat, lon, alt(Ellipsoid Height in km)) = ({self.lat[problem_index]}, {self.lon[problem_index]}, {self.alt[problem_index]}) is in the blackout zone around the magnetic pole as defined by the WMM military specification"
                " (https://www.ngdc.noaa.gov/geomag/WMM/data/MIL-PRF-89500B.pdf). Compass accuracy is highly degraded in this region.\n")
        elif np.any(h <= 6000.0):
            problem_index = np.where(h <= 6000.0)
            warnings.warn(
                
                f"Caution: (lat, lon, alt(Ellipsoid Height in km)) = ({self.lat[problem_index]}, {self.lon[problem_index]}, {self.alt[problem_index]}) is approaching the blackout zone around the magnetic pole as defined by the WMM military specification "
                "(https://www.ngdc.noaa.gov/geomag/WMM/data/MIL-PRF-89500B.pdf). Compass accuracy may be degraded in this region.\n")

    def forward_base(self) -> Tuple:
        """
        Compute the magnetic elements Bx, By and Bz in geodetic degree. If users didn't assinn the time by setup_time(), it will
        use the current time as default.
        :return: magnetic elements Bx, By and Bz in geodetic degree
        """

        if self.lat is None or self.lon is None or self.alt is None:
            raise TypeError("Coordinates haven't set up yet. Please use setup_env() to set up coordinates first.")
        
        
        # if self.timly_coef_dict == {}:
        if not self.timly_coef_dict:
            self.setup_time()
        Bt, Bp, Br = magmath.mag_SPH_summation(self.nmax, self.sph_dict, self.timly_coef_dict["g"],
                                               self.timly_coef_dict["h"], self.Leg, self.theta)
        Bx, By, Bz = magmath.rotate_magvec(Bt, Bp, Br, self.theta, self.lat)

        self.check_blackout_zone(Bx, By, Bz)

        return Bx, By, Bz

    def forward_sv(self) -> Tuple:

        """
        Compute the magnetic elements dBx, dBy and dBz in geodetic degree. If users didn't assign the time by setup_time(), it will
        use the current time as default.
        :return: magnetic elements dBx, dBy and dBz in geodetic degree
        """
        if self.lat is None or self.lon is None or self.alt is None:
            raise TypeError("Coordinates haven't set up yet. Please use setup_env() to set up coordinates first.")
        if self.timly_coef_dict == {}:
            
            self.setup_time()

        dBt, dBp, dBr = magmath.mag_SPH_summation(self.nmax, self.sph_dict, self.timly_coef_dict["g_sv"],
                                                  self.timly_coef_dict["h_sv"], self.Leg, self.theta)

        dBx, dBy, dBz = magmath.rotate_magvec(dBt, dBp, dBr, self.theta, self.lat)
        

        return dBx, dBy, dBz

    def get_Bx(self) -> float:
        """
        Get the Bx magnetic elements
        :return: Bx
        """

        Bx, By, Bz = self.forward_base()

        return Bx

    def get_By(self) -> float:
        """
        Get the By magnetic elements
        :return: By
        """

        Bx, By, Bz = self.forward_base()

        return By

    def get_Bz(self) -> float:
        """
        Get the Bz magnetic elements
        :return: Bz
        """

        Bx, By, Bz = self.forward_base()

        return Bz

    def get_Bh(self) -> float:
        """
        Get the horizontal magnetic elements
        :return: horizontal magnetic elements in float type
        """

        Bx, By, Bz = self.forward_base()

        mag_vec = wmm_elements(Bx, By, Bz)

        return mag_vec.get_Bh()

    def get_Bf(self) -> float:
        """
        Get the total intensity magnetic elements
        :return: total intensity in float type
        """

        Bx, By, Bz = self.forward_base()
        mag_vec = wmm_elements(Bx, By, Bz)

        return mag_vec.get_Bf()

    def get_Bdec(self) -> float:
        """
        Get the declination magnetic elements
        :return: declination in float type
        """

        Bx, By, Bz = self.forward_base()

        mag_vec = wmm_elements(Bx, By, Bz)

        return mag_vec.get_Bdec()

    def get_Binc(self) -> float:
        """
        Get the inclination magnetic elements
        :return: By
        """

        Bx, By, Bz = self.forward_base()

        mag_vec = wmm_elements(Bx, By, Bz)

        return mag_vec.get_Binc()

    def get_dBx(self) -> float:
        """
        Get the Bx magnetic elements
        :return: Bx
        """


        dBx, dBy, dBz = self.forward_sv()

        return dBx

    def get_dBy(self) -> float:
        """
        Get the By magnetic elements
        :return: By
        """

        dBx, dBy, dBz = self.forward_sv()

        return dBy

    def get_dBz(self) -> float:
        """
        Get the Bz magnetic elements
        :return: Bz
        """

        dBx, dBy, dBz = self.forward_sv()

        return dBz

    def get_dBh(self) -> float:
        """
        Get the delta horizontal magnetic elements
        :return: delta horizontal in float type
        """

        Bx, By, Bz = self.forward_base()
        dBx, dBy, dBz = self.forward_sv()

        mag_vec = wmm_elements(Bx, By, Bz, dBx, dBy, dBz)

        return mag_vec.get_dBh()

    def get_dBf(self) -> float:
        """
        Get the delta total intensity magnetic elements
        :return: delta total intensity in float type
        """

        Bx, By, Bz = self.forward_base()
        dBx, dBy, dBz = self.forward_sv()

        mag_vec = wmm_elements(Bx, By, Bz, dBx, dBy, dBz)

        return mag_vec.get_dBf()

    def get_dBdec(self) -> float:
        """
        Get the delta declination magnetic elements
        :return: delta declination in float type
        """

        Bx, By, Bz = self.forward_base()
        dBx, dBy, dBz = self.forward_sv()

        mag_vec = wmm_elements(Bx, By, Bz, dBx, dBy, dBz)

        return mag_vec.get_dBdec()

    def get_dBinc(self) -> float:
        """
        Get the delta inclination magnetic elements
        :return: delta inclination in float type
        """

        Bx, By, Bz = self.forward_base()
        dBx, dBy, dBz = self.forward_sv()

        mag_vec = wmm_elements(Bx, By, Bz, dBx, dBy, dBz)

        return mag_vec.get_dBinc()

    def get_all(self) -> dict:
        """
        Get the all of magnetic elements:
        Bx, By, Bz, Bh, Bf, Bdec, Binc
        dBx, dBy, dBz, dBh, dBf, dBdec, dBinc

        :return: dict object includes all of magnetic elements
        """

        Bx, By, Bz = self.forward_base()
        dBx, dBy, dBz = self.forward_sv()

        mag_vec = wmm_elements(Bx, By, Bz, dBx, dBy, dBz)

        return mag_vec.get_all()

    def get_uncertainty(self):

        Bx, By, Bz = self.forward_base()

        mag_vec = wmm_elements(Bx, By, Bz)

        return mag_vec.get_uncertainity(self.err_vals)


