"""
Steinschneider Lab Group
Code last updated: 2026-09-15
Script purpose: Load one basin's forcing and streamflow data and combine them
into a single daily dataframe for calibration/simulation.
"""

from pathlib import Path

import pandas as pd


def load_basin_data(gauge_id: str, data_dir: str = "data") -> pd.DataFrame:
    """Load and combine one basin's forcing + streamflow records.

    Parameters
    ----------
    gauge_id : 8-character CAMELS gauge ID, e.g. "01439500".
    data_dir : directory containing "<gauge_id>_forcing.csv" and
        "<gauge_id>_streamflow.csv".

    Returns
    -------
    df : daily dataframe with columns [date, precip, tavg, pet, qobs].
    """
    data_dir = Path(data_dir)

    forcing = pd.read_csv(data_dir / f"{gauge_id}_forcing.csv", parse_dates=["date"])
    streamflow = pd.read_csv(data_dir / f"{gauge_id}_streamflow.csv", parse_dates=["date"])

    # CAMELS forcing occasionally carries a -999 missing-data sentinel; drop
    # those days before calibration.
    forcing = forcing[forcing["precip"] >= 0].reset_index(drop=True)
    streamflow = streamflow.reset_index(drop=True)

    n = len(forcing)
    combined = pd.concat([forcing, streamflow["qobs"].iloc[:n].reset_index(drop=True)], axis=1)
    return combined
