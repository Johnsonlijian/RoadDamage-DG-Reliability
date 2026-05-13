# G4 Image-Level Coverage (g4a_r08_repeat_yolov8n_seed20260514_ordinary)

Generated: 2026-05-13 20:52, local time

Source predictions: `data_processed\predictions\g4a_r08_repeat_yolov8n_seed20260514_ordinary_predictions.csv`

This table converts prediction-row thresholding into an image-trigger proxy. It is closer to review workload than prediction-row coverage, but it is still not an agency work-order, road-segment, cost, or safety model.

| Threshold | Selected images | Image review coverage | Selected-image TP rate | Selected-image FP flag rate | GT-image recall proxy |
|---:|---:|---:|---:|---:|---:|
| 0.000 | 560 | 1.000000 | 0.855357 | 1.000000 | 0.855357 |
| 0.050 | 466 | 0.832143 | 0.542918 | 0.980687 | 0.451786 |
| 0.100 | 331 | 0.591071 | 0.558912 | 0.939577 | 0.330357 |
| 0.200 | 208 | 0.371429 | 0.572115 | 0.860577 | 0.212500 |
| 0.500 | 43 | 0.076786 | 0.651163 | 0.558140 | 0.050000 |

## Definitions

- Image review coverage: fraction of validation images with at least one accepted prediction at the threshold.
- Selected-image TP rate: among selected images, fraction with at least one accepted true-positive prediction.
- Selected-image FP flag rate: among selected images, fraction with at least one accepted false-positive prediction.
- GT-image recall proxy: fraction of ground-truth-positive images with at least one accepted true-positive prediction.

## Boundary

This is a post-processing workload proxy from existing prediction exports. It does not validate road-agency review cost, road-segment prioritization, or safety thresholds.
