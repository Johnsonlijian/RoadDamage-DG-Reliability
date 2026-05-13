# G4a Multi-Seed YOLOv8n Summary

Boundary: this summarizes the completed bounded subset evidence layer for YOLOv8n only. It does not establish full-scale detector performance, deployment readiness, or a calibrated referral policy.

Included seeds: 20260512 (original R08 CPU baseline treated as the first seed-level run), 20260513, and 20260514. Each seed contains one ordinary mixed-domain run and seven leave-one-domain-out runs.

## Headline Metrics

- Ordinary mixed-domain mean mAP50: 0.0831 +/- 0.0078 across 3 seeds.
- Pooled LODO-domain mean mAP50: 0.0640 +/- 0.0280 across 21 held-out-domain runs.
- Ordinary-minus-LODO mAP50 gap: 0.0191.
- Lowest mean held-out mAP50 domain: Norway (0.0103 +/- 0.0017).
- Largest across-seed held-out mAP50 spread: United_States (std 0.0255).

## Ordinary Summary

| model | epochs | imgsz | n_runs | precision_B_mean | recall_B_mean | mAP50_B_mean | mAP50_B_std | mAP50_95_B_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yolov8n.pt | 4.0000 | 320.0000 | 3.0000 | 0.1824 | 0.1687 | 0.0831 | 0.0078 | 0.0274 |

## LODO Overall Summary

| model | epochs | imgsz | n_runs | precision_B_mean | recall_B_mean | mAP50_B_mean | mAP50_B_std | mAP50_95_B_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yolov8n.pt | 4.0000 | 320.0000 | 21.0000 | 0.1859 | 0.1056 | 0.0640 | 0.0280 | 0.0210 |

## LODO By Held-Out Domain

| heldout_domain | n_runs | precision_B_mean | recall_B_mean | mAP50_B_mean | mAP50_B_std | mAP50_95_B_mean |
| --- | --- | --- | --- | --- | --- | --- |
| Norway | 3.0000 | 0.0427 | 0.0177 | 0.0103 | 0.0017 | 0.0034 |
| India | 3.0000 | 0.3266 | 0.0768 | 0.0542 | 0.0118 | 0.0188 |
| Japan | 3.0000 | 0.2047 | 0.1382 | 0.0674 | 0.0137 | 0.0234 |
| China_MotorBike | 3.0000 | 0.2087 | 0.1247 | 0.0706 | 0.0074 | 0.0181 |
| Czech_Republic | 3.0000 | 0.2637 | 0.1056 | 0.0735 | 0.0173 | 0.0231 |
| China_Drone | 3.0000 | 0.0991 | 0.1299 | 0.0760 | 0.0064 | 0.0239 |
| United_States | 3.0000 | 0.1556 | 0.1459 | 0.0961 | 0.0255 | 0.0367 |

## Calibration And Threshold Artifacts

Per-seed calibration, prediction-row risk-coverage, and image-level coverage tables were regenerated for ordinary and pooled LODO exports. Manuscript text should report these as audit diagnostics, not as calibrated deployment thresholds.

### Calibration Summary

| seed | split | n_predictions | ece_proxy | high_conf_n_predictions | high_conf_mean_confidence | high_conf_empirical_precision | high_conf_gap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 20260512.0000 | ordinary | 151913.0000 | 0.0019 | 1080.0000 | 0.2145 | 0.1954 | 0.0192 |
| 20260512.0000 | lodo_all | 141681.0000 | 0.0036 | 1344.0000 | 0.3035 | 0.0774 | 0.2261 |
| 20260513.0000 | ordinary | 154733.0000 | 0.0020 | 1128.0000 | 0.2173 | 0.1782 | 0.0391 |
| 20260513.0000 | lodo_all | 144652.0000 | 0.0021 | 728.0000 | 0.1944 | 0.1250 | 0.0694 |
| 20260514.0000 | ordinary | 158180.0000 | 0.0032 | 1657.0000 | 0.2131 | 0.1334 | 0.0797 |
| 20260514.0000 | lodo_all | 153571.0000 | 0.0025 | 955.0000 | 0.2081 | 0.1288 | 0.0793 |

