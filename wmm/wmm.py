from geomaglib import Leg_SHA_for_import, util

def get_geoc_vector(lat, lon, alt):

    alt = util.alt_to_ellipsoid_height(alt, lat, lon)
    r, theta = util.geod_to_geoc_lat(lat, alt)

    return r, theta, alt



r, theta, alt = get_geoc_vector(20, 50, 0)

print(f"r: {r}, theta: {theta}, alt: {alt}")
