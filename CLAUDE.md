## Project Purpose

A small teaching sandbox for practicing Claude Code workflows on real
scientific Python work. It calibrates a lumped HBV rainfall-runoff model to a
few real CAMELS-US basins and evaluates it. Nothing here is a real research
result — see `README.md`.

---

## Data

```text
data/<gauge_id>_forcing.csv      date, precip [mm/day], tavg [degC], pet [mm/day]
data/<gauge_id>_streamflow.csv   date, qobs [mm/day]
```

Gauge IDs are always 8-character zero-padded strings (e.g. `"01439500"`),
matching the standard USGS/CAMELS convention.

Do not modify the files in `data/` — they are trimmed extracts from real
CAMELS-US records and are treated as read-only inputs.

---

## HBV Model

`src/models/hbv.py` implements a single-unit lumped HBV model. PET is supplied
externally as a pre-computed base value and scaled by a calibrated
coefficient:

```text
actual_PET = coeff_pet * pet_base
```

`coeff_pet` is one of the 20 calibrated HBV parameters (bounds in
`configs/hbv_bounds.yaml`) — it is not hardcoded, and it is the only knob
that scales PET.

Correct:
```text
potevap = coeff_pet * pet_base
```
Incorrect:
```text
potevap = coeff_pet + pet_base
```

---

## Coding Guidelines

- Config-driven parameter bounds (`configs/hbv_bounds.yaml`) — never hardcode
  calibration bounds directly in a script.
- Reuse `src/data/loader.py`'s `load_basin_data()` rather than reading a
  basin's forcing/streamflow files directly in a new script.
- Any change to `src/models/hbv.py`'s equations must be checked against the
  documented `actual_PET = coeff_pet * pet_base` convention above, and against
  a known-good NSE score for at least one basin — a change that still "runs"
  is not evidence it is still correct.

---

## Development Rules for Claude

Every Python script in this repo must begin with this header in its
docstring, with the date updated on modification:

```text
Steinschneider Lab Group
Code last updated: YYYY-MM-DD
Script purpose:
```