### Image-Level Coverage At Selected Thresholds

| seed | split | threshold | selected_images | image_review_coverage | selected_image_tp_rate | gt_image_miss_proxy |
| --- | --- | --- | --- | --- | --- | --- |
| 20260512.0000 | ordinary | 0.0500 | 478.0000 | 0.8536 | 0.5628 | 0.5196 |
| 20260512.0000 | ordinary | 0.1000 | 349.0000 | 0.6232 | 0.5215 | 0.6750 |
| 20260512.0000 | ordinary | 0.2000 | 195.0000 | 0.3482 | 0.5692 | 0.8018 |
| 20260512.0000 | ordinary | 0.5000 | 34.0000 | 0.0607 | 0.6765 | 0.9589 |
| 20260512.0000 | lodo_all | 0.0500 | 457.0000 | 0.8161 | 0.3654 | 0.7018 |
| 20260512.0000 | lodo_all | 0.1000 | 315.0000 | 0.5625 | 0.3143 | 0.8232 |
| 20260512.0000 | lodo_all | 0.2000 | 172.0000 | 0.3071 | 0.2791 | 0.9143 |
| 20260512.0000 | lodo_all | 0.5000 | 82.0000 | 0.1464 | 0.1098 | 0.9839 |
| 20260513.0000 | ordinary | 0.0500 | 458.0000 | 0.8179 | 0.5459 | 0.5536 |
| 20260513.0000 | ordinary | 0.1000 | 334.0000 | 0.5964 | 0.5359 | 0.6804 |
| 20260513.0000 | ordinary | 0.2000 | 174.0000 | 0.3107 | 0.5920 | 0.8161 |
| 20260513.0000 | ordinary | 0.5000 | 37.0000 | 0.0661 | 0.6486 | 0.9571 |
| 20260513.0000 | lodo_all | 0.0500 | 419.0000 | 0.7482 | 0.3723 | 0.7214 |
| 20260513.0000 | lodo_all | 0.1000 | 273.0000 | 0.4875 | 0.3150 | 0.8464 |
| 20260513.0000 | lodo_all | 0.2000 | 113.0000 | 0.2018 | 0.2920 | 0.9411 |
| 20260513.0000 | lodo_all | 0.5000 | 20.0000 | 0.0357 | 0.3000 | 0.9893 |
| 20260514.0000 | ordinary | 0.0500 | 466.0000 | 0.8321 | 0.5429 | 0.5482 |
| 20260514.0000 | ordinary | 0.1000 | 331.0000 | 0.5911 | 0.5589 | 0.6696 |
| 20260514.0000 | ordinary | 0.2000 | 208.0000 | 0.3714 | 0.5721 | 0.7875 |
| 20260514.0000 | ordinary | 0.5000 | 43.0000 | 0.0768 | 0.6512 | 0.9500 |
| 20260514.0000 | lodo_all | 0.0500 | 455.0000 | 0.8125 | 0.4132 | 0.6643 |
| 20260514.0000 | lodo_all | 0.1000 | 300.0000 | 0.5357 | 0.3800 | 0.7964 |
| 20260514.0000 | lodo_all | 0.2000 | 156.0000 | 0.2786 | 0.3590 | 0.9000 |
| 20260514.0000 | lodo_all | 0.5000 | 32.0000 | 0.0571 | 0.4375 | 0.9750 |

## Output Files

- `data_processed/g4/g4a_multiseed_runs.csv`
- `data_processed/g4/g4a_multiseed_ordinary_summary.csv`
- `data_processed/g4/g4a_multiseed_lodo_by_domain_summary.csv`
- `data_processed/g4/g4a_multiseed_lodo_overall_summary.csv`
- `data_processed/g4/g4a_multiseed_calibration_summary.csv`
- `data_processed/g4/g4a_multiseed_risk_coverage_thresholds.csv`
- `data_processed/g4/g4a_multiseed_image_level_thresholds.csv`
