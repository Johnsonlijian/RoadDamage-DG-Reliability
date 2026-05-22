# R36 Small Target-Domain Evidence Check

This round fine-tunes each frozen YOLOv8s 640-image/source-domain LODO checkpoint with a small number of labelled images from the held-out target domain.
The target-domain images used for local evidence are removed from the target evaluation split; results are therefore evaluated on the remaining target-domain images.
The check is used to test whether limited local evidence changes the validation-boundary interpretation; it is not reported as a domain-adaptation leaderboard.

| domain | target images | eval images | target boxes | baseline LODO mAP50 | target-evidence mAP50 | delta | gap recovery | precision | recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| China_Drone | 20 | 60 | 34 | 0.4529 | 0.4205 | -0.0324 |  | 0.4530 | 0.4545 |
| China_MotorBike | 10 | 70 | 31 | 0.2184 | 0.2427 | +0.0244 | 0.214 | 0.3406 | 0.3013 |
| China_MotorBike | 20 | 60 | 56 | 0.2184 | 0.2122 | -0.0062 | -0.054 | 0.2411 | 0.2218 |
| China_MotorBike | 40 | 40 | 105 | 0.2184 | 0.2696 | +0.0512 | 0.449 | 0.1911 | 0.3950 |
| Czech_Republic | 20 | 60 | 33 | 0.1955 | 0.2552 | +0.0597 | 0.436 | 0.4309 | 0.3118 |
| India | 10 | 70 | 20 | 0.0696 | 0.0693 | -0.0003 | -0.001 | 0.2412 | 0.1115 |
| India | 20 | 60 | 38 | 0.0696 | 0.0742 | +0.0046 | 0.017 | 0.3572 | 0.1013 |
| India | 40 | 40 | 91 | 0.0696 | 0.1139 | +0.0443 | 0.168 | 0.2275 | 0.2097 |
| Japan | 20 | 60 | 49 | 0.2401 | 0.2722 | +0.0321 | 0.348 | 0.3727 | 0.2811 |
| Norway | 10 | 70 | 65 | 0.0980 | 0.1133 | +0.0152 | 0.065 | 0.2411 | 0.1206 |
| Norway | 20 | 60 | 98 | 0.0980 | 0.1217 | +0.0237 | 0.101 | 0.2581 | 0.1111 |
| Norway | 40 | 40 | 169 | 0.0980 | 0.0954 | -0.0026 | -0.011 | 0.2122 | 0.1125 |
| United_States | 20 | 60 | 44 | 0.2854 | 0.3220 | +0.0367 | 0.778 | 0.3742 | 0.3499 |

## Aggregate

- Mean baseline LODO mAP50: 0.1794.
- Mean target-evidence mAP50: 0.1986.
- Mean delta mAP50: +0.0193.
- Improved domains: 9 of 13.
- Degraded domains: 4 of 13.
