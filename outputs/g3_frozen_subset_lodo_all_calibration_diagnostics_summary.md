# Calibration Diagnostics Summary

Generated: 2026-05-13 18:29, local time

## Configuration

- Prediction table: `data_processed\predictions\g3_frozen_subset_lodo_all_predictions.csv`
- Group fields: `domain`
- Bins: `10`
- High-confidence threshold: `0.1`

## Diagnostics

| Group | N | Precision | ECE proxy | Max bin gap | High-conf N | High-conf precision | High-conf mean conf | High-conf gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all | 141681 | 0.004581 | 0.003589 | 0.962170 | 1344 | 0.077381 | 0.303490 | 0.226109 |
| China_Drone | 21318 | 0.004691 | 0.001824 | 0.695929 | 103 | 0.174757 | 0.161579 | 0.013178 |
| China_MotorBike | 20118 | 0.006313 | 0.000298 | 0.151325 | 100 | 0.130000 | 0.156460 | 0.026460 |
| Czech_Republic | 21858 | 0.003111 | 0.018381 | 0.962170 | 818 | 0.022005 | 0.384967 | 0.362962 |
| India | 20013 | 0.003648 | 0.000317 | 0.163139 | 26 | 0.307692 | 0.156002 | 0.151690 |
| Japan | 19616 | 0.005200 | 0.001389 | 0.805543 | 129 | 0.170543 | 0.217795 | 0.047252 |
| Norway | 15318 | 0.003786 | 0.001824 | 0.571945 | 79 | 0.088608 | 0.171275 | 0.082667 |
| United_States | 23440 | 0.005162 | 0.001280 | 0.493121 | 89 | 0.202247 | 0.168724 | 0.033523 |

## Boundary

These are prediction-level calibration diagnostics for object-detection exports. They support reliability auditing, but they do not validate an operational reject option or deployment threshold.
