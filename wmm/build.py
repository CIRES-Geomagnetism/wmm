import os
from geomaglib import util, legendre, magmath, sh_vars, sh_loader
from wmm import load, COEFS_FILE


def get_wmmcoefs_path(filename):

    currdir = os.path.dirname(__file__)

    coef_file = os.path.join(currdir, "coefs", filename)

    return coef_file[0]

def calc_magnetic_elements(lat, alt, lon, year, month, day):
    # load g, h

    dec_year = util.calc_dec_year(year, month, day)
    wmm_coeffs = get_wmmcoefs_path(COEFS_FILE)
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

    coef_dict = load.load_wmm_coef(wmm_coeffs, skip_two_columns=True)
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
    dBt, dBp, dBr = magmath.mag_SPH_summation(nmax, sph_dict, timly_coef_dict["g_sv"], timly_coef_dict["h_sv"], Leg, theta)

    Bx, By, Bz = magmath.rotate_magvec(Bt, Bp, Br, theta, lat)
    dBx, dBy, dBz = magmath.rotate_magvec(Bt, Bp, Br, theta, lat)

    geomag_results = magmath.GeomagElements(Bx, By, Bz)

    return geomag_results

