import os.path
import unittest

from geomaglib import util

from wmm import load
from wmm import build


class Test_wmm(unittest.TestCase):

    def setUp(self):

        self.lat = -18
        self.lon = 138
        self.alt = 77
        self.dec_year = 2024.5

        self.top_dir = os.path.dirname(os.path.dirname(__file__))
        self.wmm_file = os.path.join(self.top_dir, "wmm", "coefs", "WMM2020.COF")

    def test_setup_env(self):

        lat = -18
        lon = 138
        alt = 77
        dec_year = 2024.5

        alt_true = util.alt_to_ellipsoid_height(alt, lat, lon)
        r, theta = util.geod_to_geoc_lat(lat, alt_true)


        wmm_model = build.model()
        wmm_model.setup_env(lat, lon, alt, dyear=dec_year)

        self.assertAlmostEqual(wmm_model.lat, lat, places=6)

        self.assertAlmostEqual(wmm_model.theta, theta, places=6)

    def test_forward_base(self):

        lat = -18
        lon = 138
        alt = 77

        dec_year = 2024.5

        wmm_model = build.model()
        wmm_model._set_msl_False()
        wmm_model.setup_env(lat, lon, alt, dyear=dec_year)


        mag_vec = wmm_model.forward_base()

        self.assertAlmostEqual(round(mag_vec.Bx, 1), 31722.0, delta=0.01)
        self.assertAlmostEqual(round(mag_vec.By, 1), 2569.6, delta=0.01)
        self.assertAlmostEqual(round(mag_vec.Bz, 1), -34986.2, delta=0.01)

    def test_forward_sv(self):

        lat = -18
        lon = 138
        alt = 77

        dec_year = 2024.5

        wmm_model = build.model()
        wmm_model._set_msl_False()
        wmm_model.setup_env(lat, lon, alt, dyear=dec_year)


        mag_vec = wmm_model.forward()

        self.assertAlmostEqual(round(mag_vec.dBx, 1), -9.0, delta=0.01)
        self.assertAlmostEqual(round(mag_vec.dBy, 1), -27.7, delta=0.01)
        self.assertAlmostEqual(round(mag_vec.dBz, 1), -26.8, delta=0.01)

    def test_reset_env(self):
        lat = -18
        lon = 138
        alt = 77

        dec_year = 2024.5

        wmm_model = build.model()
        wmm_model.setup_env(lat, lon, alt, dyear=dec_year)



        lat1 = -19
        wmm_model.setup_env(lat1, lon, alt, dyear=dec_year)
        lat2 = wmm_model.lat

        self.assertAlmostEqual(lat2, -19)
    def test_compile(self):

        lat = -18
        lon = 138
        alt = 77
        dec_year = 2024.5

        results = build.compile(lat, lon, alt, dec_year, self.wmm_file)

        print(f"Bx: {results.Bx}, By: {results.By}, Bz:{results.Bz}")

        self.assertAlmostEqual(round(results.Bx, 1), 31722.0, delta=0.01)
        self.assertAlmostEqual(round(results.By, 1), 2569.6 , delta=0.01)
        self.assertAlmostEqual(round(results.Bz, 1), -34986.2 , delta=0.01)


    def test_get_minyear(self):

        coef = load.load_wmm_coef(self.wmm_file, skip_two_columns=True)

        self.assertAlmostEqual(coef["min_year"], 2019.756, delta=1e-6)


    def test_correct_time(self):


        user_time = 2020.0
        user_time = 2025.1

        self.assertFalse(build.compile(self.lat, self.lon, self.alt, user_time, self.wmm_file))

    def test_check_altitude(self):


        self.assertTrue()

    def test_check_latitude(self):

        self.assertTrue()

    def test_check_longtitude(self):

        self.assertTrue()








if __name__ == '__main__':
    unittest.main()
