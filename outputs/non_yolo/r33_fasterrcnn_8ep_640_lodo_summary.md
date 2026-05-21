# R33 Non-YOLO Minimal LODO Validation Summary

This summary reports non-YOLO detector-family checks on the frozen 640-image/source-domain subsets.
Faster R-CNN is run for the requested 8 epochs. RetinaNet is a minimal LODO architecture check when selected.

| model | setting | train images | val images | epochs | mAP50 | precision | recall | gt | tp | fp | elapsed sec |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fasterrcnn_mobilenet320 | ordinary | 4480 | 560 | 8 | 0.1983 | 0.0859 | 0.3920 | 1393 | 546 | 5810 | 1273.5 |
| fasterrcnn_mobilenet320 | heldout_China_Drone | 3840 | 80 | 8 | 0.1397 | 0.1332 | 0.4077 | 130 | 53 | 345 | 1141.0 |
| fasterrcnn_mobilenet320 | heldout_China_MotorBike | 3840 | 80 | 8 | 0.2099 | 0.1516 | 0.4140 | 215 | 89 | 498 | 1127.2 |
| fasterrcnn_mobilenet320 | heldout_Czech_Republic | 3840 | 80 | 8 | 0.0352 | 0.0655 | 0.1496 | 127 | 19 | 271 | 1118.7 |
| fasterrcnn_mobilenet320 | heldout_India | 3840 | 80 | 8 | 0.0456 | 0.0866 | 0.1081 | 185 | 20 | 211 | 1137.5 |
| fasterrcnn_mobilenet320 | heldout_Japan | 3840 | 80 | 8 | 0.0922 | 0.0745 | 0.2866 | 157 | 45 | 559 | 1141.4 |
| fasterrcnn_mobilenet320 | heldout_Norway | 3840 | 80 | 8 | 0.0501 | 0.0602 | 0.1046 | 325 | 34 | 531 | 734.9 |
| fasterrcnn_mobilenet320 | heldout_United_States | 3840 | 80 | 8 | 0.0306 | 0.0790 | 0.2299 | 187 | 43 | 501 | 1072.8 |

## Ordinary vs mean LODO

| model | ordinary mAP50 | mean LODO mAP50 | gap | n LODO | weakest LODO domain | weakest mAP50 |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| fasterrcnn_mobilenet320 | 0.1983 | 0.0862 | 0.1121 | 7 | United_States | 0.0306 |
