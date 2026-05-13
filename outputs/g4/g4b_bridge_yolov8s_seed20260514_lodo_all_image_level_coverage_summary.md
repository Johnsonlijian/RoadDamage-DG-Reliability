# G4 Image-Level Coverage (g4b_bridge_yolov8s_seed20260514_lodo_all)

Generated: 2026-05-14 00:25, local time

Source predictions: `data_processed\predictions\g4b_bridge_yolov8s_seed20260514_lodo_all_predictions.csv`

This table converts prediction-row thresholding into an image-trigger proxy. It is closer to review workload than prediction-row coverage, but it is still not an agency work-order, road-segment, cost, or safety model.

| Threshold | Selected images | Image review coverage | Selected-image TP rate | Selected-image FP flag rate | GT-image recall proxy |
|---:|---:|---:|---:|---:|---:|
| 0.000 | 560 | 1.000000 | 0.850000 | 1.000000 | 0.850000 |
| 0.050 | 497 | 0.887500 | 0.627767 | 0.971831 | 0.557143 |
| 0.100 | 371 | 0.662500 | 0.614555 | 0.924528 | 0.407143 |
| 0.200 | 183 | 0.326786 | 0.590164 | 0.710383 | 0.192857 |
| 0.500 | 4 | 0.007143 | 1.000000 | 0.250000 | 0.007143 |

## Definitions

- Image review coverage: fraction of validation images with at least one accepted prediction at the threshold.
- Selected-image TP rate: among selected images, fraction with at least one accepted true-positive prediction.
- Selected-image FP flag rate: among selected images, fraction with at least one accepted false-positive prediction.
- GT-image recall proxy: fraction of ground-truth-positive images with at least one accepted true-positive prediction.

## Boundary

This is a post-processing workload proxy from existing prediction exports. It does not validate road-agency review cost, road-segment prioritization, or safety thresholds.
