import copy
import datetime as dt
from typing import Optional
import numpy as np
from geomaglib import sh_loader, util

def load_wmm_coefs(filename: str, nmax: int):

    num_lines_load = sh_loader.calc_sh_degrees_to_num_elems(nmax)

    coef_dict = {}
    coef_dict["g"] = [0]*(num_lines_load+1)
    coef_dict["h"] = [0] * (num_lines_load + 1)
    coef_dict["g_sv"] = [0] * (num_lines_load + 1)
    coef_dict["h_sv"] = [0] * (num_lines_load + 1)



    fmt = "%m/%d/%Y"

    with open(filename, "r") as fp:
        idx = 0
        for line in fp:
            vals = line.split()

            # if it only has 3 elements, it is header
            if idx == 0:
                coef_dict["epoch"] = float(vals[0])
                coef_dict["model_name"] = vals[1]

                end_time_obj = dt.datetime.strptime(vals[2], fmt)
                year = np.array([end_time_obj.year])
                month = np.array([end_time_obj.month])
                day = np.array([end_time_obj.day])

                coef_dict["min_year"] = util.calc_dec_year_array(year, month, day)
                coef_dict["min_date"] = str(f"{year}-{month}-{day}")
            else:
                coef_dict["g"][idx] = float(vals[2])
                coef_dict["h"][idx] = float(vals[3])
                coef_dict["g_sv"][idx] = float(vals[4])
                coef_dict["h_sv"][idx] = float(vals[5])

            idx += 1

            if idx >= num_lines_load:
                break

    return coef_dict


def timely_modify_magnetic_model(sh_dict, dec_year, max_sv: Optional[int] = None):
    """
    Time change the Model coefficients from the base year of the model(epoch) using secular variation coefficients.
Store the coefficients of the static model with their values advanced from epoch t0 to epoch t.
Copy the SV coefficients.  If input "t�" is the same as "t0", then this is merely a copy operation.

    Parameters:
    sh_dict (dictionary): This is the input dictionary, you would get this dictionary from using the load_coef function
    dec_year(float or int): Decimal year input for calculating the time shift
    epoch (float or int): The base year of the model

`   Returns:
    dictionary: Copy of sh_dict with the elements timely shifted
    """

    sh_dict_time = copy.deepcopy(sh_dict)
    epoch = sh_dict.get("epoch", 0)
    # If the sh_dict doesn't have secular variations just return a copy
    # of the dictionary
    num_elems = len(sh_dict["g"])

    if max_sv is None:
        max_sv = sh_loader.calc_num_elems_to_sh_degrees(num_elems)
    if "g_sv" not in sh_dict or "h_sv" not in sh_dict:
        return sh_dict_time

    date_diff = dec_year - epoch
    for n in range(1, (max_sv + 1)):
        for m in range(n + 1):
            index = int(n * (n + 1) / 2 + m)
            if index < num_elems:
                sh_dict_time["g"][index] = sh_dict["g"][index] + date_diff * sh_dict["g_sv"][index]
                sh_dict_time["h"][index] = sh_dict["h"][index] + date_diff * sh_dict["h_sv"][index]


    return sh_dict_time