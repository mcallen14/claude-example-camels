"""
Steinschneider Lab Group
Code last updated: 2026-09-15
Script purpose: Standard hydrologic model performance metrics.
"""

import numpy as np


def nse(qobs: np.ndarray, qsim: np.ndarray) -> float:
    """Nash-Sutcliffe Efficiency. 1 = perfect, 0 = no better than the mean of
    observations, negative = worse than the mean."""
    qobs = np.asarray(qobs, dtype=float)
    qsim = np.asarray(qsim, dtype=float)
    numerator = np.sum((qobs - qsim) ** 2)
    denominator = np.sum((qobs - qobs.mean()) ** 2)
    return 1.0 - numerator / denominator
