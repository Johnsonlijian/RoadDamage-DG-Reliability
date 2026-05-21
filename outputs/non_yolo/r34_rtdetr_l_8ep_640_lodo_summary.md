# R34 RT-DETR-L 640-Subset LODO Validation Summary

This summary reports an Ultralytics RT-DETR-L transformer-family check on the frozen 640-image/source-domain subsets.
The run is a detector-family reliability check, not a tuned detector leaderboard.

| setting | train images | val images | epochs | imgsz | batch | mAP50 | precision | recall | mAP50-95 | elapsed sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ordinary | 4480 | 560 | 8 | 640 | 2 | 0.3489 | 0.4491 | 0.3870 | 0.1562 | 3972.7 |
| heldout_China_Drone | 3840 | 80 | 8 | 640 | 2 | 0.4475 | 0.5101 | 0.4409 | 0.2486 | 3412.7 |
| heldout_China_MotorBike | 3840 | 80 | 8 | 640 | 2 | 0.3998 | 0.5357 | 0.4010 | 0.1825 | 3321.7 |
| heldout_Czech_Republic | 3840 | 80 | 8 | 640 | 2 | 0.2111 | 0.2811 | 0.3713 | 0.0750 | 3323.8 |
| heldout_India | 3840 | 80 | 8 | 640 | 2 | 0.0668 | 0.3299 | 0.1199 | 0.0206 | 3245.7 |
| heldout_Japan | 3840 | 80 | 8 | 640 | 2 | 0.2828 | 0.3544 | 0.3204 | 0.1316 | 3164.6 |
| heldout_Norway | 3840 | 80 | 8 | 640 | 2 | 0.1506 | 0.1867 | 0.2382 | 0.0648 | 3063.7 |
| heldout_United_States | 3840 | 80 | 8 | 640 | 2 | 0.2861 | 0.2651 | 0.3123 | 0.1384 | 3180.6 |

## Ordinary vs mean LODO

| ordinary mAP50 | mean LODO mAP50 | gap | n LODO | weakest LODO domain | weakest mAP50 |
| ---: | ---: | ---: | ---: | --- | ---: |
| 0.3489 | 0.2635 | 0.0854 | 7 | India | 0.0668 |
