import os.path
import unittest

from geomaglib import util

from wmm import load
from wmm import wmm_calc
from wmm.build import fill_timeslot
from wmm import uncertainty


class Test_wmm(unittest.TestCase):

    def setUp(self):

        self.lat = -18
        self.lon = 138
        self.alt = 77
        self.dec_year = 2025.5

        self.top_dir = os.path.dirname(os.path.dirname(__file__))
        self.wmm_file = os.path.join(self.top_dir, "wmm", "coefs", "WMM2025.cof")

    def test_setup_time(self):

        model = wmm_calc()
        lat, lon, alt = 23.35, 40, 21.0

        model.setup_time(2025, 1, 1)

        model.setup_env(lat, lon, alt)

        model.get_all()

        print(model.get_all())

    def test_setup_env(self):

        lat = -18
        lon = 138
        alt = 77
        dec_year = 2029.5

        alt_true = util.alt_to_ellipsoid_height(alt, lat, lon)
        r, theta = util.geod_to_geoc_lat(lat, alt_true)


        wmm_model = wmm_calc()
        wmm_model.setup_env(lat, lon, alt)
        wmm_model.setup_time(dyear=dec_year)

        self.assertAlmostEqual(wmm_model.lat, lat, places=6)

        self.assertAlmostEqual(wmm_model.theta, theta, places=6)

    def test_forward_base(self):



        lat = -57
        lon = 3
        alt = 74

        dec_year = 2026.0

        wmm_model = wmm_calc()

        wmm_model.setup_time(dyear=dec_year)
        wmm_model.setup_env(lat, lon, alt, msl=False)


        Bx, By, Bz = wmm_model.forward_base()

        self.assertAlmostEqual(Bx, 13268.119649, delta=1e-6)
        self.assertAlmostEqual(By, 5498.179626, delta=1e-6)
        self.assertAlmostEqual(Bz, 23576.062921, delta=1e-6)

    def test_setup_sv(self):

        lat = -18
        lon = 138
        alt = 77

        dec_year = 2029.5

        wmm_model = wmm_calc()

        wmm_model.setup_time(dyear=dec_year)
        wmm_model.setup_env(lat, lon, alt, msl=False)


        dBx, dBy, dBz = wmm_model.forward_sv()

        tol = 1e-6
        self.assertAlmostEqual(dBx,  2.471158, delta=tol)
        self.assertAlmostEqual(dBy, -20.201885, delta=tol)
        self.assertAlmostEqual(dBz, 14.262673, delta=tol)

    def test_get_dBh(self):

        lat = -18
        lon = 138
        alt = 77

        dec_year = 2029.5

        wmm_model = wmm_calc()

        wmm_model.setup_time(dyear=dec_year)
        wmm_model.setup_env(lat, lon, alt, msl=False)


        self.assertTrue(isinstance(wmm_model.get_dBh(), float))



    def test_inherit_GeomagElements(self):
        lat = -21
        lon = 32
        alt = 66



        dec_year = 2029.5

        wmm_model = wmm_calc()

        wmm_model.setup_time(dyear=dec_year)
        wmm_model.setup_env(lat, lon, alt, msl=False)


        map = wmm_model.get_all()

        print(map)

        self.assertAlmostEqual(round(map["ddec"]/60, 1), -0.1, places=6)
        self.assertAlmostEqual(round(map["dinc"] / 60, 1), 0.1, places=6)

    def test_reset_env(self):
        lat = -18
        lon = 138
        alt = 77

        dec_year = 2029.5

        wmm_model = wmm_calc()
        wmm_model.setup_time(dyear=dec_year)
        wmm_model.setup_env(lat, lon, alt, msl=False)



        lat1 = -19
        wmm_model.setup_time(dyear=dec_year)
        wmm_model.setup_env(lat1, lon, alt, msl=False)
        lat2 = wmm_model.lat

        self.assertAlmostEqual(lat2, -19)

    def test_get_minyear(self):

        coef = load.load_wmm_coef(self.wmm_file, skip_two_columns=True)

        self.assertAlmostEqual(coef["min_year"], 2024.96, delta=1e-6)


    def test_correct_time(self):



        user_time = 2030.0



        wmm_model = wmm_calc()

        try:
            wmm_model.setup_time(dyear=user_time)
        except ValueError as e:
            print(e)




    def test_check_altitude(self):
        user_time = 2020.0
        user_time = 2025.1

        lat, lon, alt = 30.0, 20, 700

        wmm_model = wmm_calc()

        wmm_model.setup_time(dyear=user_time)
        wmm_model.setup_env(lat, lon, alt, msl=False)


    def test_check_latitude(self):
        user_time = 2020.0
        user_time = 2025.1

        lat, lon, alt = 90.1, 20, 700

        wmm_model = wmm_calc()

        try:
            wmm_model.setup_time(dyear=user_time)
            wmm_model.setup_env(lat, lon, alt, msl=False)
        except ValueError as e:
            print(e)




    def test_check_longtitude(self):

        user_time = 2020.0
        user_time = 2025.1

        lat, lon, alt = 90.0, 361, 700

        wmm_model = wmm_calc()

        try:
            wmm_model.setup_time(dyear=user_time)
            wmm_model.setup_env(lat, lon, alt, msl=False)
        except ValueError as e:
            print(e)




    def test_fill_timeslot(self):
        year = None
        month =3
        day = 25

        year, month, day = fill_timeslot(year, month, day)

        self.assertEqual(year, 2024)
        self.assertEqual(month, 3)
        self.assertEqual(day, 25)


    def test_not_setup_env(self):

        model = wmm_calc()
        model.setup_time(dyear=2025.5)
        x = model.get_Bx()

        print(x)

    def test_wmm_altitude_warning(self):

        lat = -18
        lon = 138
        alt = -20
        dec_year = 2025.5

        wmm_model = wmm_calc()
        wmm_model.setup_env(lat, lon, alt)

    def test_get_uncertainty(self):

        lat = -18
        lon = 138
        alt = -20

        model = wmm_calc()
        model.setup_time(dyear=2025.5)
        model.setup_env(lat, lon, alt)

        print(model.get_uncertainty())

    def test_coef_load(self):

        model = wmm_calc()
        model.setup_time(dyear=2025.5)
        for lat in range(-90, 91):
            for lon in range(-180, 180):

                model.setup_env(lat, lon, 0)
                model.get_all()







if __name__ == '__main__':
    unittest.main()
