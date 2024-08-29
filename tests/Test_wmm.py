import os.path
import unittest

from wmm import compute


class Test_wmm(unittest.TestCase):

    def setUp(self):

        self.top_dir = os.path.dirname(os.path.dirname(__file__))
        self.wmm_file = os.path.join(self.top_dir, "wmm", "coefs", "WMM2020.cof")
    def test_compile(self):

        lat = -18
        lon = 138
        alt = 77
        dec_year = 2024.5

        Bx, By, Bz = compute.compile(lat, lon, alt, dec_year, self.wmm_file)

        print(f"Bx: {Bx}, By: {By}, Bz:{Bz}")

        self.assertAlmostEqual(round(Bx, 1), 31722.0, delta=0.01)
        self.assertAlmostEqual(round(By, 1), 2569.6 , delta=0.01)
        self.assertAlmostEqual(round(Bz, 1), -34986.2 , delta=0.01)







if __name__ == '__main__':
    unittest.main()
