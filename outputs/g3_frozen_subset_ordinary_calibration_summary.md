# Calibration And Risk-Coverage Summary

Generated: 2026-05-12 16:10, local time

## Configuration

- Prediction table: `R:\NAS_DRIVE\IMUT\1-Research_Output\1-Papers\1-In_Preparation\2026-TRC-RoadDamage-DomainGeneralization\data_processed\predictions\g3_frozen_subset_ordinary_predictions.csv`
- Bins: `10`
- Prediction rows: `151913`
- Ground-truth objects counted through TP+FN rows: `1406`

## Prediction-Level Calibration

- Expected calibration error proxy: `0.001865`

| Bin | Confidence range | N | Mean confidence | Empirical precision | Abs gap |
|---:|---|---:|---:|---:|---:|
| 0 | [0.000, 0.100] | 150833 | 0.005658 | 0.004051 | 0.001607 |
| 1 | [0.100, 0.200] | 680 | 0.136714 | 0.129412 | 0.007302 |
| 2 | [0.200, 0.300] | 199 | 0.241159 | 0.291457 | 0.050299 |
| 3 | [0.300, 0.400] | 106 | 0.341404 | 0.292453 | 0.048951 |
| 4 | [0.400, 0.500] | 35 | 0.441010 | 0.314286 | 0.126725 |
| 5 | [0.500, 0.600] | 32 | 0.546836 | 0.406250 | 0.140586 |
| 6 | [0.600, 0.700] | 11 | 0.652741 | 0.363636 | 0.289105 |
| 7 | [0.700, 0.800] | 5 | 0.763255 | 0.400000 | 0.363255 |
| 8 | [0.800, 0.900] | 7 | 0.842202 | 0.000000 | 0.842202 |
| 9 | [0.900, 1.000] | 5 | 0.945522 | 0.800000 | 0.145522 |

## Risk-Coverage

| Threshold | Coverage | Accepted | Precision | Residual error | GT recall |
|---:|---:|---:|---:|---:|---:|
| 0.000000 | 1.000000 | 151913 | 0.005411 | 0.994589 | 0.584637 |
| 0.001000 | 1.000000 | 151913 | 0.005411 | 0.994589 | 0.584637 |
| 0.005000 | 0.272570 | 41407 | 0.017920 | 0.982080 | 0.527738 |
| 0.010000 | 0.126487 | 19215 | 0.033620 | 0.966380 | 0.459459 |
| 0.025000 | 0.043347 | 6585 | 0.073349 | 0.926651 | 0.343528 |
| 0.050000 | 0.018208 | 2766 | 0.127260 | 0.872740 | 0.250356 |
| 0.100000 | 0.007109 | 1080 | 0.195370 | 0.804630 | 0.150071 |
| 0.200000 | 0.002633 | 400 | 0.307500 | 0.692500 | 0.087482 |
| 0.300000 | 0.001323 | 201 | 0.323383 | 0.676617 | 0.046230 |
| 0.500000 | 0.000395 | 60 | 0.383333 | 0.616667 | 0.016358 |

## Boundary

This is a prediction-level calibration proxy for object detections. It supports method development and failure analysis, but paper claims require fixed G3 baselines and consistent thresholds.
