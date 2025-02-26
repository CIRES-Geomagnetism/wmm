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



        self.year = np.array([2025, 2026]).astype(int)
        self.month = np.array([12, 1]).astype(int)
        self.day = np.array([6, 15]).astype(int)

        self.dyears = np.array([2025.5, 2026.6])

        self.top_dir = os.path.dirname(os.path.dirname(__file__))
        self.wmm_file = os.path.join(self.top_dir, "wmm", "coefs", "WMM.COF")

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



        nmax_cases = [1, 5.0, 10, 11]
        print("here")


        for nmax in nmax_cases:
            print(f'doing test case {nmax}')
            model = wmm_calc(nmax)
            model.setup_time(dyear = 2025.5 + 0.1*nmax)
            num_elements = sh_loader.calc_sh_degrees_to_num_elems(nmax)
            self.assertEqual(len(model.coef_dict["g"]), num_elements + 1)
            self.assertEqual(nmax, model.nmax)
            model.setup_env(lat = 5, lon = 5, alt = 0)
            print(f"Get_all output of nmax = {nmax}",model.get_all())


        nmax_cases = [0, 13, 12.9]
        for nmax in nmax_cases:
            try:
                model = wmm_calc(nmax)
                model.setup_max_degree(nmax)
                model.setup_time(dyear = 2025.5 + 0.1*nmax)
            except ValueError as e:
                self.assertEqual(str(e), f"The degree is not available. Please assign the degree > 0 and degree <= 12.")




    def test_setup_dtime_arr(self):

        model = wmm_calc()
        dyears = np.array([2025.5, 2026.6])

        model.setup_env(self.lats, self.lons, self.alts)
        model.setup_time(dyear=self.dyears)

        for i in range(len(dyears)):
            self.assertAlmostEqual(self.dyears[i], model.dyear[i], places=1)


    def test_setup_dtime_tuple(self):

        model = wmm_calc()
        dyears = (2025.5, 2026.6)

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

        model = wmm_calc()
        years = np.array([2025, 2026])
        months = np.array([10,11]).astype(int)
        days = np.array([1,2]).astype(int)



        model.setup_env(self.lats[:2], self.lons[:2], self.alts[:2])
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

        model.setup_env(self.lats, self.lons, self.alts)

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



        alt_true = util.alt_to_ellipsoid_height(self.alts, self.lats, self.lons)
        r, theta = util.geod_to_geoc_lat(self.lats, alt_true)




        wmm_model = wmm_calc()
        wmm_model.setup_env(self.lats, self.lons, self.alts, msl=False)
        wmm_model.setup_time(dyear=self.dyears)

        for i in range(len(self.lats)):
            self.assertAlmostEqual(wmm_model.lat[i], self.lats[i], places=6)

            self.assertAlmostEqual(wmm_model.theta[len(self.lats) - 1], theta[len(self.lats) - 1], places=6)


    def test_to_km(self):

        wmm_model = wmm_calc()
        wmm_model.setup_env(self.lats, self.lons, self.alts, msl=False, unit="m")
        wmm_model.setup_time(2025, 1, 1)

        for i in range(len(self.alts)):
            self.assertAlmostEqual(self.alts[i]*1000, wmm_model.alt[i], places=6)





    def test_forward_base(self):


        wmm_model = wmm_calc()

        wmm_model.setup_time(dyear=self.dyears)
        wmm_model.setup_env(self.lats, self.lons, self.alts, msl=False)



        Bx, By, Bz = wmm_model.forward_base()

        for i in range(len(self.Bx)):
            self.assertAlmostEqual(Bx[i], self.Bx[i], delta=0.05)
            self.assertAlmostEqual(By[i], self.By[i], delta=0.05)
            self.assertAlmostEqual(Bz[i], self.Bz[i], delta=0.05)

    def test_setup_sv(self):

        lat = np.array([-18])
        lon = np.array([138])
        alt = np.array([77])

        dec_year = np.array([2029.5])

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


        wmm_model = wmm_calc()

        wmm_model.setup_time(dyear=self.dyears)
        wmm_model.setup_env(self.lats, self.lons, self.alts, msl=False)


        map = wmm_model.get_all()

        for i in range(len(self.dBdec)):
            self.assertAlmostEqual(map["ddec"][i] , self.dBdec[i], delta=0.05)
            self.assertAlmostEqual(map["dinc"][i] , self.dBinc[i], delta=0.05)

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



    def test_correct_time(self):



        user_time = np.array([2030.0, 2014.7])

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

        user_time = np.array([2025.1])
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

        user_time = np.array([2025.1])

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

        user_time = np.array([2025.1])

        lat = np.array([-18, 20, 20])
        lon = np.array([138, 139, 140])
        alt = np.array([100, 150, 200])

        model = wmm_calc()
        model.setup_time(dyear=user_time)
        model.setup_env(lat, lon, alt)

        print(model.get_uncertainty())




    def test_readme1(self):

        model = wmm_calc()
        lat = [80.,  0., 80.]
        lon = [  0., 120.,   0.]
        alt = [0., 0., 0.]

        #year = [2025, 2026]
        #month = [12, 1]
        #day = [6, 15]
        dyear = [2025.,  2025.,  2027.5]

        # set up time
        #model.setup_time(year, month, day)
        model.setup_time(dyear=dyear)
        # set up the coordinates
        model.setup_env(lat, lon, alt)

        print(model.get_uncertainty())

    def test_readme2(self):

        model = wmm_calc()
        lat = [23.35, 24.5]
        lon = [40, 45]
        alt = [21, 21]

        year = [2025, 2026]
        month = [12, 1]
        day = [6, 15]

        # set up time
        model.setup_time(year, month, day)
        # set up the coordinates
        model.setup_env(lat, lon, alt)

        print(model.get_all())
        print(model.get_uncertainty())





if __name__ == '__main__':
    unittest.main()