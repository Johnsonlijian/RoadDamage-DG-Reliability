# G4 Image-Level Coverage (g4b_bridge_yolov8s_seed20260512_lodo_all)

Generated: 2026-05-13 22:13, local time

Source predictions: `data_processed\predictions\g4b_bridge_yolov8s_seed20260512_lodo_all_predictions.csv`

This table converts prediction-row thresholding into an image-trigger proxy. It is closer to review workload than prediction-row coverage, but it is still not an agency work-order, road-segment, cost, or safety model.

| Threshold | Selected images | Image review coverage | Selected-image TP rate | Selected-image FP flag rate | GT-image recall proxy |
|---:|---:|---:|---:|---:|---:|
| 0.000 | 560 | 1.000000 | 0.855357 | 1.000000 | 0.855357 |
| 0.050 | 518 | 0.925000 | 0.600386 | 0.986486 | 0.555357 |
| 0.100 | 430 | 0.767857 | 0.504651 | 0.923256 | 0.387500 |
| 0.200 | 222 | 0.396429 | 0.481982 | 0.761261 | 0.191071 |
| 0.500 | 22 | 0.039286 | 0.681818 | 0.454545 | 0.026786 |

## Definitions

- Image review coverage: fraction of validation images with at least one accepted prediction at the threshold.
- Selected-image TP rate: among selected images, fraction with at least one accepted true-positive prediction.
- Selected-image FP flag rate: among selected images, fraction with at least one accepted false-positive prediction.
- GT-image recall proxy: fraction of ground-truth-positive images with at least one accepted true-positive prediction.

## Boundary

This is a post-processing workload proxy from existing prediction exports. It does not validate road-agency review cost, road-segment prioritization, or safety thresholds.
