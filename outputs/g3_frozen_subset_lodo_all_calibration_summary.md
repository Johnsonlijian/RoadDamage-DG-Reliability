# Calibration And Risk-Coverage Summary

Generated: 2026-05-12 16:11, local time

## Configuration

- Prediction table: `<local_project_root>\data_processed\predictions\g3_frozen_subset_lodo_all_predictions.csv`
- Bins: `10`
- Prediction rows: `141681`
- Ground-truth objects counted through TP+FN rows: `1326`

## Prediction-Level Calibration

- Expected calibration error proxy: `0.003588`

| Bin | Confidence range | N | Mean confidence | Empirical precision | Abs gap |
|---:|---|---:|---:|---:|---:|
| 0 | [0.000, 0.100] | 140337 | 0.005342 | 0.003884 | 0.001458 |
| 1 | [0.100, 0.200] | 742 | 0.137310 | 0.074124 | 0.063186 |
| 2 | [0.200, 0.300] | 200 | 0.243048 | 0.100000 | 0.143048 |
| 3 | [0.300, 0.400] | 99 | 0.348398 | 0.171717 | 0.176680 |
| 4 | [0.400, 0.500] | 49 | 0.450066 | 0.061224 | 0.388841 |
| 5 | [0.500, 0.600] | 46 | 0.544670 | 0.043478 | 0.501192 |
| 6 | [0.600, 0.700] | 45 | 0.648752 | 0.044444 | 0.604308 |
| 7 | [0.700, 0.800] | 36 | 0.743889 | 0.083333 | 0.660555 |
| 8 | [0.800, 0.900] | 33 | 0.859994 | 0.030303 | 0.829690 |
| 9 | [0.900, 1.000] | 94 | 0.972808 | 0.010638 | 0.962170 |

## Risk-Coverage

| Threshold | Coverage | Accepted | Precision | Residual error | GT recall |
|---:|---:|---:|---:|---:|---:|
| 0.000000 | 1.000000 | 141681 | 0.004581 | 0.995419 | 0.489442 |
| 0.001000 | 1.000000 | 141681 | 0.004581 | 0.995419 | 0.489442 |
| 0.005000 | 0.239397 | 33918 | 0.015007 | 0.984993 | 0.383861 |
| 0.010000 | 0.120341 | 17050 | 0.023578 | 0.976422 | 0.303167 |
| 0.025000 | 0.045398 | 6432 | 0.041200 | 0.958800 | 0.199849 |
| 0.050000 | 0.020864 | 2956 | 0.062246 | 0.937754 | 0.138763 |
| 0.100000 | 0.009486 | 1344 | 0.077381 | 0.922619 | 0.078431 |
| 0.200000 | 0.004249 | 602 | 0.081395 | 0.918605 | 0.036953 |
| 0.300000 | 0.002837 | 402 | 0.072139 | 0.927861 | 0.021870 |
| 0.500000 | 0.001793 | 254 | 0.035433 | 0.964567 | 0.006787 |

## Boundary

This is a prediction-level calibration proxy for object detections. It supports method development and failure analysis, but paper claims require fixed G3 baselines and consistent thresholds.
