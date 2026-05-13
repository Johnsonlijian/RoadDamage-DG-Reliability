# G4 Image-Level Coverage (g4a_r08_repeat_yolov8n_seed20260513_ordinary)

Generated: 2026-05-13 20:35, local time

Source predictions: `data_processed\predictions\g4a_r08_repeat_yolov8n_seed20260513_ordinary_predictions.csv`

This table converts prediction-row thresholding into an image-trigger proxy. It is closer to review workload than prediction-row coverage, but it is still not an agency work-order, road-segment, cost, or safety model.

| Threshold | Selected images | Image review coverage | Selected-image TP rate | Selected-image FP flag rate | GT-image recall proxy |
|---:|---:|---:|---:|---:|---:|
| 0.000 | 560 | 1.000000 | 0.871429 | 1.000000 | 0.871429 |
| 0.050 | 458 | 0.817857 | 0.545852 | 0.986900 | 0.446429 |
| 0.100 | 334 | 0.596429 | 0.535928 | 0.904192 | 0.319643 |
| 0.200 | 174 | 0.310714 | 0.591954 | 0.741379 | 0.183929 |
| 0.500 | 37 | 0.066071 | 0.648649 | 0.675676 | 0.042857 |

## Definitions

- Image review coverage: fraction of validation images with at least one accepted prediction at the threshold.
- Selected-image TP rate: among selected images, fraction with at least one accepted true-positive prediction.
- Selected-image FP flag rate: among selected images, fraction with at least one accepted false-positive prediction.
- GT-image recall proxy: fraction of ground-truth-positive images with at least one accepted true-positive prediction.

## Boundary

This is a post-processing workload proxy from existing prediction exports. It does not validate road-agency review cost, road-segment prioritization, or safety thresholds.
