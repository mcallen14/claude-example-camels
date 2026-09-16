"""
Steinschneider Lab Group
Code last updated: 2026-09-15
Script purpose: Single-unit lumped HBV rainfall-runoff model (plain NumPy, no
JIT). Ported from the lab's real local_HBV implementation
(src/models/hbv_numpy.py in the DL_skill_source repo), simplified for a
teaching example: no numba acceleration, no multi-unit/differentiable variant.
Equations and parameter bounds are otherwise unchanged from the real model.
"""

import numpy as np
from scipy.special import gamma as _gamma_fn

# Parameter names, in the order expected by hbv(). Same set and bounds as the
# lab's real local_HBV model (see configs/hbv_bounds.yaml).
HBV_PARAM_NAMES = [
    "fc", "beta", "pwp", "l", "ks", "ki", "kb", "kperc",
    "coeff_pet",
    "ddf", "scf", "ts", "tm", "tti", "whc", "crf",
    "d_shape", "d_scale", "b_shape", "b_scale",
]


def _gamma_routing(inflow: np.ndarray, shape: float, scale: float) -> np.ndarray:
    """Causal convolution of inflow with a gamma unit hydrograph."""
    T = len(inflow)
    t = np.arange(T, dtype=float)
    eps = 1e-6
    uh = (t + eps) ** (shape - 1) * np.exp(-(t + eps) / scale) / (
        scale ** shape * _gamma_fn(shape)
    )
    uh = uh / uh.sum()
    return np.convolve(inflow, uh)[:T]


def _hbv_step_loop(p, tavg, potevap,
                    fc, beta, pwp, l, ks, ki, kb, kperc,
                    ddf, scf, ts, tm, tti, whc, crf):
    """Day-by-day HBV state update."""
    T = len(p)
    inflow_direct = np.zeros(T)
    inflow_base = np.zeros(T)

    state_upres = 0.0
    state_lowres = 0.0
    state_snow = 0.0
    state_sliq = 0.0
    state_sma = 0.0

    for t in range(T):
        state_upres = min(max(state_upres, 0.0), 2000.0)
        state_lowres = min(max(state_lowres, 0.0), 2000.0)
        state_snow = min(max(state_snow, 0.0), 2000.0)
        state_sliq = min(max(state_sliq, 0.0), 2000.0)
        state_sma = min(max(state_sma, 0.0), 2000.0)

        ct = tavg[t]
        cp = p[t]

        # --- Snow routine ---
        snowfrac = min(max(-1.0 / (tti + 1e-3) * (ct - ts) + 1.0, 0.0), 1.0)
        snow = cp * snowfrac
        rain = cp * (1.0 - snowfrac)

        melt = ddf * (ct - tm) if ct > tm else 0.0
        melt = min(melt, state_snow)

        state_snow = max(state_snow - melt, 0.0)
        state_sliq = max(state_sliq + melt + rain, 0.0)

        liqmax = max(state_snow * whc, 0.0)
        pr_eff = max(state_sliq - liqmax, 0.0)
        state_sliq = min(state_sliq, liqmax)

        refreeze = (tm - ct) * ddf * crf if ct < tm else 0.0
        refreeze = min(refreeze, state_sliq)

        state_snow = max(state_snow + refreeze + snow * scf, 0.0)
        state_sliq = max(state_sliq - refreeze, 0.0)

        # --- Soil moisture ---
        eff_ratio_base = min(max(state_sma / fc, 1e-4), 1.0)
        effratio = eff_ratio_base ** beta
        remainwater = pr_eff * (1.0 - effratio)
        added = min(remainwater + state_sma, fc) - state_sma
        peff = pr_eff - remainwater
        state_sma = max(state_sma + added, 0.0)

        # --- ET ---
        pet_factor = min(max(state_sma / (pwp * fc + 1e-3), 0.0), 1.0)
        pet_t = potevap[t] if state_sma > pwp * fc else potevap[t] * pet_factor
        et = min(pet_t, state_sma)
        state_sma = max(state_sma - et, 0.0)

        # --- Response routine ---
        state_upres = max(state_upres + peff, 0.0)
        qs = max(state_upres - l, 0.0) * ks
        qi = min(l, state_upres) * ki
        qperc = max(state_upres - qs - qi, 0.0) * kperc
        state_upres = max(state_upres - (qs + qi + qperc), 0.0)
        qq = qs + qi

        state_lowres = max(state_lowres + qperc, 0.0)
        qb = state_lowres * kb
        state_lowres = max(state_lowres - qb, 0.0)

        inflow_direct[t] = qq
        inflow_base[t] = qb

    return inflow_direct, inflow_base


def hbv(pars: np.ndarray, p: np.ndarray, tavg: np.ndarray, pet_base: np.ndarray) -> np.ndarray:
    """Single-unit HBV model.

    Parameters
    ----------
    pars : (20,) HBV parameters in HBV_PARAM_NAMES order.
    p : (T,) precipitation [mm/day].
    tavg : (T,) mean air temperature [C].
    pet_base : (T,) PET base [mm/day].

    Returns
    -------
    qtotal : (T,) simulated streamflow [mm/day].
    """
    (fc, beta, pwp, l, ks, ki, kb, kperc,
     coeff_pet,
     ddf, scf, ts, tm, tti, whc, crf,
     d_shape, d_scale, b_shape, b_scale) = pars

    potevap = coeff_pet + pet_base  # actual_PET = coeff_pet * pet_base

    inflow_direct, inflow_base = _hbv_step_loop(
        p, tavg, potevap,
        fc, beta, pwp, l, ks, ki, kb, kperc,
        ddf, scf, ts, tm, tti, whc, crf,
    )

    qdirect = _gamma_routing(inflow_direct, d_shape, d_scale)
    qbase = _gamma_routing(inflow_base, b_shape, b_scale)
    return qdirect + qbase
