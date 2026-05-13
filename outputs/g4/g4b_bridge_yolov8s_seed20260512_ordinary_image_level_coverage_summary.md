# G4 Image-Level Coverage (g4b_bridge_yolov8s_seed20260512_ordinary)

Generated: 2026-05-13 22:13, local time

Source predictions: `data_processed\predictions\g4b_bridge_yolov8s_seed20260512_ordinary_predictions.csv`

This table converts prediction-row thresholding into an image-trigger proxy. It is closer to review workload than prediction-row coverage, but it is still not an agency work-order, road-segment, cost, or safety model.

| Threshold | Selected images | Image review coverage | Selected-image TP rate | Selected-image FP flag rate | GT-image recall proxy |
|---:|---:|---:|---:|---:|---:|
| 0.000 | 560 | 1.000000 | 0.928571 | 1.000000 | 0.928571 |
| 0.050 | 544 | 0.971429 | 0.768382 | 0.988971 | 0.746429 |
| 0.100 | 485 | 0.866071 | 0.701031 | 0.923711 | 0.607143 |
| 0.200 | 283 | 0.505357 | 0.713781 | 0.646643 | 0.360714 |
| 0.500 | 41 | 0.073214 | 0.878049 | 0.317073 | 0.064286 |

## Definitions

- Image review coverage: fraction of validation images with at least one accepted prediction at the threshold.
- Selected-image TP rate: among selected images, fraction with at least one accepted true-positive prediction.
- Selected-image FP flag rate: among selected images, fraction with at least one accepted false-positive prediction.
- GT-image recall proxy: fraction of ground-truth-positive images with at least one accepted true-positive prediction.

## Boundary

This is a post-processing workload proxy from existing prediction exports. It does not validate road-agency review cost, road-segment prioritization, or safety thresholds.
