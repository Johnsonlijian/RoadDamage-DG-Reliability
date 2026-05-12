# RDD2022 Extracted Inventory Audit

## Totals

- XML image rows: 38385
- Box rows: 65712
- Primary label-map classes: D00, D10, D20, D40
- Primary-class boxes: 55007
- Non-primary observed boxes: 10705

## Train XML Images By Domain

- China_Drone: 2401
- China_MotorBike: 1977
- Czech_Republic: 2829
- India: 7706
- Japan: 10506
- Norway: 8161
- United_States: 4805

## Boxes By Domain

- China_Drone: 3840
- China_MotorBike: 4927
- Czech_Republic: 1745
- India: 8203
- Japan: 24754
- Norway: 11229
- United_States: 11014

## Boxes By Label

- D00: 26016 (primary)
- D10: 11830 (primary)
- D20: 10617 (primary)
- D40: 6544 (primary)
- D44: 5057 (non-primary-observed)
- D50: 3581 (non-primary-observed)
- Repair: 1046 (non-primary-observed)
- D43: 793 (non-primary-observed)
- D01: 179 (non-primary-observed)
- D11: 45 (non-primary-observed)
- Block crack: 3 (non-primary-observed)
- D0w0: 1 (non-primary-observed)

## Interpretation Boundary

Use the label-map classes as the primary supervised detection task unless the additional observed labels are verified against official RDD documentation. Non-primary observed labels must be reported as ignored, merged, or modeled only after an explicit task definition.
