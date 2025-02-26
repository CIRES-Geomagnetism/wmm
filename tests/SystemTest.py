import os
import shutil
from math import fabs
import argparse
import numpy as np

from wmm.build import wmm_calc

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
    if (fabs(res_map["ddec"][index] - dec) > tol):
        filename = f"{folder_path}/dec.csv"
        write_diff_results(filename, inputs, res_map['ddec'][index], dec)
    if (fabs(res_map["dinc"][index] - inc) > tol):
        filename = f"{folder_path}/inc.csv"
        write_diff_results(filename, inputs, res_map['dinc'][index], inc)


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


def compare_all_results(testval_filename, dyears, lats, lons, alts, res_folder, reserr_folder):

    wmm_model = wmm_calc()

    wmm_model.setup_time(dyear=dyears)
    wmm_model.setup_env(lats, lons, alts)
    tol = 1e-6
    index = 0
    map = wmm_model.get_all()

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

                check_base_results(map, index, lat, lon, alt, dyear, dec, inc, h, x, y, z, f, tol, res_folder)
                check_sv_results(map, index, lat, lon, alt, dyear, ddec, dinc, dh, dx, dy, dz, df, tol, reserr_folder)

                index += 1

def get_single_results(wmm_model: wmm_calc) -> dict:

    map = {}

    map["x"] = wmm_model.get_Bx()
    map["y"] = wmm_model.get_By()
    map["z"] = wmm_model.get_Bz()
    map["h"] = wmm_model.get_Bh()
    map["f"] = wmm_model.get_Bf()
    map["dec"] = wmm_model.get_Bdec()
    map["inc"] = wmm_model.get_Binc()

    map["dx"] = wmm_model.get_dBx()
    map["dy"] = wmm_model.get_dBy()
    map["dz"] = wmm_model.get_dBz()
    map["dh"] = wmm_model.get_dBh()
    map["df"] = wmm_model.get_dBf()
    map["ddec"] = wmm_model.get_dBdec()
    map["dinc"] = wmm_model.get_dBinc()

    return map
def compare_single_results(testval_filename, dyears, lats, lons, alts, res_folder, reserr_folder):

    wmm_model = wmm_calc()

    wmm_model.setup_time(dyear=dyears)
    wmm_model.setup_env(lats, lons, alts)
    tol = 1e-6
    index = 0

    map = get_single_results(wmm_model)

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

                check_base_results(map, index, lat, lon, alt, dyear, dec, inc, h, x, y, z, f, tol, res_folder)
                check_sv_results(map, index, lat, lon, alt, dyear, ddec, dinc, dh, dx, dy, dz, df, tol, reserr_folder)

                index += 1



def main():
    testval_filename = "WMM2025_FINAL_TEST_VALUES_HIGHPREC.txt"

    parser = argparse.ArgumentParser(description="scitific tests for WMM Python api")
    parser.add_argument("--results_type", "-r", type=str, help="The results type of wmm_calc. all for wmm_calc.get_all(); single for verifying the every single outputs from wmm_calc. e.g. get_Bx(), get_By()")

    args = parser.parse_args()

    out_filename_all = "diff_results_get_all.csv"
    out_filename_single = "diff_results_get_single.csv"



    mag_component = ["x", "y", "z", "h", "f", "dec", "inc"]
    magsv_component = ["dx", "dy", "dz", "dh", "df", "ddec", "dinc"]
    tol = 0.06

    topdir = os.path.dirname(os.path. dirname(__file__))
    testval_path = os.path.join(topdir, "tests", testval_filename)
    res_folder = os.path.join(topdir, "tests", "results")
    reserr_folder = os.path.join(topdir, "tests", "results_err")

    if os.path.isdir(res_folder):
        shutil.rmtree(res_folder)

    os.mkdir(res_folder)

    if os.path.isdir(reserr_folder):
        shutil.rmtree(reserr_folder)

    os.mkdir(reserr_folder)

    dyears, lats, lons, alts = refer_testValues(testval_path)

    if args.results_type == "all":
        out_filename = out_filename_all
        compare_all_results(testval_path, dyears, lats, lons, alts, res_folder, reserr_folder)
    elif args.results_type == "single":
        out_filename = out_filename_single
        compare_single_results(testval_path, dyears, lats, lons, alts, res_folder, reserr_folder)
    else:
        print("Assign all or single to the -r flag.")
        exit(1)


    N = len(mag_component)
    topdir = os.path.dirname(os.path.dirname(__file__))


    out_path = os.path.join(topdir, "tests", out_filename)

    fp = open(out_path, "w")
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
