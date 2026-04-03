import os.path
import unittest

import geomaglib.util
import numpy as np
import datetime as dt


from geomaglib import util, sh_loader

from wmm import load, utils
from wmm import wmm_calc
from wmm.build import fill_timeslot
from wmm import uncertainty



class Test_wmm(unittest.TestCase):

    def setUp(self):



        self.year = np.array([2025, 2026]).astype(int)
        self.month = np.array([12, 1]).astype(int)
        self.day = np.array([6, 15]).astype(int)

        self.dyears = np.array([2025.5, 2026.6])

        self.top_dir = os.path.dirname(os.path.dirname(__file__))
        self.wmm_file = os.path.join(self.top_dir, "wmm", "coefs", "WMM.COF")
        coef = load.load_wmm_coefs(self.wmm_file, nmax=12)
        self.start_time = coef["epoch"]

        self.wmm_testval = os.path.join(self.top_dir, "tests", "WMM2025_TEST_VALUE_TABLE_FOR_REPORT.txt")
        self.get_wmm_testval()


    def get_wmm_testval(self):

        self.dyears, self.alts, self.lats, self.lons = [], [], [], []
        self.Bh, self.Bf, self.Bx, self.By, self.Bz, self.Bdec, self.Binc, self.Bgv = [], [], [], [], [], [], [], []
        self.dBh, self.dBf, self.dBx, self.dBy, self.dBz, self.dBdec, self.dBinc = [], [], [], [], [], [], []

        with open(self.wmm_testval, "r") as fp:
            for line in fp:
                vals = line.split()

                if vals[0] == "#":
                    continue
                else:
                    for i in range(len(vals)):
                        vals[i] = float(vals[i])
                    dyear, alt, lat, lon = vals[0], vals[1], vals[2], vals[3]
                    x, y, z, h, f, inc, dec, gv = vals[4], vals[5], vals[6], vals[7], vals[8], vals[9], vals[10], vals[
                        11]
                    dx, dy, dz, dh, df, dinc, ddec = vals[12], vals[13], vals[14], vals[15], vals[16], vals[17], vals[
                        18]

                self.dyears.append(dyear)
                self.alts.append(alt)
                self.lats.append(lat)
                self.lons.append(lon)

                self.Bdec.append(dec)
                self.Binc.append(inc)
                self.Bx.append(x)
                self.By.append(y)
                self.Bz.append(z)
                self.Bh.append(h)
                self.Bf.append(f)
                self.Bgv.append(gv)

                self.dBdec.append(ddec)
                self.dBinc.append(dinc)
                self.dBx.append(dx)
                self.dBy.append(dy)
                self.dBz.append(dz)
                self.dBh.append(dh)
                self.dBf.append(df)

    def test_load_wmmcoeff(self):

        nmax = 12
        coef = load.load_wmm_coefs(self.wmm_file, nmax)
        num_elems = sh_loader.calc_sh_degrees_to_num_elems(nmax)


        self.assertEqual(2025, coef["epoch"])
        self.assertAlmostEqual(coef["min_year"][0], 2024.866, delta=1e-3)
        self.assertEqual(len(coef["g"]), num_elems + 1)

    def test_setup_max_degree(self):
        """
        Check whether setup_max_degree() can allow users to set up the max degree. When the input
        is out of range or have invalid type, it should return error to users.
        """

        nmax_cases = [1, 5, 10, 11]
        print("here")


        decimal_year = float(self.start_time) + 0.5


        for nmax in nmax_cases:
            print(f'doing test case {nmax}')
            model = wmm_calc(nmax)
            model.setup_time(dyear = decimal_year + 0.1*nmax)
            num_elements = sh_loader.calc_sh_degrees_to_num_elems(nmax)
            self.assertEqual(len(model.coef_dict["g"]), num_elements + 1)
            self.assertEqual(nmax, model.nmax)
            model.setup_env(lat = 5, lon = 5, alt = 0)


        nmax_cases = [0, 13, 14]
        for nmax in nmax_cases:
            try:
                model = wmm_calc(nmax)
                model.setup_max_degree(nmax)
                model.setup_time(dyear = decimal_year + 0.1*nmax)
            except ValueError as e:
                self.assertEqual(str(e), f"The degree is not available. Please assign the degree > 0 and degree <= 12.")

        nmax_cases = [5.0, 11.9]
        for nmax in nmax_cases:
            try:
                print(nmax)
                model = wmm_calc(nmax)
                model.setup_max_degree(nmax)
                model.setup_time(dyear = decimal_year + 0.1*nmax)
            except TypeError as e:
                print(e)
                self.assertEqual(str(e), f"Please provide nmax with integer type.")

    def test_setup_dtime_arr(self):
        """
        Test users can use setup_time() with dyear .
        """

        model = wmm_calc()
        date1 = float(self.start_time) + 0.66
        date2 = float(self.start_time) + 0.7

        dyears = np.array([date1, date2])

        model.setup_env(self.lats, self.lons, self.alts)
        model.setup_time(dyear=self.dyears)

        for i in range(len(dyears)):
            self.assertAlmostEqual(self.dyears[i], model.dyear[i], places=1)


    def test_setup_dtime_tuple(self):
        """
        Test whether uesers can uset setup_time() with dyear in tuple.
        """

        model = wmm_calc()
        date1 = float(self.start_time) + 2.8
        date2 = float(self.start_time) + 3.5


        dyears = (date1, date2)

        dy_arr = utils.to_npFloatarr(dyears)

        lats = (10,20)
        lons = [100, 105.5]
        alts = [100, 200]

        lats= utils.to_npIntarr(lats)

        model.setup_env(lats, lons, alts)
        model.setup_time(dyear=dy_arr)

        for i in range(len(dyears)):
            self.assertAlmostEqual(dyears[i], model.dyear[i], places=1)

    def test_setup_strdate(self):
        """
        Test users can pass year, month and day in array type to setup_time()
        """

        model = wmm_calc()
        year1 = int(self.start_time) + 2
        year2 = int(self.start_time) + 3
        years = np.array([year1, year2])
        months = np.array([10,11]).astype(int)
        days = np.array([1,2]).astype(int)

        dYear1 = geomaglib.util.calc_dec_year(year1, 10, 1)
        dYear2 = geomaglib.util.calc_dec_year(year2, 11, 2)
        dyears = [dYear1, dYear2]

        model.setup_env(self.lats[:2], self.lons[:2], self.alts[:2])
        model.setup_time(years, months, days)

        for i in range(len(years)):
            self.assertAlmostEqual(dyears[i], model.dyear[i], places=6)

    def test_fill_timeslot(self):
        """
        When user miss either one of the variables, it should use the current time value as default
        """
        year = None
        month = 3
        day = 25

        dt_today = dt.datetime.now()
        this_year = dt_today.year

        year, month, day = fill_timeslot(year, month, day)

        self.assertEqual(year, this_year)
        self.assertEqual(month, 3)
        self.assertEqual(day, 25)

        year, month, day = fill_timeslot(year, month, day)

        self.assertEqual(year, this_year)
        self.assertEqual(month, 3)

    def test_setup_empty_time(self):
        """
        When users doesn't pass any time variable to setup_time(), it should use the current time as default.
        """
        model = wmm_calc()
        # model.setup_time()

        model.setup_time()

        model.setup_env(self.lats, self.lons, self.alts)

        model.get_all()
        curr_time = dt.datetime.now()
        year = curr_time.year
        month = curr_time.month
        day = curr_time.day

        dyear = util.calc_dec_year(year, month, day)

        self.assertEqual(dyear, model.dyear)


    def test_broadcast(self):
        """
        Test whether the model can broadcast each of coordinates(lat, lon and alt) to the same shape.
        """


        model = wmm_calc()

        year1 = int(self.start_time) + 1
        year2 = int(self.start_time) + 3

        years = np.array([year1, year2]).astype(int)
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
        dYear = float(self.start_time) + 0.55
        model.dyear = [2025.5]

        model.setup_env(lats, lons, alts)
        model.setup_time(years, months, days)
        self.assertEqual(len(model.lat), N)
        self.assertEqual(len(model.lon), N)

        # When year, month, day and coordinates has different shape, and year, month and day shape is not 1
        wmm = wmm_calc()
        wmm.setup_env(lats, lons, alts)
        try:

            wmm.setup_time(years, months, days)
        except ValueError as e:
            self.assertEqual(str(e), f"The input time and space vectors have different sizes of time size: {len(years)}, "
                                     f"position sizes: ({len(lats)}, {len(lons)}, {len(alts)}), input scalars, or vectors of matching length")





        #except ValueError as e:
        #    print(str(e))


    def test_setup_geod_to_geoc_lat(self):
        """
        Test the covertion of geodetic to geocentric can be done correctly when it is called by setup_env()
        """


        alt_true = util.alt_to_ellipsoid_height(self.alts, self.lats, self.lons)
        r, theta = util.geod_to_geoc_lat(self.lats, alt_true)

        wmm_model = wmm_calc()
        wmm_model.setup_env(self.lats, self.lons, self.alts, msl=False)
        wmm_model.setup_time(dyear=self.dyears)

        for i in range(len(self.lats)):
            self.assertAlmostEqual(wmm_model.lat[i], self.lats[i], places=6)

            self.assertAlmostEqual(wmm_model.theta[len(self.lats) - 1], theta[len(self.lats) - 1], places=6)


    def test_to_km(self):
        """
        Test to_km() function
        """

        wmm_model = wmm_calc()
        wmm_alts = wmm_model.to_km(np.array(self.alts), unit="m")

        for i in range(len(self.alts)):
            self.assertAlmostEqual(self.alts[i]/1000, wmm_alts[i], places=6)

    def test_forward_base(self):
        """
        Test forward_base() can return the correct Bx, By and Bz in geodetic
        """


        wmm_model = wmm_calc()

        wmm_model.setup_time(dyear=self.dyears)
        wmm_model.setup_env(self.lats, self.lons, self.alts, msl=False)

        Bx, By, Bz = wmm_model.forward_base()

        for i in range(len(self.Bx)):
            self.assertAlmostEqual(Bx[i], self.Bx[i], delta=0.05)
            self.assertAlmostEqual(By[i], self.By[i], delta=0.05)
            self.assertAlmostEqual(Bz[i], self.Bz[i], delta=0.05)

    def test_get_sv(self):

        """
        Test users can get sv values by calling forward_sv()
        """

        lat = np.array([-18])
        lon = np.array([138])
        alt = np.array([77])

        dYear = float(self.start_time) + 4.5
        dec_year = np.array([dYear])

        wmm_model = wmm_calc()

        wmm_model.setup_time(dyear=self.dyears)
        wmm_model.setup_env(self.lats, self.lons, self.alts, msl=False)

        dBx, dBy, dBz = wmm_model.forward_sv()

        tol = 0.05
        for i in range(len(self.Bx)):
            self.assertAlmostEqual(dBx[i], self.dBx[i], delta=tol)
            self.assertAlmostEqual(dBy[i], self.dBy[i], delta=tol)
            self.assertAlmostEqual(dBz[i], self.dBz[i], delta=tol)

    def test_get_dBh(self):


        wmm_model = wmm_calc()

        wmm_model.setup_time(dyear=self.dyears)
        wmm_model.setup_env(self.lats, self.lons, self.alts, msl=False)

        dh = wmm_model.get_dBh()
        self.assertTrue(isinstance(dh[0], float))

        for i in range(len(self.dBh)):
            self.assertAlmostEqual(dh[i], self.dBh[i], delta=0.05)

    def test_get_dBdec(self):

        wmm_model = wmm_calc()

        wmm_model.setup_time(dyear=self.dyears)
        wmm_model.setup_env(self.lats, self.lons, self.alts, msl=False)

        dBdec = wmm_model.get_dBdec()
        self.assertTrue(isinstance(dBdec[0], float))

        for i in range(len(self.dBh)):
            self.assertAlmostEqual(dBdec[i], self.dBdec[i], delta=0.05)


    def test_get_dBinc(self):

        wmm_model = wmm_calc()

        wmm_model.setup_time(dyear=self.dyears)
        wmm_model.setup_env(self.lats, self.lons, self.alts, msl=False)

        dBinc = wmm_model.get_dBinc()
        self.assertTrue(isinstance(dBinc[0], float))

        for i in range(len(self.dBh)):
            self.assertAlmostEqual(dBinc[i], self.dBinc[i], delta=0.05)



    def test_inherit_GeomagElements(self):

        """
        wmm_element class inherit magmath.GeomagElements class from geomaglib.
        The test is to check whether it can computing ddec and dinc correctly by using magmath.GeomagElements
        """


        wmm_model = wmm_calc()

        wmm_model.setup_time(dyear=self.dyears)
        wmm_model.setup_env(self.lats, self.lons, self.alts, msl=False)


        map = wmm_model.get_all()

        for i in range(len(self.dBdec)):
            self.assertAlmostEqual(map["ddec"][i] , self.dBdec[i], delta=0.05)
            self.assertAlmostEqual(map["dinc"][i] , self.dBinc[i], delta=0.05)

    def test_reset_env(self):
        """
        When users only call wmm class once, it should allow users to reset the lat, lon or alt when users call the function again
        """
        lat = np.array([-18])
        lon = np.array([138])
        alt = np.array([77])

        dYear = float(self.start_time) + 4.5
        dec_year = np.array([dYear])

        wmm_model = wmm_calc()
        wmm_model.setup_time(dyear=dec_year)
        wmm_model.setup_env(lat, lon, alt, msl=False)

        lat1 = np.array([-19])
        wmm_model.setup_time(dyear=dec_year)
        wmm_model.setup_env(lat1, lon, alt, msl=False)
        lat2 = wmm_model.lat[0]

        self.assertAlmostEqual(lat2, -19)



    def test_correct_time(self):

        """
        Test whether it can verify users provide the valid time for the model.
        """

        date1 = float(self.start_time) + 5.0
        date2 = float(self.start_time) - 0.3
        user_time = np.array([date1, date2])

        get_err = 0

        wmm_model = wmm_calc()

        for i in range(2):
            try:
                wmm_model.setup_time(dyear=user_time)
            except ValueError as e:
                get_err += 1
                self.assertEqual(str(e), "Invalid year. Please provide date from [2024]-[11]-[13] to [2030]-[01]-[01] 00:00")

        self.assertEqual(get_err, 2)



    def test_check_latitude(self):
        """
        Test whether it can verify users provide the valid latitude.
        """

        date1 = float(self.start_time) + 0.1
        user_time = np.array([date1])
        lon, alt = 20, 700

        lat = [-90.8, 90.1]
        get_err = 0

        wmm_model = wmm_calc()

        for i in range(2):
            try:
                wmm_model.setup_time(dyear=user_time)
                wmm_model.setup_env(lat, lon, alt, msl=False)
            except ValueError as e:
                self.assertEqual(str(e), "latitude should between -90 to 90")
                get_err += 1

        self.assertEqual(get_err, 2)




    def test_check_longtitude(self):
        """
        Test whether it can verify users provide the valid longitude.
        """

        date1 = float(self.start_time) + 0.1
        user_time = np.array([date1])

        lat = np.array([-18])
        lon = np.array([-180.0, 360.1])
        alt = np.array([3000])

        wmm_model = wmm_calc()
        get_err = 0

        for i in range(2):
            try:
                wmm_model.setup_time(dyear=user_time)
                wmm_model.setup_env(lat, lon, alt, msl=False)
            except ValueError as e:
                self.assertEqual(str(e), "lontitude should between -180 to 360")
                get_err += 1

        self.assertEqual(get_err, 2)


    #@unittest.expectedFailure
    def test_not_setup_env(self):

        date1 = float(self.start_time) + 3.77
        model = wmm_calc()
        user_time = np.array([date1])
        model.setup_time(dyear=user_time)

        try:
            x = model.get_Bx()
        except TypeError as e:
            self.assertEqual(str(e), "Coordinates haven't set up yet. Please use setup_env() to set up coordinates first.")




    def test_wmm_altitude_warning(self):
        """
        It should  return Milspec warning when altitude is < -1 or altitude > 1900 km
        """

        date1 = float(self.start_time) + 2.778
        user_time = np.array([date1])

        lat = np.array([-18])
        lon = np.array([138])
        alt = np.array([-2, 3000])


        link = "\033[94mhttps://www.ncei.noaa.gov/products/world-magnetic-model/accuracy-limitations-error-model\033[0m"  # Blue color

        wmm_model = wmm_calc()
        wmm_model.setup_env(lat, lon, alt)


        with self.assertWarns(UserWarning) as w:
            wmm_model.setup_env(lat[0], lon[0], alt[0])
        self.assertEqual(str(w.warning), f"Warning: WMM will not meet MilSpec at this altitude. For more information see {link}" )

        with self.assertWarns(UserWarning) as w:
            wmm_model.setup_env(lat[0], lon[0], alt[1])
        self.assertEqual(str(w.warning), f"Warning: WMM will not meet MilSpec at this altitude. For more information see {link}" )



    def test_get_uncertainty(self):

        date1 = float(self.start_time) + 1.46
        user_time = np.array([2025.1])

        lat = np.array([-18, 20, 20])
        lon = np.array([138, 139, 140])
        alt = np.array([100, 150, 200])

        model = wmm_calc()
        model.setup_time(dyear=user_time)
        model.setup_env(lat, lon, alt)

        uncert_map = model.get_uncertainty()

        self.assertTrue(isinstance(uncert_map, dict))
        for key, value in uncert_map.items():
            self.assertIsNotNone(value)



if __name__ == '__main__':
    unittest.main()