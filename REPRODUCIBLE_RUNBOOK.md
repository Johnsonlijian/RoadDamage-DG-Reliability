# Reproducible Runbook

Status: scaffold only. Commands will be finalized after the G3 baseline scale is frozen.

## Expected Local Inputs

- Download RDD2022 from Figshare.
- Place raw archives under `data_raw/` locally.
- Do not commit raw archives or extracted images.

## Planned Stages

1. Fetch or verify RDD2022 metadata.
2. Validate archive size and MD5.
3. Extract nested domain ZIPs.
4. Index images and parse XML annotations.
5. Build four-class YOLO subsets.
6. Run ordinary and leave-one-domain-out baselines.
7. Export prediction-level TP/FP/FN rows.
8. Compute calibration, risk-coverage, and error taxonomy tables.
9. Generate figures.

## Current Internal Provenance

Internal development outputs were generated under the private project folder on 2026-05-12. Only non-sensitive scripts, configs, derived summaries, and figures should be copied into this public package after final baseline scale is decided.
