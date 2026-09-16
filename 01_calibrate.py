"""
Steinschneider Lab Group
Code last updated: 2026-09-15
Script purpose: Calibrate the lumped HBV model to one CAMELS basin via
differential evolution, mirroring the lab's real 01a_calibrate_local_hbv.py
approach at teaching scale.

Usage:
    python 01_calibrate.py <gauge_id>
"""

import sys

import numpy as np
import yaml
from scipy.optimize import differential_evolution

from src.data.loader import load_basin_data
from src.metrics.metrics import nse
from src.models.hbv import HBV_PARAM_NAMES, hbv

SPINUP_DAYS = 365


def calibrate(gauge_id: str, config_path: str = "configs/hbv_bounds.yaml") -> np.ndarray:
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    bounds_dict = cfg["bounds"]
    bounds = [tuple(bounds_dict[name]) for name in HBV_PARAM_NAMES]

    df = load_basin_data(gauge_id)
    p = df["precip"].to_numpy()
    tavg = df["tavg"].to_numpy()
    pet_base = df["pet"].to_numpy()
    qobs = df["qobs"].to_numpy()

    def objective(pars):
        qsim = hbv(pars, p, tavg, pet_base)
        score = nse(qobs[SPINUP_DAYS:], qsim[SPINUP_DAYS:])
        return -score  # DE minimizes

    result = differential_evolution(
        objective,
        bounds,
        seed=cfg["calibration"]["seed"],
        maxiter=cfg["calibration"]["maxiter"],
        popsize=cfg["calibration"]["popsize"],
        polish=True,
        disp=True,
    )

    print(f"\n{gauge_id}: calibrated NSE = {-result.fun:.3f}")
    for name, value in zip(HBV_PARAM_NAMES, result.x):
        print(f"  {name:>10s} = {value:.4f}")

    np.savetxt(f"data/{gauge_id}_params.csv", result.x, delimiter=",",
               header=",".join(HBV_PARAM_NAMES), comments="")
    return result.x


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 01_calibrate.py <gauge_id>")
        sys.exit(1)
    calibrate(sys.argv[1])
