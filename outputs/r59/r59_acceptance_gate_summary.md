# R59 Acceptance-Gate Public Summary

Source: `data_processed/r59_acceptance_gate/source_tables/r43_dose_curves.csv`.
Criterion: mAP50 >= 0.20, reported as an audit criterion rather than a deployment threshold.

| Domain | K=0 mean | K=320 mean | K* mean | K* same-K all-seed clearance |
| --- | ---: | ---: | ---: | ---: |
| China_Drone | 0.304 | 0.353 | 0 | 0 |
| China_MotorBike | 0.245 | 0.373 | 0 | 0 |
| Czech_Republic | 0.213 | 0.226 | 0 | 160 |
| India | 0.091 | 0.130 | >320 | >320 |
| Japan | 0.261 | 0.299 | 0 | 0 |
| Norway | 0.087 | 0.108 | >320 | >320 |
| United_States | 0.362 | 0.424 | 0 | 0 |

Boundary: these are derived summary results from the R59/AutCon acceptance-gate package.
Raw RDD images, trained weights, active manuscripts, cover letters, and internal round logs are not redistributed.
