# G4 Execution Report

Date: 2026-05-14, Asia/Shanghai

## Summary

The G4 evidence layer has been executed after user authorization for GPU compute. The project now has repeated-seed YOLOv8n evidence, a three-seed YOLOv8s detector-capacity bridge, regenerated calibration diagnostics, image-level workload proxies, label-boundary false-positive overlap summaries, and G4 figures.

## Environment

- Python environment: `.venv-rdd`
- PyTorch: `2.11.0+cu126`
- CUDA available: `True`
- GPU: NVIDIA GeForce RTX 3070, 8192 MiB, driver 560.94
- YOLO weights used: `yolov8n.pt`, `yolov8s.pt`

## Commands Executed

G4a:

```powershell
.venv-rdd\Scripts\python.exe scripts\24_run_g4_evidence_layer.py `
  --suite g4a_r08_repeat `
  --models yolov8n.pt `
  --seeds 20260513 20260514 `
  --train-per-domain 160 `
  --val-per-domain 80 `
  --epochs 4 `
  --imgsz 320 `
  --batch 8 `
  --device cuda `
  --workers 0 `
  --copy-mode copy `
  --overwrite `
  --overwrite-runs `
  --postprocess
```

G4b:

```powershell
.venv-rdd\Scripts\python.exe scripts\24_run_g4_evidence_layer.py `
  --suite g4b_bridge `
  --models yolov8s.pt `
  --seeds 20260512 20260513 20260514 `
  --train-per-domain 160 `
  --val-per-domain 80 `
  --epochs 8 `
  --imgsz 640 `
  --batch 8 `
  --device cuda `
  --workers 0 `
  --copy-mode copy `
  --overwrite `
  --overwrite-runs `
  --postprocess
```

Label-boundary batch:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\31_run_g4_label_boundary_batch.ps1
```

## Result Summaries

- `outputs/g4/g4a_multiseed_summary.md`
- `outputs/g4/g4b_bridge_summary.md`
- `outputs/g4/g4_label_boundary_overlap_summary.md`

## Figures

- `manuscript/figures/fig09_g4a_multiseed_lodo_map50.svg`
- `manuscript/figures/fig10_g4a_image_level_thresholds.svg`
- `manuscript/figures/fig11_g4b_yolov8n_vs_yolov8s_bridge.svg`

## Gate Outcome

G4 compute passes for a bounded protocol manuscript. It does not pass for deployment claims, state-of-the-art detector claims, full-scale benchmark claims, or validated road-agency workload policy.
