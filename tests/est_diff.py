import os
from typing import TextIO


def estimate(file_path: str, out_fp: TextIO, mag_comp: str):

    count = -1
    diff_sum = 0
    max_diff = 0
    min_diff = 999999

    with open(file_path, "r") as inp_fp:

        for line in inp_fp:
            if count == -1:
                count += 1
                continue
            vals = line.split(",")

            diff = abs(float(vals[4]) - float(vals[5]))
            diff_sum += diff

            max_diff = max(max_diff, diff)
            min_diff = min(min_diff, diff)
            count += 1

    ave = diff_sum/16380
    out_fp.write(f"{mag_comp},{round(ave,6)},{round(max_diff,6)},{round(min_diff,6)}\n")


def main():

    diff_res_folder = "results"
    diff_res_err_folder = "results_err"


    out_file = "diff_results.csv"

    mag_component = ["x","y","z","h","f","dec", "inc"]

    N = len(mag_component)

    fp = open(out_file, "w")
    fp.write("component,ave_diff,max_diff,min_diff\n")

    for i in range(N):
        file_path = f"{diff_res_folder}/{mag_component[i]}.csv"

        if os.path.exists(file_path):
            estimate(file_path, fp, mag_component[i])

    magsv_component = ["dx", "dy", "dz", "dh", "df", "ddec", "dinc"]

    for i in range(N):
        file_path = f"{diff_res_err_folder}/{mag_component[i]}.csv"

        if os.path.exists(file_path):
            estimate(file_path, fp, magsv_component[i])


    fp.close()

if __name__=="__main__":
    main()

