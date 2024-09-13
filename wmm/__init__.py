import os
from . import load

COEFS_FILE="WMM2020.cof"

def get_wmmcoefs_path(filename):

    currdir = os.path.dirname(__file__)

    coef_file = os.path.join(currdir, "coefs", filename)

    return coef_file

wmm_coeffs = get_wmmcoefs_path(COEFS_FILE)
print(f"path :{wmm_coeffs}")
coef_dict = load.load_wmm_coef(wmm_coeffs, skip_two_columns=True)