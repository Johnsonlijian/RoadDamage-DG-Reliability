# G4 Image-Level Coverage (g4a_r08_repeat_yolov8n_seed20260514_lodo_all)

Generated: 2026-05-13 20:52, local time

Source predictions: `data_processed\predictions\g4a_r08_repeat_yolov8n_seed20260514_lodo_all_predictions.csv`

This table converts prediction-row thresholding into an image-trigger proxy. It is closer to review workload than prediction-row coverage, but it is still not an agency work-order, road-segment, cost, or safety model.

| Threshold | Selected images | Image review coverage | Selected-image TP rate | Selected-image FP flag rate | GT-image recall proxy |
|---:|---:|---:|---:|---:|---:|
| 0.000 | 560 | 1.000000 | 0.807143 | 1.000000 | 0.807143 |
| 0.050 | 455 | 0.812500 | 0.413187 | 0.971429 | 0.335714 |
| 0.100 | 300 | 0.535714 | 0.380000 | 0.926667 | 0.203571 |
| 0.200 | 156 | 0.278571 | 0.358974 | 0.839744 | 0.100000 |
| 0.500 | 32 | 0.057143 | 0.437500 | 0.750000 | 0.025000 |

## Definitions

- Image review coverage: fraction of validation images with at least one accepted prediction at the threshold.
- Selected-image TP rate: among selected images, fraction with at least one accepted true-positive prediction.
- Selected-image FP flag rate: among selected images, fraction with at least one accepted false-positive prediction.
- GT-image recall proxy: fraction of ground-truth-positive images with at least one accepted true-positive prediction.

## Boundary

This is a post-processing workload proxy from existing prediction exports. It does not validate road-agency review cost, road-segment prioritization, or safety thresholds.
