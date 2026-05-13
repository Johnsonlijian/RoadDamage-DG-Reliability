# G4b YOLOv8s Detector-Capacity Bridge Summary

Boundary: this bridge changes detector size, image size, epoch count, and GPU execution together. It tests whether the audit protocol remains informative with a stronger bounded baseline; it is not an architecture ranking or a full-scale benchmark.

Completed YOLOv8s bridge seeds: 20260512, 20260513, 20260514.

## Headline Metrics

- Ordinary mAP50 changes from 0.0831 +/- 0.0078 with YOLOv8n 320px/4ep to 0.1864 +/- 0.0087 with YOLOv8s 640px/8ep across completed seed pairs.
- Mean LODO mAP50 changes from 0.0640 +/- 0.0049 to 0.1294 +/- 0.0154.
- The lowest YOLOv8s held-out-domain mean mAP50 is Norway (0.0511 +/- 0.0178).

## Setting Summary

| model_label | setting | n_seed_runs | n_detector_runs_total | precision_B_mean | recall_B_mean | mAP50_B_mean | mAP50_B_std | mAP50_95_B_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| YOLOv8n 320px 4ep | LODO mean | 3.0000 | 21.0000 | 0.1859 | 0.1056 | 0.0640 | 0.0049 | 0.0210 |
| YOLOv8n 320px 4ep | ordinary | 3.0000 | 3.0000 | 0.1824 | 0.1687 | 0.0831 | 0.0078 | 0.0274 |
| YOLOv8s 640px 8ep | LODO mean | 3.0000 | 21.0000 | 0.2586 | 0.1913 | 0.1294 | 0.0154 | 0.0513 |
| YOLOv8s 640px 8ep | ordinary | 3.0000 | 3.0000 | 0.2926 | 0.2683 | 0.1864 | 0.0087 | 0.0714 |

## Domain Bridge Summary

| heldout_domain | n_seed_pairs | mAP50_B_yolov8n_mean | mAP50_B_yolov8s_mean | mAP50_B_delta_yolov8s_minus_yolov8n_mean | recall_B_yolov8n_mean | recall_B_yolov8s_mean |
| --- | --- | --- | --- | --- | --- | --- |
| Norway | 3.0000 | 0.0103 | 0.0511 | 0.0408 | 0.0177 | 0.0820 |
| India | 3.0000 | 0.0542 | 0.0602 | 0.0060 | 0.0768 | 0.0841 |
| China_MotorBike | 3.0000 | 0.0706 | 0.1147 | 0.0441 | 0.1247 | 0.1970 |
| Czech_Republic | 3.0000 | 0.0735 | 0.1474 | 0.0739 | 0.1056 | 0.2200 |
| Japan | 3.0000 | 0.0674 | 0.1542 | 0.0868 | 0.1382 | 0.2308 |
| China_Drone | 3.0000 | 0.0760 | 0.1754 | 0.0994 | 0.1299 | 0.1745 |
| United_States | 3.0000 | 0.0961 | 0.2027 | 0.1066 | 0.1459 | 0.3509 |

## Calibration Bridge

| seed | model_label | split | n_predictions | ece_proxy | high_conf_n_predictions | high_conf_mean_confidence | high_conf_empirical_precision | high_conf_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20260512.0000 | YOLOv8n 320px 4ep | lodo_all | 141681.0000 | 0.0036 | 1344.0000 | 0.3035 | 0.0774 | 0.2261 |
| 20260512.0000 | YOLOv8n 320px 4ep | ordinary | 151913.0000 | 0.0019 | 1080.0000 | 0.2145 | 0.1954 | 0.0192 |
| 20260513.0000 | YOLOv8n 320px 4ep | lodo_all | 144652.0000 | 0.0021 | 728.0000 | 0.1944 | 0.1250 | 0.0694 |
| 20260513.0000 | YOLOv8n 320px 4ep | ordinary | 154733.0000 | 0.0020 | 1128.0000 | 0.2173 | 0.1782 | 0.0391 |
| 20260514.0000 | YOLOv8n 320px 4ep | lodo_all | 153571.0000 | 0.0025 | 955.0000 | 0.2081 | 0.1288 | 0.0793 |
| 20260514.0000 | YOLOv8n 320px 4ep | ordinary | 158180.0000 | 0.0032 | 1657.0000 | 0.2131 | 0.1334 | 0.0797 |
| 20260512.0000 | YOLOv8s 640px 8ep | lodo_all | 112123.0000 | 0.0042 | 1852.0000 | 0.1697 | 0.1377 | 0.0320 |
| 20260512.0000 | YOLOv8s 640px 8ep | ordinary | 119821.0000 | 0.0043 | 2696.0000 | 0.1818 | 0.1903 | 0.0085 |
| 20260513.0000 | YOLOv8s 640px 8ep | lodo_all | 97842.0000 | 0.0025 | 1190.0000 | 0.1586 | 0.1824 | 0.0238 |
| 20260513.0000 | YOLOv8s 640px 8ep | ordinary | 132693.0000 | 0.0050 | 3098.0000 | 0.1868 | 0.1540 | 0.0328 |
| 20260514.0000 | YOLOv8s 640px 8ep | lodo_all | 112661.0000 | 0.0033 | 1705.0000 | 0.1695 | 0.1677 | 0.0017 |
| 20260514.0000 | YOLOv8s 640px 8ep | ordinary | 122284.0000 | 0.0046 | 2731.0000 | 0.1861 | 0.1867 | 0.0007 |

