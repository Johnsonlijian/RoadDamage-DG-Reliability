# G4 Image-Level Coverage (g4b_bridge_yolov8s_seed20260514_ordinary)

Generated: 2026-05-14 00:25, local time

Source predictions: `data_processed\predictions\g4b_bridge_yolov8s_seed20260514_ordinary_predictions.csv`

This table converts prediction-row thresholding into an image-trigger proxy. It is closer to review workload than prediction-row coverage, but it is still not an agency work-order, road-segment, cost, or safety model.

| Threshold | Selected images | Image review coverage | Selected-image TP rate | Selected-image FP flag rate | GT-image recall proxy |
|---:|---:|---:|---:|---:|---:|
| 0.000 | 560 | 1.000000 | 0.942857 | 1.000000 | 0.942857 |
| 0.050 | 540 | 0.964286 | 0.779630 | 0.990741 | 0.751786 |
| 0.100 | 491 | 0.876786 | 0.718941 | 0.932790 | 0.630357 |
| 0.200 | 314 | 0.560714 | 0.678344 | 0.757962 | 0.380357 |
| 0.500 | 44 | 0.078571 | 0.863636 | 0.363636 | 0.067857 |

## Definitions

- Image review coverage: fraction of validation images with at least one accepted prediction at the threshold.
- Selected-image TP rate: among selected images, fraction with at least one accepted true-positive prediction.
- Selected-image FP flag rate: among selected images, fraction with at least one accepted false-positive prediction.
- GT-image recall proxy: fraction of ground-truth-positive images with at least one accepted true-positive prediction.

## Boundary

This is a post-processing workload proxy from existing prediction exports. It does not validate road-agency review cost, road-segment prioritization, or safety thresholds.
