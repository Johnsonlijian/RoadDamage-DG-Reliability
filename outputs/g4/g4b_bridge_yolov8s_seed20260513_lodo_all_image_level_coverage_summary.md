# G4 Image-Level Coverage (g4b_bridge_yolov8s_seed20260513_lodo_all)

Generated: 2026-05-13 23:20, local time

Source predictions: `data_processed\predictions\g4b_bridge_yolov8s_seed20260513_lodo_all_predictions.csv`

This table converts prediction-row thresholding into an image-trigger proxy. It is closer to review workload than prediction-row coverage, but it is still not an agency work-order, road-segment, cost, or safety model.

| Threshold | Selected images | Image review coverage | Selected-image TP rate | Selected-image FP flag rate | GT-image recall proxy |
|---:|---:|---:|---:|---:|---:|
| 0.000 | 560 | 1.000000 | 0.782143 | 1.000000 | 0.782143 |
| 0.050 | 474 | 0.846429 | 0.567511 | 0.966245 | 0.480357 |
| 0.100 | 335 | 0.598214 | 0.528358 | 0.871642 | 0.316071 |
| 0.200 | 144 | 0.257143 | 0.500000 | 0.645833 | 0.128571 |
| 0.500 | 5 | 0.008929 | 0.600000 | 0.400000 | 0.005357 |

## Definitions

- Image review coverage: fraction of validation images with at least one accepted prediction at the threshold.
- Selected-image TP rate: among selected images, fraction with at least one accepted true-positive prediction.
- Selected-image FP flag rate: among selected images, fraction with at least one accepted false-positive prediction.
- GT-image recall proxy: fraction of ground-truth-positive images with at least one accepted true-positive prediction.

## Boundary

This is a post-processing workload proxy from existing prediction exports. It does not validate road-agency review cost, road-segment prioritization, or safety thresholds.
