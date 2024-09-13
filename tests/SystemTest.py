from math import fabs
from wmm.build import model

def check_base_results(res_map, lat, lon, alt, dyear, dec, inc, h, x, y, z, f, tol, res_fp):

    if (fabs(round(res_map["x"], 1) - x) > tol):
        res_fp.write(f"x,{lat},{lon},{alt},{dyear},{res_map['x']},{x}\n")
        print(f"x,{lat},{lon},{alt},{dyear},{res_map['x']},{x}\n")
    if (fabs(round(res_map["y"], 1) - y) > tol):
        res_fp.write(f"y,{lat},{lon},{alt},{dyear},{res_map['y']},{y}\n")
    if (fabs(round(res_map["z"], 1) - z) > tol):
        res_fp.write(f"z,{lat},{lon},{alt},{dyear},{res_map['z']},{z}\n")
    if (fabs(round(res_map["h"], 1) - h) > tol):
        res_fp.write(f"h,{lat},{lon},{alt},{dyear},{res_map['h']},{h}\n")
    if (fabs(round(res_map["f"], 1) - f) > tol):
        res_fp.write(f"f,{lat},{lon},{alt},{dyear},{res_map['f']},{f}\n")
    if (fabs(round(res_map["dec"], 2) - dec) > tol):
        res_fp.write(f"dec,{lat},{lon},{alt},{dyear},{res_map['dec']},{dec}\n")
    if (fabs(round(res_map["inc"], 2) - inc) > tol):
        res_fp.write(f"inc,{lat},{lon},{alt},{dyear},{res_map['inc']},{inc}\n")

def check_sv_results(res_map, lat, lon, alt, dyear, dec, inc, h, x, y, z, f, tol, res_fp):

    if (fabs(round(res_map["dx"], 1) - x) > tol):
        res_fp.write(f"x,{lat},{lon},{alt},{dyear},{res_map['dx']},{x}\n")
        print(f"x,{lat},{lon},{alt},{dyear},{res_map['dx']},{x}\n")
    if (fabs(round(res_map["dy"], 1) - y) > tol):
        res_fp.write(f"y,{lat},{lon},{alt},{dyear},{res_map['dy']},{y}\n")
    if (fabs(round(res_map["dz"], 1) - z) > tol):
        res_fp.write(f"z,{lat},{lon},{alt},{dyear},{res_map['dz']},{z}\n")
    if (fabs(round(res_map["dh"], 1) - h) > tol):
        res_fp.write(f"h,{lat},{lon},{alt},{dyear},{res_map['dh']},{h}\n")
    if (fabs(round(res_map["df"], 1) - f) > tol):
        res_fp.write(f"f,{lat},{lon},{alt},{dyear},{res_map['df']},{f}\n")
    if (fabs(round(res_map["ddec"], 1) - dec) > tol):
        res_fp.write(f"dec,{lat},{lon},{alt},{dyear},{res_map['ddec']},{dec}\n")
    if (fabs(round(res_map["dinc"], 1) - inc) > tol):
        res_fp.write(f"inc,{lat},{lon},{alt},{dyear},{res_map['dinc']},{inc}\n")






def refer_testValues(testval_filename, res_filename):

    wmm_model = model()
    wmm_model._set_msl_False()
    tol = 1e-6


    res_fp = open(res_filename, "w")
    resd_filename = "delta_"+res_filename
    resd_fp = open(resd_filename, "w")


    with open(testval_filename, "r") as fp:

        for line in fp:
            vals = line.split()

            if vals[0] == "#":
                continue
            else:
                for i in range(len(vals)):
                    vals[i] = float(vals[i])
                dyear, alt, lat, lon = vals[0], vals[1], vals[2],vals[3]
                dec, inc, h, x, y, z, f = vals[4], vals[5], vals[6], vals[7], vals[8], vals[9], vals[10]
                ddec, dinc, dh, dx, dy, dz, df = vals[11], vals[12], vals[13], vals[14], vals[15], vals[16], vals[17]

                wmm_model.setup_env(lat, lon, alt, dyear=float(dyear))

                res = wmm_model.forward()

                mag_map = res.get_all()

                check_base_results(mag_map, lat, lon, alt, dyear, dec, inc, h, x, y, z, f, tol, res_fp)
                check_sv_results(mag_map, lat, lon, alt, dyear, ddec, dinc, dh, dx, dy, dz, df, tol, resd_fp)

    res_fp.close()
    resd_fp.close()

def main():
    testval_filename = "WMM2020_TEST_VALUES.txt"
    res_filename = "res.csv"
    refer_testValues(testval_filename, res_filename)

if __name__=="__main__":
    main()


