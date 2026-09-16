"""
Steinschneider Lab Group
Code last updated: 2026-09-15
Script purpose: Sanity checks for src/metrics/metrics.py against known
inputs/outputs -- not a stand-in for scientific validation, but enough to
catch a broken metric before it silently produces wrong scores.
"""

import numpy as np

from src.metrics.metrics import nse


def test_nse_perfect_fit():
    obs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    assert nse(obs, obs) == 1.0


def test_nse_equals_mean_is_zero():
    obs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    sim = np.full_like(obs, obs.mean())
    assert abs(nse(obs, sim)) < 1e-9


def test_nse_worse_than_mean_is_negative():
    obs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    sim = obs[::-1]  # a deliberately bad, uncorrelated "prediction"
    assert nse(obs, sim) < 0
