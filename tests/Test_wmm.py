import os.path
import unittest
import numpy as np
import datetime as dt

from geomaglib import util, sh_loader

from wmm import load, utils
from wmm import wmm_calc
from wmm.build import fill_timeslot



class Test_wmm(unittest.TestCase):

    def setUp(self):

        self.lat = np.array([23.35, 24.5])
        self.lon = np.array([40, 45])
        self.alt = np.ones(len(self.lat)) * 21

        self.year = np.array([2025, 2026]).astype(int)
        self.month = np.array([12, 1]).astype(int)
        self.day = np.array([6, 15]).astype(int)

        self.dyears = np.array([2025.5, 2026.6])

        self.top_dir = os.path.dirname(os.path.dirname(__file__))
        self.wmm_file = os.path.join(self.top_dir, "wmm", "coefs", "WMM.COF")

    def test_setup_dtime_arr(self):

        model = wmm_calc()
        dyears = np.array([2025.5, 2026.6])

        model.setup_env(self.lat, self.lon, self.alt)
        model.setup_time(dyear=self.dyears)

        for i in range(len(dyears)):
            self.assertAlmostEqual(dyears[i], model.dyear[i], places=1)


    def test_setup_dtime_tuple(self):

        model = wmm_calc()
        dyears = (2025.5, 2026.6)

        dy_arr = utils.to_npFloatarr(dyears)

        lat = (10,20)

        lat= utils.to_npIntarr(lat)

        model.setup_env(lat, self.lon, self.alt)
        model.setup_time(dyear=dy_arr)

        for i in range(len(dyears)):
            self.assertAlmostEqual(dyears[i], model.dyear[i], places=1)

    def test_setup_strdate(self):

        model = wmm_calc()
        years = np.array([2025, 2026])
        months = np.array([10,11]).astype(int)
        days = np.array([1,2]).astype(int)



        model.setup_env(self.lat, self.lon, self.alt)
        model.setup_time(years, months, days)


        dyears = [2025.7479452054795, 2026.835616438356]


        for i in range(len(years)):
            self.assertAlmostEqual(dyears[i], model.dyear[i], places=6)

    def test_fill_timeslot(self):
        year = None
        month = 3
        day = 25

        year, month, day = fill_timeslot(year, month, day)

        self.assertEqual(year, 2025)
        self.assertEqual(month, 3)
        self.assertEqual(day, 25)

        year, month, day = fill_timeslot(year, month, day)

        self.assertEqual(year, 2025)
        self.assertEqual(month, 3)

    def test_setup_empty_time(self):

        model = wmm_calc()
        # model.setup_time()

        model.setup_time()

        model.setup_env(self.lat, self.lon, self.alt)

        model.get_all()
        curr_time = dt.datetime.now()
        year = curr_time.year
        month = curr_time.month
        day = curr_time.day

        dyear = util.calc_dec_year(year, month, day)

        self.assertEqual(dyear, model.dyear)


    def test_broadcast(self):


        model = wmm_calc()
        years = np.array([2025.5, 2026]).astype(int)
        months = np.array([10, 11]).astype(int)
        days = np.array([1, 2]).astype(int)
        N = 20

        # the shape of lats and lons is 1
        lats = np.array([1])
        lons = np.array([100])
        alts = np.linspace(0, 100, N)

        model.setup_env(lats, lons, alts)
        model.setup_time(years, months, days)

        self.assertEqual(len(model.lat), N)
        self.assertEqual(len(model.lon), N)

        # the shape of lats is 1
        lons = np.linspace(0,180, N)
        alts = np.linspace(0, 100, N)
        model.dyear = [2025.5]

        model.setup_env(lats, lons, alts)
        model.setup_time(years, months, days)

        self.assertEqual(len(model.lat), N)
        self.assertEqual(len(model.lon), N)

    def test_setup_geod_to_geoc_lat(self):



        alt_true = util.alt_to_ellipsoid_height(self.alt, self.lat, self.lon)
        r, theta = util.geod_to_geoc_lat(self.lat, self.alt)




        wmm_model = wmm_calc()
        wmm_model.setup_env(self.lat, self.lon, self.alt, msl=False)
        wmm_model.setup_time(dyear=self.dyears)

        self.assertAlmostEqual(wmm_model.lat[0], self.lat[0], places=6)

        self.assertAlmostEqual(wmm_model.theta[len(self.lat) - 1], wmm_model.theta[len(self.lat) - 1], places=6)


    def test_to_km(self):

        wmm_model = wmm_calc()
        wmm_model.setup_env(self.lat, self.lon, self.alt, msl=False, unit="m")
        wmm_model.setup_time(2025, 1, 1)

        for i in range(len(self.alt)):
            self.assertAlmostEqual(self.alt[i]*1000, wmm_model.alt[i], places=6)





    def test_forward_base(self):



        lat = np.array([-57])
        lon = np.array([3])
        alt = np.array([74])

        dec_year = np.array([2026.0])

        wmm_model = wmm_calc()

        wmm_model.setup_time(dyear=dec_year)
        wmm_model.setup_env(lat, lon, alt, msl=False)


        print(wmm_model.timly_coef_dict["g"][:5])
        Bx, By, Bz = wmm_model.forward_base()


        self.assertAlmostEqual(Bx[0], 13268.119649, delta=1e-3)
        self.assertAlmostEqual(By[0], -5498.179626, delta=1e-3)
        self.assertAlmostEqual(Bz[0], -23576.062921, delta=1e-3)

    def test_setup_sv(self):

        lat = np.array([-18])
        lon = np.array([138])
        alt = np.array([77])

        dec_year = np.array([2029.5])

        wmm_model = wmm_calc()

        wmm_model.setup_time(dyear=dec_year)
        wmm_model.setup_env(lat, lon, alt, msl=False)


        dBx, dBy, dBz = wmm_model.forward_sv()

        tol = 1e-6
        self.assertAlmostEqual(dBx[0],  2.471158, delta=tol)
        self.assertAlmostEqual(dBy[0], -20.201885, delta=tol)
        self.assertAlmostEqual(dBz[0], 14.262673, delta=tol)

    def test_get_dBh(self):

        lat = np.array([-18])
        lon = np.array([138])
        alt = np.array([77])

        dec_year = np.array([2029.5])

        wmm_model = wmm_calc()

        wmm_model.setup_time(dyear=dec_year)
        wmm_model.setup_env(lat, lon, alt, msl=False)


        self.assertTrue(isinstance(wmm_model.get_dBh()[0], float))
        self.assertAlmostEqual(wmm_model.get_dBh()[0], 0.895474, delta=1e-3)



    def test_inherit_GeomagElements(self):
        lat = np.array([-18])
        lon = np.array([138])
        alt = np.array([77])


        dec_year = np.array([2029.5])

        wmm_model = wmm_calc()

        wmm_model.setup_time(dyear=dec_year)
        wmm_model.setup_env(lat, lon, alt, msl=False)


        map = wmm_model.get_all()

        print(map)

        self.assertAlmostEqual(map["ddec"][0]/60, -0.036580, places=6)
        self.assertAlmostEqual(map["dinc"][0]/60, 0.012491, places=6)

    def test_reset_env(self):
        lat = np.array([-18])
        lon = np.array([138])
        alt = np.array([77])

        dec_year = np.array([2029.5])

        wmm_model = wmm_calc()
        wmm_model.setup_time(dyear=dec_year)
        wmm_model.setup_env(lat, lon, alt, msl=False)



        lat1 = np.array([-19])
        wmm_model.setup_time(dyear=dec_year)
        wmm_model.setup_env(lat1, lon, alt, msl=False)
        lat2 = wmm_model.lat[0]

        self.assertAlmostEqual(lat2, -19)

    def test_load_wmmcoeff(self):

        coef_dict = sh_loader.load_coef(self.wmm_file, skip_two_columns=True, end_degree=12)





        coef = load.load_wmm_coef(self.wmm_file)



        self.assertEqual(2025, coef["epoch"])
        self.assertAlmostEqual(coef["min_year"][0], 2024.866, delta=1e-3)



    def test_correct_time(self):



        user_time = np.array([2030.0])



        wmm_model = wmm_calc()

        try:
            wmm_model.setup_time(dyear=user_time)
        except ValueError as e:
            print(e)




    def test_check_altitude(self):

        user_time = np.array([2025.1])

        lat = np.array([-18])
        lon = np.array([138])
        alt = np.array([3000])

        wmm_model = wmm_calc()

        wmm_model.setup_time(dyear=user_time)
        wmm_model.setup_env(lat, lon, alt, msl=False)


    def test_check_latitude(self):

        user_time = np.array([2025.1])
        lat, lon, alt = 90.1, 20, 700

        wmm_model = wmm_calc()

        try:
            wmm_model.setup_time(dyear=user_time)
            wmm_model.setup_env(lat, lon, alt, msl=False)
        except ValueError as e:
            print(e)




    def test_check_longtitude(self):

        user_time = np.array([2025.1])

        lat = np.array([-18])
        lon = np.array([138])
        alt = np.array([3000])

        wmm_model = wmm_calc()

        try:
            wmm_model.setup_time(dyear=user_time)
            wmm_model.setup_env(lat, lon, alt, msl=False)
        except ValueError as e:
            print(e)






    @unittest.expectedFailure
    def test_not_setup_env(self):

        model = wmm_calc()
        user_time = np.array([2025.1])
        model.setup_time(dyear=user_time)
        x = model.get_Bx()



    def test_wmm_altitude_warning(self):

        user_time = np.array([2025.1])

        lat = np.array([-18])
        lon = np.array([138])
        alt = np.array([3000])

        wmm_model = wmm_calc()
        wmm_model.setup_env(lat, lon, alt)

    def test_get_uncertainty(self):

        user_time = np.array([2025.1])

        lat = np.array([-18, 20, 20])
        lon = np.array([138, 139, 140])
        alt = np.array([100, 150, 200])

        model = wmm_calc()
        model.setup_time(dyear=user_time)
        model.setup_env(lat, lon, alt)

        print(model.get_uncertainty())





if __name__ == '__main__':
    unittest.main()