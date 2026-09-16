# CAMELS HBV Quickstart

A small teaching sandbox for learning to use **Claude Code** on real scientific
Python work — not a research project in its own right. It calibrates a lumped
HBV rainfall-runoff model to a few real CAMELS-US basins, evaluates it, and
improves it, at a scale you can run and understand end to end in a few
minutes.

This repo is deliberately separate from any lab research repository. Nothing
in it represents a real research finding — it exists purely so you can safely
practice a Claude Code workflow (investigate → plan → implement → test →
review → commit) on something real enough to be interesting.

## What's here

- `src/models/hbv.py` — a single-unit lumped HBV model (NumPy only).
- `src/data/loader.py` — loads and merges a basin's forcing + streamflow data.
- `src/metrics/metrics.py` — hydrologic performance metrics.
- `01_calibrate.py` — calibrates HBV to one basin via differential evolution.
- `02_evaluate.py` — simulates, scores, and plots a calibrated basin.
- `data/` — trimmed, real CAMELS-US forcing/streamflow data for 4 basins
  (~5 water years each, single forcing product).

## Setup

```bash
pip install -r requirements.txt
```

## Quickstart

```bash
python 01_calibrate.py 01439500
python 02_evaluate.py 01439500
pytest
```

## Data source and attribution

Forcing and streamflow data are trimmed extracts from **CAMELS-US**
(Catchment Attributes and MEteorology for Large-sample Studies). If you use
this data beyond this teaching sandbox, cite:

- Newman, A. J., et al. (2015). Development of a large-sample
  watershed-scale hydrometeorological data set for the contiguous USA: data
  set characteristics and assessment of regional variability in hydrologic
  model performance. *Hydrology and Earth System Sciences*, 19(1), 209–223.
- Addor, N., Newman, A. J., Mizukami, N., & Clark, M. P. (2017). The CAMELS
  data set: catchment attributes and meteorology for large-sample studies.
  *Hydrology and Earth System Sciences*, 21(10), 5293–5313.

*(Exact bibliographic details above should be double-checked against the
original sources before this repo is made public.)*
