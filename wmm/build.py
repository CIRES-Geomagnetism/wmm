import os
from geomaglib import util, Leg_SHA_for_import, magmath, sh_vars, sh_loader
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


def compile(lat, lon, alt, dec_year, wmm_coeffs):
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

    if coef_dict["min_year"] <= dec_year <= max_year:
        timly_coef_dict = sh_loader.timely_modify_magnetic_model(coef_dict, dec_year)

        nmax = sh_loader.calc_num_elems_to_sh_degrees(len(coef_dict["g"]))
        r, theta = util.geod_to_geoc_lat(lat, alt)
        sph_dict = sh_vars.comp_sh_vars(lon, r, theta, nmax)

        cotheta = 90 - theta

        colats = [cotheta]

        Leg = Leg_SHA_for_import.Flattened_Chaos_Legendre1(nmax, colats)

        Bt, Bp, Br = magmath.mag_SPH_summation(nmax, sph_dict, timly_coef_dict, Leg, theta)

        Bx, By, Bz = magmath.rotate_magvec(Bt, Bp, Br, theta, lat)

        return Bx, By, Bz
    else:
        max_year = round(max_year, 1)
        min_year = round(coef_dict["min_year"], 1)
        raise ValueError(f"Invalid year. Please provide date <= {min_year} and >= {max_year}")