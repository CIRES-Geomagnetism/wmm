import unittest
from wmm_py import wmm

class Test_geomaglib(unittest.testcase):

    def setUp()->None:

    def test_get_geoc_vec():

        

        r, theta, alt = wmm.get_geoc_vec(lat, lon, alt)