## Image-Level Threshold Bridge

| seed | model_label | split | threshold | selected_images | image_review_coverage | selected_image_tp_rate | gt_image_miss_proxy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 20260512.0000 | YOLOv8n 320px 4ep | lodo_all | 0.0500 | 457.0000 | 0.8161 | 0.3654 | 0.7018 |
| 20260512.0000 | YOLOv8n 320px 4ep | lodo_all | 0.1000 | 315.0000 | 0.5625 | 0.3143 | 0.8232 |
| 20260512.0000 | YOLOv8n 320px 4ep | lodo_all | 0.2000 | 172.0000 | 0.3071 | 0.2791 | 0.9143 |
| 20260512.0000 | YOLOv8n 320px 4ep | lodo_all | 0.5000 | 82.0000 | 0.1464 | 0.1098 | 0.9839 |
| 20260512.0000 | YOLOv8n 320px 4ep | ordinary | 0.0500 | 478.0000 | 0.8536 | 0.5628 | 0.5196 |
| 20260512.0000 | YOLOv8n 320px 4ep | ordinary | 0.1000 | 349.0000 | 0.6232 | 0.5215 | 0.6750 |
| 20260512.0000 | YOLOv8n 320px 4ep | ordinary | 0.2000 | 195.0000 | 0.3482 | 0.5692 | 0.8018 |
| 20260512.0000 | YOLOv8n 320px 4ep | ordinary | 0.5000 | 34.0000 | 0.0607 | 0.6765 | 0.9589 |
| 20260513.0000 | YOLOv8n 320px 4ep | lodo_all | 0.0500 | 419.0000 | 0.7482 | 0.3723 | 0.7214 |
| 20260513.0000 | YOLOv8n 320px 4ep | lodo_all | 0.1000 | 273.0000 | 0.4875 | 0.3150 | 0.8464 |
| 20260513.0000 | YOLOv8n 320px 4ep | lodo_all | 0.2000 | 113.0000 | 0.2018 | 0.2920 | 0.9411 |
| 20260513.0000 | YOLOv8n 320px 4ep | lodo_all | 0.5000 | 20.0000 | 0.0357 | 0.3000 | 0.9893 |
| 20260513.0000 | YOLOv8n 320px 4ep | ordinary | 0.0500 | 458.0000 | 0.8179 | 0.5459 | 0.5536 |
| 20260513.0000 | YOLOv8n 320px 4ep | ordinary | 0.1000 | 334.0000 | 0.5964 | 0.5359 | 0.6804 |
| 20260513.0000 | YOLOv8n 320px 4ep | ordinary | 0.2000 | 174.0000 | 0.3107 | 0.5920 | 0.8161 |
| 20260513.0000 | YOLOv8n 320px 4ep | ordinary | 0.5000 | 37.0000 | 0.0661 | 0.6486 | 0.9571 |
| 20260514.0000 | YOLOv8n 320px 4ep | lodo_all | 0.0500 | 455.0000 | 0.8125 | 0.4132 | 0.6643 |
| 20260514.0000 | YOLOv8n 320px 4ep | lodo_all | 0.1000 | 300.0000 | 0.5357 | 0.3800 | 0.7964 |
| 20260514.0000 | YOLOv8n 320px 4ep | lodo_all | 0.2000 | 156.0000 | 0.2786 | 0.3590 | 0.9000 |
| 20260514.0000 | YOLOv8n 320px 4ep | lodo_all | 0.5000 | 32.0000 | 0.0571 | 0.4375 | 0.9750 |
| 20260514.0000 | YOLOv8n 320px 4ep | ordinary | 0.0500 | 466.0000 | 0.8321 | 0.5429 | 0.5482 |
| 20260514.0000 | YOLOv8n 320px 4ep | ordinary | 0.1000 | 331.0000 | 0.5911 | 0.5589 | 0.6696 |
| 20260514.0000 | YOLOv8n 320px 4ep | ordinary | 0.2000 | 208.0000 | 0.3714 | 0.5721 | 0.7875 |
| 20260514.0000 | YOLOv8n 320px 4ep | ordinary | 0.5000 | 43.0000 | 0.0768 | 0.6512 | 0.9500 |
| 20260512.0000 | YOLOv8s 640px 8ep | lodo_all | 0.0500 | 518.0000 | 0.9250 | 0.6004 | 0.4446 |
| 20260512.0000 | YOLOv8s 640px 8ep | lodo_all | 0.1000 | 430.0000 | 0.7679 | 0.5047 | 0.6125 |
| 20260512.0000 | YOLOv8s 640px 8ep | lodo_all | 0.2000 | 222.0000 | 0.3964 | 0.4820 | 0.8089 |
| 20260512.0000 | YOLOv8s 640px 8ep | lodo_all | 0.5000 | 22.0000 | 0.0393 | 0.6818 | 0.9732 |
| 20260512.0000 | YOLOv8s 640px 8ep | ordinary | 0.0500 | 544.0000 | 0.9714 | 0.7684 | 0.2536 |
| 20260512.0000 | YOLOv8s 640px 8ep | ordinary | 0.1000 | 485.0000 | 0.8661 | 0.7010 | 0.3929 |
| 20260512.0000 | YOLOv8s 640px 8ep | ordinary | 0.2000 | 283.0000 | 0.5054 | 0.7138 | 0.6393 |
| 20260512.0000 | YOLOv8s 640px 8ep | ordinary | 0.5000 | 41.0000 | 0.0732 | 0.8780 | 0.9357 |
| 20260513.0000 | YOLOv8s 640px 8ep | lodo_all | 0.0500 | 474.0000 | 0.8464 | 0.5675 | 0.5196 |
| 20260513.0000 | YOLOv8s 640px 8ep | lodo_all | 0.1000 | 335.0000 | 0.5982 | 0.5284 | 0.6839 |
| 20260513.0000 | YOLOv8s 640px 8ep | lodo_all | 0.2000 | 144.0000 | 0.2571 | 0.5000 | 0.8714 |
| 20260513.0000 | YOLOv8s 640px 8ep | lodo_all | 0.5000 | 5.0000 | 0.0089 | 0.6000 | 0.9946 |
| 20260513.0000 | YOLOv8s 640px 8ep | ordinary | 0.0500 | 544.0000 | 0.9714 | 0.7629 | 0.2589 |
| 20260513.0000 | YOLOv8s 640px 8ep | ordinary | 0.1000 | 475.0000 | 0.8482 | 0.7200 | 0.3893 |
| 20260513.0000 | YOLOv8s 640px 8ep | ordinary | 0.2000 | 317.0000 | 0.5661 | 0.7224 | 0.5911 |
| 20260513.0000 | YOLOv8s 640px 8ep | ordinary | 0.5000 | 48.0000 | 0.0857 | 0.8125 | 0.9304 |
| 20260514.0000 | YOLOv8s 640px 8ep | lodo_all | 0.0500 | 497.0000 | 0.8875 | 0.6278 | 0.4429 |
| 20260514.0000 | YOLOv8s 640px 8ep | lodo_all | 0.1000 | 371.0000 | 0.6625 | 0.6146 | 0.5929 |
| 20260514.0000 | YOLOv8s 640px 8ep | lodo_all | 0.2000 | 183.0000 | 0.3268 | 0.5902 | 0.8071 |
| 20260514.0000 | YOLOv8s 640px 8ep | lodo_all | 0.5000 | 4.0000 | 0.0071 | 1.0000 | 0.9929 |
| 20260514.0000 | YOLOv8s 640px 8ep | ordinary | 0.0500 | 540.0000 | 0.9643 | 0.7796 | 0.2482 |
| 20260514.0000 | YOLOv8s 640px 8ep | ordinary | 0.1000 | 491.0000 | 0.8768 | 0.7189 | 0.3696 |
| 20260514.0000 | YOLOv8s 640px 8ep | ordinary | 0.2000 | 314.0000 | 0.5607 | 0.6783 | 0.6196 |
| 20260514.0000 | YOLOv8s 640px 8ep | ordinary | 0.5000 | 44.0000 | 0.0786 | 0.8636 | 0.9321 |

## Output Files

- `data_processed/g4/g4b_bridge_setting_runs.csv`
- `data_processed/g4/g4b_bridge_setting_summary.csv`
- `data_processed/g4/g4b_bridge_domain_long.csv`
- `data_processed/g4/g4b_bridge_domain_comparison.csv`
- `data_processed/g4/g4b_bridge_domain_summary.csv`
- `data_processed/g4/g4b_bridge_calibration_summary.csv`
- `data_processed/g4/g4b_bridge_image_level_thresholds.csv`
