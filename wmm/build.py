import os
import warnings
from geomaglib import util, legendre, magmath, sh_vars, sh_loader
from wmm import load, COEFS_FILE


class model:

    def __init__(self):

        self.coef_file = COEFS_FILE
        self.nmax = 12
        self.max_year = 2030.0
        self.min_date = ""
        self.msl = True
        self.coef_dict = {}
        self.timly_coef_dict = {}
        self.lat = None
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
    def setup_env(self, lat, lon, alt, year=None, month=None, day=None, dyear=None):


        self.lat = lat
        lon = lon
        alt = alt

        self.dyear = dyear
        if self.dyear == None:
            self.dyear = util.calc_dec_year(year, month, day)

        if not self.coef_dict:
            self.load_coeffs(self.coef_file)

        self.check_coords(self.lat, lon, alt, self.dyear, self.coef_dict)

        self.timly_coef_dict = sh_loader.timely_modify_magnetic_model(self.coef_dict, self.dyear)

        if self.msl:
            alt = util.alt_to_ellipsoid_height(alt, self.lat, lon)
        self.r, self.theta = util.geod_to_geoc_lat(self.lat, alt)
        self.sph_dict = sh_vars.comp_sh_vars(lon, self.r, self.theta, self.nmax)

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

        if alt > -1 or alt < 600:
            warnings.warn("Altitude is should between -1 km to 600 km")

    def forward_base(self):

        Bt, Bp, Br = magmath.mag_SPH_summation(self.nmax, self.sph_dict, self.timly_coef_dict["g"], self.timly_coef_dict["h"], self.Leg, self.theta)


        Bx, By, Bz = magmath.rotate_magvec(Bt, Bp, Br, self.theta, self.lat)

        return magmath.GeomagElements(Bx, By, Bz)

    def forward(self):

        mag_vec = self.forward_base()

        dBt, dBp, dBr = magmath.mag_SPH_summation(self.nmax, self.sph_dict, self.timly_coef_dict["g_sv"], self.timly_coef_dict["h_sv"], self.Leg, self.theta)

        dBx, dBy, dBz = magmath.rotate_magvec(dBt, dBp, dBr, self.theta, self.lat)
        mag_vec.set_sv_vec(dBx, dBy, dBz)
        return mag_vec


