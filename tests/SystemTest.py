import os
import shutil
from math import fabs
from wmm.build import wmm_calc


def write_diff_results(file_path, inputs, true_v, pred_v):

    results_str = (",").join(inputs)


    if os.path.isfile(file_path):
        with open(file_path, "a") as f:
            f.write(f"{results_str},{true_v},{pred_v} \n")
    else:
        with open(file_path, "w") as f:
            f.write("date,lat,lon,alt,predict,true\n")
            f.write(f"{results_str},{true_v},{pred_v} \n")


def check_base_results(res_map, lat, lon, alt, dyear, dec, inc, h, x, y, z, f, tol, folder_path):

    inputs = [str(dyear), str(lat), str(lon), str(alt)]
    if (fabs(res_map["x"] - x) > tol):
        filename = f"{folder_path}/x.csv"
        write_diff_results(filename, inputs, res_map['x'], x)
    if (fabs(res_map["y"] - y) > tol):
        filename = f"{folder_path}/y.csv"
        write_diff_results(filename, inputs, res_map['y'], y)
    if (fabs(res_map["z"] - z) > tol):
        filename = f"{folder_path}/z.csv"
        write_diff_results(filename, inputs, res_map['z'], z)
    if (fabs(res_map["h"] - h) > tol):
        filename = f"{folder_path}/h.csv"
        write_diff_results(filename, inputs, res_map['h'], h)
    if (fabs(res_map["f"] - f) > tol):
        filename = f"{folder_path}/f.csv"
        write_diff_results(filename, inputs, res_map['f'], f)
    if (fabs(res_map["dec"] - dec) > tol):
        filename = f"{folder_path}/dec.csv"
        write_diff_results(filename, inputs, res_map['dec'], dec)
    if (fabs(res_map["inc"] - inc) > tol):
        filename = f"{folder_path}/inc.csv"
        write_diff_results(filename, inputs, res_map['inc'], inc)


def check_sv_results(res_map, lat, lon, alt, dyear, dec, inc, h, x, y, z, f, tol, folder_path):

    inputs = [str(dyear), str(lat), str(lon), str(alt)]
    if (fabs(res_map["dx"] - x) > tol):
        filename = f"{folder_path}/x.csv"
        write_diff_results(filename, inputs, res_map['dx'], x)
    if (fabs(res_map["dy"] - y) > tol):
        filename = f"{folder_path}/y.csv"
        write_diff_results(filename, inputs, res_map['dy'], y)
    if (fabs(res_map["dz"] - z) > tol):
        filename = f"{folder_path}/z.csv"
        write_diff_results(filename, inputs, res_map['dz'], z)
    if (fabs(res_map["dh"] - h) > tol):
        filename = f"{folder_path}/h.csv"
        write_diff_results(filename, inputs, res_map['dh'], h)
    if (fabs(res_map["df"] - f) > tol):
        filename = f"{folder_path}/f.csv"
        write_diff_results(filename, inputs, res_map['df'], f)
    if (fabs(res_map["ddec"] / 60 - res_map["dec"]) > tol):
        filename = f"{folder_path}/dec.csv"
        write_diff_results(filename, inputs, res_map['ddec'] / 60, dec)
    if (fabs(res_map["dinc"] / 60 - res_map["inc"]) > tol):
        filename = f"{folder_path}/inc.csv"
        write_diff_results(filename, inputs, res_map['dinc'] / 60, inc)


def refer_testValues(testval_filename, res_folder, reserr_folder):
    wmm_model = wmm_calc()

    tol = 1e-6

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

                wmm_model.setup_time(dyear=float(dyear))
                wmm_model.setup_env(float(lat), float(lon), float(alt), msl=False)

                mag_map = wmm_model.get_all()

                check_base_results(mag_map, lat, lon, alt, dyear, dec, inc, h, x, y, z, f, tol, res_folder)
                check_sv_results(mag_map, lat, lon, alt, dyear, ddec, dinc, dh, dx, dy, dz, df, tol, reserr_folder)




def main():
    testval_filename = "WMM2025_FINAL_TEST_VALUES_HIGHPREC.txt"
    res_folder="results"
    reserr_folder="results_err"

    if os.path.isdir(res_folder):
        shutil.rmtree(res_folder)

    os.mkdir(res_folder)

    if os.path.isdir(reserr_folder):
        shutil.rmtree(reserr_folder)

    os.mkdir(reserr_folder)

    refer_testValues(testval_filename, res_folder, reserr_folder)


if __name__ == "__main__":
    main()
