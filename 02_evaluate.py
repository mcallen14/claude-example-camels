"""
Steinschneider Lab Group
Code last updated: 2026-09-15
Script purpose: Simulate streamflow with a basin's calibrated HBV parameters,
score it against observations, and plot the hydrograph.

Usage:
    python 02_evaluate.py <gauge_id>
"""

import sys

import matplotlib.pyplot as plt
import numpy as np

from src.data.loader import load_basin_data
from src.metrics.metrics import nse
from src.models.hbv import hbv

SPINUP_DAYS = 365


def evaluate(gauge_id: str) -> None:
    pars = np.loadtxt(f"data/{gauge_id}_params.csv", delimiter=",", skiprows=1)

    df = load_basin_data(gauge_id)
    p = df["precip"].to_numpy()
    tavg = df["tavg"].to_numpy()
    pet_base = df["pet"].to_numpy()
    qobs = df["qobs"].to_numpy()

    qsim = hbv(pars, p, tavg, pet_base)

    score = nse(qobs[SPINUP_DAYS:], qsim[SPINUP_DAYS:])
    print(f"{gauge_id}: NSE = {score:.3f}")

    dates = df["date"].iloc[SPINUP_DAYS:]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(dates, qobs[SPINUP_DAYS:], label="Observed", color="black", linewidth=1)
    ax.plot(dates, qsim[SPINUP_DAYS:], label="Simulated", color="tab:blue", linewidth=1)
    ax.set_ylabel("Streamflow [mm/day]")
    ax.set_title(f"{gauge_id} — NSE = {score:.3f}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(f"data/{gauge_id}_hydrograph.png", dpi=150)
    print(f"Saved data/{gauge_id}_hydrograph.png")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 02_evaluate.py <gauge_id>")
        sys.exit(1)
    evaluate(sys.argv[1])
