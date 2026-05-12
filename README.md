# RoadDamage-DG Reliability Benchmark

Clean public reproducibility package for the RoadDamage-DG paper project.

Status: R08 frozen subset package, 2026-05-12. This repository contains code, configs, small derived summaries, metric tables, and SVG figures for the subset-scale reliability-audit route.

## Scope

This repository is intended to reproduce:

- RDD2022 source metadata checks;
- archive and nested-ZIP validation;
- domain and label-boundary inventories;
- leave-one-domain-out subset construction;
- YOLO frozen subset baselines;
- prediction export, calibration, risk-coverage, and failure-taxonomy tables.

## Current Frozen Baseline

The included R08 baseline uses YOLOv8n pretrained weights with:

- 160 training images per training domain;
- 80 validation images per target domain;
- 4 CPU epochs;
- image size 320;
- batch size 8;
- seven leave-one-domain-out domains plus an ordinary mixed-domain reference.

Key derived files:

- `outputs/g3_frozen_subset_baseline_summary.md`
- `data_processed/yolo_g3_frozen_subset_ordinary_result.csv`
- `data_processed/yolo_g3_frozen_subset_lodo_results.csv`
- `outputs/g3_frozen_subset_prediction_calibration_batch_summary.md`
- `outputs/g3_frozen_subset_error_taxonomy_summary.md`
- `figures/fig06_g3_frozen_ordinary_vs_lodo.svg`
- `figures/fig07_g3_frozen_risk_tradeoff.svg`
- `figures/fig08_g3_frozen_pooled_risk_coverage.svg`

## Exclusions

This repository must not contain:

- raw RDD2022 archives or extracted images;
- active manuscript drafts;
- internal `rounds/` or `logs/`;
- reviewer-response or cover-letter drafts;
- credentials or local virtual environments.

## Intended Remote

`https://github.com/Johnsonlijian/RoadDamage-DG-Reliability`

Repository creation and push remain blocked until the user creates the GitHub repository or authorizes push from the local environment.
