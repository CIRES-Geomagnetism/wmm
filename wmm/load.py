import copy
import os
from typing import Optional
import numpy as np
from geomaglib import sh_loader, util


def load_wmm_coef(filename: str) -> dict:
    """
    Takes a coefficient filename of WMM or path and gives you back a dictionary with the
    components in arrays under the keys g,h,g_sv, and h_sv

    Parameters:
    filename (string): The relative path or just the name of the coefficient file

    Returns:
    dictionary: The dictionary loaded with g, h, g_sv, h_sv arrays under those keys
    """

    coef_dict = sh_loader.load_coef(filename, skip_two_columns=True)


    # Update the header of WMM in coef_dict
    fp = open(filename, "r")
    for line in fp:

        split = line.split()
        coef_dict["epoch"] = int(float(split[0]))

        if ('/' in split[2]):  # modern WMM where second value is mm/dd/yyyy
            date_string = split[2]

            month, day, year = map(int, date_string.split('/'))
            month = np.array([month])
            day = np.array([day])
            year = np.array([year])
            coef_dict["min_year"] = util.calc_dec_year(year, month, day)
            coef_dict["min_date"] = str(f"{year}-{month}-{day}")
            # print(f"Month: {month}, Day: {day}, Year: {year}")
        elif ('/' in split[3]):  # Old WMM with second value being decimal year
            date_string = split[3]

            month, day, year = map(int, date_string.split('/'))
            month = np.array([month])
            day = np.array([day])
            year = np.array([year])

            coef_dict["min_year"] = float(split[2])
            year, month, day, hour, minute = util.decimalYearToDateTime(float(split[2]))

            coef_dict["min_date"] = str(f"{year}-{month}-{day} {hour}:{minute}")
        else:
            raise ValueError(
                f"Header line of WMM.COF file should have form: 2025.0           WMM              11/13/2024")

        break

    fp.close()

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