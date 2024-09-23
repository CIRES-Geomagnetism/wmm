import os
import warnings
import math
from geomaglib import util, legendre, magmath, sh_vars, sh_loader
from wmm import load, COEFS_FILE

class wmm_elements(magmath.GeomagElements):

    def __init__(self, Bx, By, Bz, dBx = None, dBy = None, dBz = None):
        super().__init__(Bx, By, Bz, dBx, dBy, dBz)



    def get_dBdec(self):

        ddec = super().get_dBdec()

        return ddec*60.0

    def get_dBinc(self):
        ddec = super().get_dBinc()

        return ddec * 60.0

    def get_all(self):

        mag_map = super().get_all()

        mag_map["ddec"] = mag_map["ddec"]*60.0
        mag_map["dinc"] = mag_map["dinc"]*60.0

        return mag_map




class model():

    def __init__(self):

        self.coef_file = COEFS_FILE
        self.nmax = 12
        self.max_year = 2030.0
        self.min_date = ""
        self.coef_dict = {}
        self.timly_coef_dict = {}
        self.lat = None
        self.lon = None
        self.alt = None
        self.r = None
        self.theta = None
        self.sph_dict = {}
        self.Leg = []

    def get_wmmcoefs_path(self, filename):

        currdir = os.path.dirname(__file__)

        coef_file = os.path.join(currdir, "coefs", filename)

        return coef_file

    def load_coeffs(self, filename):
        wmm_coeffs = self.get_wmmcoefs_path(filename)
        self.coef_dict = load.load_wmm_coef(wmm_coeffs, skip_two_columns=True)
        self.max_year = self.coef_dict["epoch"] + 5.0
        self.min_date = self.coef_dict["min_date"]
        self.nmax = sh_loader.calc_num_elems_to_sh_degrees(len(self.coef_dict["g"]))


    def _set_msl_False(self):
        self.msl = False

    def to_km(self, alt, unit):

        if unit == "km":
            return alt

        elif unit == "m":
            return alt*1000
        elif unit == "feet":
            return alt*0.0003048
        else:
            raise ValueError("Get unknown unit. Please provide km, m or feet.")
    def setup_env(self, lat, lon, alt, year=None, month=None, day=None, dyear=None, unit="km", msl=True):


        self.lat = lat
        self.lon = lon


        self.alt = self.to_km(alt, unit)

        self.dyear = dyear
        if self.dyear == None:
            self.dyear = util.calc_dec_year(year, month, day)

        if not self.coef_dict:
            self.load_coeffs(self.coef_file)

        self.check_coords(self.lat, self.lon, self.alt, self.dyear, self.coef_dict)

        self.timly_coef_dict = sh_loader.timely_modify_magnetic_model(self.coef_dict, self.dyear)

        if msl:
            self.alt = util.alt_to_ellipsoid_height(alt, self.lat, self.lon)
        self.r, self.theta = util.geod_to_geoc_lat(self.lat, self.alt)
        self.sph_dict = sh_vars.comp_sh_vars(self.lon, self.r, self.theta, self.nmax)

        cotheta = 90.0 - self.theta

        colats = [cotheta]

        self.Leg = legendre.Flattened_Chaos_Legendre1(self.nmax, colats)

    def check_coords(self, lat, lon, alt, dyear, coef_dict):
        if dyear < coef_dict["min_year"] or dyear > self.max_year:
            max_year = round(self.max_year, 1)
            raise ValueError(f"Invalid year. Please provide date from {self.min_date} to {int(max_year)}-01-01 00:00")

        if lat > 90.0 or lat < -90.0:
            raise ValueError("latitude should between -90 to 90")

        if lon > 360.0 or lon < -180.0:
            raise ValueError("lontitude should between -180 t")

        if alt > -1 or alt < 850:
            warnings.warn("Altitude is should between -1 km to 850 km")


    def check_blackout_zone(self, Bx, By, Bz):

        wmm_calc = wmm_elements(Bx, By, Bz)
        h = wmm_calc.get_Bh()
        if h <= 2000.0:
            warnings.warn(f"Warning: (lat, lon, alt(Ellipsoid Height in km)) = ({self.lat}, {self.lon}, {self.alt}) is in the blackout zone around the magnetic pole as defined by the WMM military specification"
                          " (https://www.ngdc.noaa.gov/geomag/WMM/data/MIL-PRF-89500B.pdf). Compass accuracy is highly degraded in this region.\n")
        elif h <= 6000.0:
            warnings.warn(f"Caution: (lat, lon, alt(Ellipsoid Height in km)) = ({self.lat}, {self.lon}, {self.alt}) is approaching the blackout zone around the magnetic pole as defined by the WMM military specification "
                                     "(https://www.ngdc.noaa.gov/geomag/WMM/data/MIL-PRF-89500B.pdf). Compass accuracy may be degraded in this region.\n")
    def forward_base(self):

        Bt, Bp, Br = magmath.mag_SPH_summation(self.nmax, self.sph_dict, self.timly_coef_dict["g"], self.timly_coef_dict["h"], self.Leg, self.theta)


        Bx, By, Bz = magmath.rotate_magvec(Bt, Bp, Br, self.theta, self.lat)

        self.check_blackout_zone(Bx, By, Bz)


        return Bx, By, Bz

    def forward_sv(self):



        dBt, dBp, dBr = magmath.mag_SPH_summation(self.nmax, self.sph_dict, self.timly_coef_dict["g_sv"], self.timly_coef_dict["h_sv"], self.Leg, self.theta)

        dBx, dBy, dBz = magmath.rotate_magvec(dBt, dBp, dBr, self.theta, self.lat)

        return dBx, dBy, dBz

    def get_Bx(self):

        Bx, By, Bz = self.forward_base()

        return Bx

    def get_By(self):

        Bx, By, Bz = self.forward_base()

        return By

    def get_Bz(self):

        Bx, By, Bz = self.forward_base()

        return Bz

    def get_Bh(self):

        Bx, By, Bz = self.forward_base()

        wmm_calc = wmm_elements(Bx, By, Bz)

        return wmm_calc.get_Bh()

    def get_Bf(self):

        Bx, By, Bz = self.forward_base()

        wmm_calc = wmm_elements(Bx, By, Bz)

        return wmm_calc.get_Bf()

    def get_Bdec(self):

        Bx, By, Bz = self.forward_base()

        wmm_calc = wmm_elements(Bx, By, Bz)

        return wmm_calc.get_Bdec()

    def get_Binc(self):

        Bx, By, Bz = self.forward_base()

        wmm_calc = wmm_elements(Bx, By, Bz)

        return wmm_calc.get_Binc()

    def get_dBh(self):

        Bx, By, Bz = self.forward_base()
        dBx, dBy, dBz = self.forward_sv()

        wmm_calc = wmm_elements(Bx, By, Bz, dBx, dBy, dBz)

        return wmm_calc.get_dBh()

    def get_dBf(self):

        Bx, By, Bz = self.forward_base()
        dBx, dBy, dBz = self.forward_sv()

        wmm_calc = wmm_elements(Bx, By, Bz, dBx, dBy, dBz)

        return wmm_calc.get_dBf()

    def get_dBdec(self):

        Bx, By, Bz = self.forward_base()
        dBx, dBy, dBz = self.forward_sv()

        wmm_calc = wmm_elements(Bx, By, Bz, dBx, dBy, dBz)

        return wmm_calc.get_dBdec()

    def get_dBinc(self):

        Bx, By, Bz = self.forward_base()
        dBx, dBy, dBz = self.forward_sv()

        wmm_calc = wmm_elements(Bx, By, Bz, dBx, dBy, dBz)

        return wmm_calc.get_dBinc()

    def get_all(self):

        Bx, By, Bz = self.forward_base()
        dBx, dBy, dBz = self.forward_sv()

        wmm_calc = wmm_elements(Bx, By, Bz, dBx, dBy, dBz)

        return wmm_calc.get_all()





