# G4 Image-Level Coverage (g4b_bridge_yolov8s_seed20260513_ordinary)

Generated: 2026-05-13 23:20, local time

Source predictions: `data_processed\predictions\g4b_bridge_yolov8s_seed20260513_ordinary_predictions.csv`

This table converts prediction-row thresholding into an image-trigger proxy. It is closer to review workload than prediction-row coverage, but it is still not an agency work-order, road-segment, cost, or safety model.

| Threshold | Selected images | Image review coverage | Selected-image TP rate | Selected-image FP flag rate | GT-image recall proxy |
|---:|---:|---:|---:|---:|---:|
| 0.000 | 560 | 1.000000 | 0.946429 | 1.000000 | 0.946429 |
| 0.050 | 544 | 0.971429 | 0.762868 | 0.988971 | 0.741071 |
| 0.100 | 475 | 0.848214 | 0.720000 | 0.930526 | 0.610714 |
| 0.200 | 317 | 0.566071 | 0.722397 | 0.722397 | 0.408929 |
| 0.500 | 48 | 0.085714 | 0.812500 | 0.229167 | 0.069643 |

## Definitions

- Image review coverage: fraction of validation images with at least one accepted prediction at the threshold.
- Selected-image TP rate: among selected images, fraction with at least one accepted true-positive prediction.
- Selected-image FP flag rate: among selected images, fraction with at least one accepted false-positive prediction.
- GT-image recall proxy: fraction of ground-truth-positive images with at least one accepted true-positive prediction.

## Boundary

This is a post-processing workload proxy from existing prediction exports. It does not validate road-agency review cost, road-segment prioritization, or safety thresholds.
