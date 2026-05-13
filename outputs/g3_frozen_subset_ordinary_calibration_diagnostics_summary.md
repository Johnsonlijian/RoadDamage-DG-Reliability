# Calibration Diagnostics Summary

Generated: 2026-05-13 18:29, local time

## Configuration

- Prediction table: `data_processed\predictions\g3_frozen_subset_ordinary_predictions.csv`
- Group fields: `domain`
- Bins: `10`
- High-confidence threshold: `0.1`

## Diagnostics

| Group | N | Precision | ECE proxy | Max bin gap | High-conf N | High-conf precision | High-conf mean conf | High-conf gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all | 151913 | 0.005411 | 0.001864 | 0.842202 | 1080 | 0.195370 | 0.214536 | 0.019165 |
| China_Drone | 20429 | 0.005825 | 0.002824 | 0.851461 | 204 | 0.250000 | 0.219186 | 0.030814 |
| China_MotorBike | 22312 | 0.006723 | 0.003226 | 0.840658 | 318 | 0.176101 | 0.264042 | 0.087942 |
| Czech_Republic | 20738 | 0.004677 | 0.001691 | 0.942411 | 127 | 0.141732 | 0.198794 | 0.057061 |
| India | 22900 | 0.004891 | 0.001706 | 0.575320 | 96 | 0.156250 | 0.184853 | 0.028603 |
| Japan | 20963 | 0.005295 | 0.001476 | 0.421102 | 75 | 0.266667 | 0.175177 | 0.091490 |
| Norway | 20938 | 0.004298 | 0.001800 | 0.561128 | 83 | 0.144578 | 0.180409 | 0.035831 |
| United_States | 23633 | 0.006051 | 0.002206 | 0.603299 | 177 | 0.220339 | 0.180306 | 0.040033 |

## Boundary

These are prediction-level calibration diagnostics for object-detection exports. They support reliability auditing, but they do not validate an operational reject option or deployment threshold.
