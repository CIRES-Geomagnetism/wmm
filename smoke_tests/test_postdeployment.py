# The smoke tests is for verifying deployment
import subprocess
import pytest
import os
@pytest.mark.smoke
def test_import():
    try:
        import wmm
        import geomaglib
    except ImportError as e:
        assert False, f"Import failed: {e}"


@pytest.mark.smoke
def test_get_all_keys():

    from wmm import wmm_calc
    model = wmm_calc()
    lat = [23.35, 24.5]
    lon = [40, 45]
    alt = [21, 21]

    year = [2025, 2026]
    month = [12, 1]
    day = [6, 15]

    # set up time
    model.setup_time(year, month, day)
    # set up the coordinates
    model.setup_env(lat, lon, alt)
    map = model.get_all()

    keys = ["x", "y", "z", "h", "f", "dec", "inc", "dx", "dy", "dz", "dh", "df", "ddec", "dinc"]

    for key in keys:
        if key not in map.keys():
            assert False, f"Can't find {key} in model.get_all()"


@pytest.mark.smoke
def test_uncertainty():
    from wmm import wmm_calc

    model = wmm_calc()
    lat = [80., 0., 80.]
    lon = [0., 120., 0.]
    alt = [0., 0., 0.]
    dyear = [2025., 2025., 2027.5]

    # set up time
    model.setup_time(dyear=dyear)
    # set up the coordinates
    model.setup_env(lat, lon, alt)
    map = model.get_uncertainty()

    assert map["x_uncertainty"] == 137, "x uncertainty is not correct."
    assert map["y_uncertainty"] == 89, "y uncertainty is not correct"
    assert map["z_uncertainty"] == 141, "z uncertainty is not correct"
    assert map["h_uncertainty"] == 133, "h uncertainty is not correct"
    assert map["f_uncertainty"] == 138, "f uncertainty is not correct"
    assert map["inclination_uncertainty"] == 0.2, "inclination_uncertainty is not correct"

    ddecs = [3.98575493e-05, 6.55276509e-06, 3.99539341e-05]

    assert map["declination_uncertainty"] == pytest.approx(ddecs), "declination_uncertainty is not correct"


@pytest.mark.smoke
def test_cli_runs():

    curr_dir = os.path.dirname(__file__)
    script_path = os.path.join(curr_dir, "load_testing.py")

    results = subprocess.run(["python", script_path], capture_output=True)
    assert results.returncode == 0, "CLI did not run successfully"


