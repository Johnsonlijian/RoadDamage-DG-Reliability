# Reproducible Runbook

Status: R08 frozen subset runbook.

## Expected Local Inputs

- Download RDD2022 from Figshare.
- Place raw archives under `data_raw/` locally.
- Do not commit raw archives or extracted images.

## Stages

1. Fetch or verify RDD2022 metadata.
2. Validate archive size and MD5.
3. Extract nested domain ZIPs.
4. Index images and parse XML annotations.
5. Build four-class YOLO subsets.
6. Run ordinary and leave-one-domain-out baselines.
7. Export prediction-level TP/FP/FN rows.
8. Compute calibration, risk-coverage, and error taxonomy tables.
9. Generate figures.

## R08 Frozen Subset Commands

Run from the repository root after installing `requirements-experiment.txt` and placing RDD2022 raw inputs under local `data_raw/`:

```powershell
python scripts/19_run_g3_timing_pilot.py --model yolov8n.pt --train-per-domain 160 --val-per-domain 80 --epochs 4 --imgsz 320 --batch 8 --device cpu --workers 0 --copy-mode copy --overwrite --ordinary-root data_processed/yolo_g3_frozen_subset_ordinary --lodo-root data_processed/yolo_g3_frozen_subset_lodo --ordinary-project outputs/yolo_g3_frozen_subset_ordinary --lodo-project outputs/yolo_g3_frozen_subset_lodo --ordinary-csv data_processed/yolo_g3_frozen_subset_ordinary_result.csv --lodo-csv data_processed/yolo_g3_frozen_subset_lodo_results.csv --ordinary-summary outputs/g3_frozen_subset_ordinary_summary.md --lodo-summary outputs/g3_frozen_subset_lodo_summary.md --combined-summary outputs/g3_frozen_subset_baseline_summary.md --summary-title "G3 Frozen Subset Baseline Summary" --purpose-text "Purpose: provide a frozen, CPU-feasible ordinary-vs-LODO subset baseline with saved prediction outputs for manuscript evidence. These results are subset-scale evidence only." --boundary-text "This frozen subset baseline can support a bounded reliability-audit manuscript, but it does not replace full-scale GPU training for a detector-performance claim."

python scripts/20_run_g3_prediction_calibration.py --ordinary-csv data_processed/yolo_g3_frozen_subset_ordinary_result.csv --lodo-csv data_processed/yolo_g3_frozen_subset_lodo_results.csv --label-prefix g3_frozen_subset --combined-lodo-predictions data_processed/predictions/g3_frozen_subset_lodo_all_predictions.csv --summary outputs/g3_frozen_subset_prediction_calibration_batch_summary.md

python scripts/21_plot_g3_reliability.py --ordinary-risk data_processed/calibration/g3_frozen_subset_ordinary_risk_coverage.csv --lodo-risk data_processed/calibration/g3_frozen_subset_lodo_all_risk_coverage.csv --svg figures/fig_g3_frozen_subset_risk_coverage.svg --summary figures/fig_g3_frozen_subset_risk_coverage_inputs.md

python scripts/22_summarize_prediction_errors.py --predictions data_processed/predictions/g3_frozen_subset_lodo_all_predictions.csv --domain-csv data_processed/g3_frozen_subset_lodo_error_by_domain.csv --domain-class-csv data_processed/g3_frozen_subset_lodo_error_by_domain_class.csv --class-csv data_processed/g3_frozen_subset_lodo_error_by_class.csv --summary outputs/g3_frozen_subset_error_taxonomy_summary.md --title "G3 Frozen Subset Error Taxonomy Summary" --boundary "frozen subset-scale prediction export. Use for manuscript failure analysis with an explicit subset-scale boundary; do not treat as full-scale detector performance."
```

Prediction CSVs and calibration tables can be large and are ignored by default. The repository includes small summaries and final metric/error tables.
