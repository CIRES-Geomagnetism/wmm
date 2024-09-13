import os
from geomaglib import sh_loader

def load_wmm_coef(filename, skip_two_columns=False, load_sv=True, end_degree=None, load_year=None):
    """
    Takes a coefficient filename or path and gives you back a dictionary with the
    components in arrays under the keys g,h,g_sv, and h_sv

    Parameters:
    filename (string): The relative path or just the name of the coefficient file
    skip_two_columns (boolean): Sometimes the coefficient file in the data lines
    lists the spherical harmonic degree numbers in the first two columns like in
    WMM and IGRF. If this parameter is true it lets the function know to skip those
    two columns
    load_sv (boolean): The coefficient file doesn't always have sv columns like
    in HDGM crust,set this false to let the function know to not load g_sv and h_sv
    end_degree (int): If you just want to load a specific amount of spherical harmonic
    degrees from the coefficient file set this to that number. Set it to None if
    you wish to ignore
    load_year (int): The coefficient file could be seperated by year components like
    in HDGM core, set this to a year value based on what year you want to be loaded.
    Set it to None if you wish to ignore this parameter

    Returns:
    dictionary: The dictionary loaded with g, h, g_sv, h_sv arrays under those keys
    """
    coef_dict = {"g": [], "h": []}
    if load_sv:
        coef_dict["g_sv"] = []
        coef_dict["h_sv"] = []

    skip_adder = 0
    if skip_two_columns:
        skip_adder = 2

    coef_file = open(filename, 'r')
    lines = coef_file.readlines()

    header_line = True
    load = True
    footer_line_split_len = 4
    if not load_sv:
        footer_line_split_len = 2
    if load_year is not None:
        load = False
    num_lines_load = None
    load_counter = 0
    if end_degree is not None:
        num_lines_load = sh_loader.calc_sh_degrees_to_num_elems(end_degree)
    for line in lines:
        split = line.split()
        # This will detect the footer and we can stop loading
        if len(split) < footer_line_split_len:
            break

        if load_year is not None and split[1] == (str(load_year) + ".0"):
            load = True
            header_line = False
            coef_dict["epoch"] = float(split[1])
            continue
        if load_year is not None and split[1] == (str(load_year + 1) + ".0"):
            break
        if header_line:
            header_line = False
            if load_sv:
                coef_dict["epoch"] = float(split[0])
            coef_dict["min_year"] = float(split[2])
            coef_dict["min_date"] = str(split[3])
            continue
        if num_lines_load is not None and load_counter >= num_lines_load:
            break
        if load:
            load_counter = load_counter + 1
            coef_dict['g'].append(float(split[0 + skip_adder]))
            coef_dict['h'].append(float(split[1 + skip_adder]))
            if load_sv:
                coef_dict['g_sv'].append(float(split[2 + skip_adder]))
                coef_dict['h_sv'].append(float(split[3 + skip_adder]))

    coef_file.close()

    if len(coef_dict["g"]) > 0 and (coef_dict["g"][0] != 0 or coef_dict['h'][0] != 0):
        coef_dict["g"].insert(0, 0)
        coef_dict["h"].insert(0, 0)
        if load_sv:
            coef_dict["g_sv"].insert(0, 0)
            coef_dict["h_sv"].insert(0, 0)

    if end_degree is not None and len(coef_dict["g"]) > num_lines_load:
        coef_dict["g"].pop()
        coef_dict["h"].pop()
        if load_sv:
            coef_dict["g_sv"].pop()
            coef_dict["h_sv"].pop()

    return coef_dict
