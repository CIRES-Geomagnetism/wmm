import os
import shutil
from math import fabs
from wmm.build import wmm_calc
import numpy as np
from est_diff import estimate


def write_diff_results(file_path, inputs, true_v, pred_v):

    results_str = (",").join(inputs)


    if os.path.isfile(file_path):
        with open(file_path, "a") as f:
            f.write(f"{results_str},{true_v},{pred_v} \n")
    else:
        with open(file_path, "w") as f:
            f.write("date,lat,lon,alt,predict,true\n")
            f.write(f"{results_str},{true_v},{pred_v} \n")


def check_base_results(res_map, index, lat, lon, alt, dyear, dec, inc, h, x, y, z, f, tol, folder_path):

    inputs = [str(dyear), str(lat), str(lon), str(alt)]



    if (fabs(res_map["x"][index] - x) > tol):
        filename = f"{folder_path}/x.csv"
        write_diff_results(filename, inputs, res_map['x'][index], x)
    if (fabs(res_map["y"][index] - y) > tol):
        filename = f"{folder_path}/y.csv"
        write_diff_results(filename, inputs, res_map['y'][index], y)
    if (fabs(res_map["z"][index] - z) > tol):
        filename = f"{folder_path}/z.csv"
        write_diff_results(filename, inputs, res_map['z'][index], z)
    if (fabs(res_map["h"][index] - h) > tol):
        filename = f"{folder_path}/h.csv"
        write_diff_results(filename, inputs, res_map['h'][index], h)
    if (fabs(res_map["f"][index] - f) > tol):
        filename = f"{folder_path}/f.csv"
        write_diff_results(filename, inputs, res_map['f'][index], f)
    if (fabs(res_map["dec"][index] - dec) > tol):
        filename = f"{folder_path}/dec.csv"
        write_diff_results(filename, inputs, res_map['dec'][index], dec)
    if (fabs(res_map["inc"][index] - inc) > tol):
        filename = f"{folder_path}/inc.csv"
        write_diff_results(filename, inputs, res_map['inc'][index], inc)


def check_sv_results(res_map, index, lat, lon, alt, dyear, dec, inc, h, x, y, z, f, tol, folder_path):

    inputs = [str(dyear), str(lat), str(lon), str(alt)]
    if (fabs(res_map["dx"][index] - x) > tol):
        filename = f"{folder_path}/x.csv"
        write_diff_results(filename, inputs, res_map['dx'][index], x)
    if (fabs(res_map["dy"][index] - y) > tol):
        filename = f"{folder_path}/y.csv"
        write_diff_results(filename, inputs, res_map['dy'][index], y)
    if (fabs(res_map["dz"][index] - z) > tol):
        filename = f"{folder_path}/z.csv"
        write_diff_results(filename, inputs, res_map['dz'][index], z)
    if (fabs(res_map["dh"][index] - h) > tol):
        filename = f"{folder_path}/h.csv"
        write_diff_results(filename, inputs, res_map['dh'][index], h)
    if (fabs(res_map["df"][index] - f) > tol):
        filename = f"{folder_path}/f.csv"
        write_diff_results(filename, inputs, res_map['df'][index], f)
    if (fabs(res_map["ddec"][index] / 60 - dec) > tol):
        filename = f"{folder_path}/dec.csv"
        write_diff_results(filename, inputs, res_map['ddec'][index] / 60, dec)
    if (fabs(res_map["dinc"][index] / 60 - inc) > tol):
        filename = f"{folder_path}/inc.csv"
        write_diff_results(filename, inputs, res_map['dinc'][index] / 60, inc)


def refer_testValues(testval_filename: str) -> tuple[np.array, np.array, np.array, np.array]:

    dyears, alts, lats, lons = [], [], [], []
    with open(testval_filename, "r") as fp:

        for line in fp:
            vals = line.split()

            if vals[0] == "#":
                continue
            else:
                for i in range(len(vals)):
                    vals[i] = float(vals[i])
                dyear, alt, lat, lon = vals[0], vals[1], vals[2], vals[3]

                dyears.append(dyear)
                lats.append(lat)
                lons.append(lon)
                alts.append(alt)

    dyears = np.array(dyears)
    lats = np.array(lats)
    lons = np.array(lons)
    alts = np.array(alts)

    return dyears, lats, lons, alts


def compare_single_results(testval_filename, dyears, lats, lons, alts, res_folder, reserr_folder):

    wmm_model = wmm_calc()

    wmm_model.setup_time(dyear=dyears)
    wmm_model.setup_env(lats, lons, alts)
    tol = 1e-6
    index = 0

    with open(testval_filename, "r") as fp:

        for line in fp:
            vals = line.split()

            if vals[0] == "#":
                continue
            else:
                for i in range(len(vals)):
                    vals[i] = float(vals[i])
                dyear, alt, lat, lon = vals[0], vals[1], vals[2], vals[3]
                dec, inc, h, x, y, z, f = vals[4], vals[5], vals[6], vals[7], vals[8], vals[9], vals[10]
                ddec, dinc, dh, dx, dy, dz, df = vals[11], vals[12], vals[13], vals[14], vals[15], vals[16], vals[17]

                map = wmm_model.get_all()

                check_base_results(map, index, lat, lon, alt, dyear, dec, inc, h, x, y, z, f, tol, res_folder)
                check_sv_results(map, index, lat, lon, alt, dyear, ddec, dinc, dh, dx, dy, dz, df, tol, reserr_folder)

                index += 1






def main():
    testval_filename = "WMM2025_FINAL_TEST_VALUES_HIGHPREC.txt"
    res_folder="results"
    reserr_folder="results_err"
    out_file = "diff_results.csv"
    mag_component = ["x", "y", "z", "h", "f", "dec", "inc"]
    magsv_component = ["dx", "dy", "dz", "dh", "df", "ddec", "dinc"]
    tol = 0.06

    topdir = os.path.dirname(os.path. dirname(__file__))
    testval_path = os.path.join(topdir, "tests", testval_filename)

    if os.path.isdir(res_folder):
        shutil.rmtree(res_folder)

    os.mkdir(res_folder)

    if os.path.isdir(reserr_folder):
        shutil.rmtree(reserr_folder)

    os.mkdir(reserr_folder)

    dyears, lats, lons, alts = refer_testValues(testval_filename)
    compare_single_results(testval_path, dyears, lats, lons, alts, res_folder, reserr_folder)

    N = len(mag_component)
    fp = open(out_file, "w")
    fp.write("component,ave_diff,max_diff,min_diff\n")

    for i in range(N):
        file_path = f"{res_folder}/{mag_component[i]}.csv"

        if os.path.exists(file_path):
            estimate(file_path, fp, mag_component[i], tol)

    for i in range(N):
        file_path = f"{reserr_folder}/{mag_component[i]}.csv"

        if os.path.exists(file_path):
            estimate(file_path, fp, magsv_component[i], tol)

    fp.close()


if __name__ == "__main__":
    main()
