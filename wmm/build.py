import os
import warnings
from geomaglib import util, legendre, magmath, sh_vars, sh_loader
from wmm import load, coef_dict


class model:

    def __init__(self):
        self.max_year = coef_dict["epoch"] + 5.0
        self.min_date = coef_dict["min_date"]
        self.lat = None
        self.msl = True

        self.timly_coef_dict = {}
        self.nmax = sh_loader.calc_num_elems_to_sh_degrees(len(coef_dict["g"]))
        self.r = None
        self.theta = None
        self.sph_dict = {}
        self.Leg = []

    def _set_msl_False(self):
        self.msl = False
    def setup_env(self, lat, lon, alt, year=None, month=None, day=None, dyear=None):

        self.lat = lat
        lon = lon
        alt = alt

        self.dyear = dyear
        if self.dyear == None:
            self.dyear = util.calc_dec_year(year, month, day)

        self.check_coords(self.lat, lon, alt, self.dyear)

        self.timly_coef_dict = sh_loader.timely_modify_magnetic_model(coef_dict, self.dyear)

        if self.msl:
            alt = util.alt_to_ellipsoid_height(alt, self.lat, lon)
        self.r, self.theta = util.geod_to_geoc_lat(self.lat, alt)
        self.sph_dict = sh_vars.comp_sh_vars(lon, self.r, self.theta, self.nmax)

        cotheta = 90.0 - self.theta

        colats = [cotheta]

        self.Leg = legendre.Flattened_Chaos_Legendre1(self.nmax, colats)



    def check_coords(self, lat, lon, alt, dyear):

        if dyear < coef_dict["min_year"] or dyear > self.max_year:
            max_year = round(self.max_year, 1)
            raise ValueError(f"Invalid year. Please provide date from {self.min_date} to {int(max_year)}/01/01")

        if lat > 90.0 or lat < -90.0:
            warnings.warn("latitude is out of range")

        if lon > 360.0 or lon < -180.0:
            warnings.warn("lontitude is out of range")

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


def calc_magnetic_elements(lat, alt, lon, year, month, day):
    # load g, h

    dec_year = util.calc_dec_year(year, month, day)

    alt = util.alt_to_ellipsoid_height(alt, lat, lon)

    return compile(lat, alt, lon, dec_year, wmm_coeffs)


def compile(lat, lon, alt, dec_year, wmm_coeffs) -> magmath.GeomagElements:
    '''
    Inputs:
    :param lat:
    :param lon:
    :param alt: WGS height
    :param dec_year:
    :param wmm_coeffs:
    :return:
    '''


    max_year = coef_dict["epoch"] + 5.0
    min_date = coef_dict["min_date"]

    if dec_year < coef_dict["min_year"] or dec_year > max_year:
        max_year = round(max_year, 1)
        raise ValueError(f"Invalid year. Please provide date from {min_date} to {max_year}/01/01")

    timly_coef_dict = sh_loader.timely_modify_magnetic_model(coef_dict, dec_year)

    nmax = sh_loader.calc_num_elems_to_sh_degrees(len(coef_dict["g"]))
    r, theta = util.geod_to_geoc_lat(lat, alt)
    sph_dict = sh_vars.comp_sh_vars(lon, r, theta, nmax)

    cotheta = 90 - theta

    colats = [cotheta]

    Leg = legendre.Flattened_Chaos_Legendre1(nmax, colats)

    Bt, Bp, Br = magmath.mag_SPH_summation(nmax, sph_dict, timly_coef_dict["g"], timly_coef_dict["h"], Leg, theta)
    print(f"Br:{Br} Bt:{Bt} Bp:{Bp}")
    #dBt, dBp, dBr = magmath.mag_SPH_summation(nmax, sph_dict, timly_coef_dict["g_sv"], timly_coef_dict["h_sv"], Leg, theta)

    Bx, By, Bz = magmath.rotate_magvec(Bt, Bp, Br, theta, lat)
    #dBx, dBy, dBz = magmath.rotate_magvec(Bt, Bp, Br, theta, lat)

    geomag_results = magmath.GeomagElements(Bx, By, Bz)

    return geomag_results

