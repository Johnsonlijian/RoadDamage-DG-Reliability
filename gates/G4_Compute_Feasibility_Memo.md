# G4 Compute Feasibility Memo

Date checked: 2026-05-13, Asia/Shanghai

## Local Environment

- GPU visible through `nvidia-smi`: NVIDIA GeForce RTX 3070, 8192 MiB, driver 560.94.
- Current RoadDamage-DG Python environment: `.venv-rdd`.
- PyTorch in `.venv-rdd`: `2.11.0+cpu`.
- `torch.cuda.is_available()`: `False`.
- Local YOLO weights found: `yolov8n.pt`.
- Local YOLO stronger bridge weights not found: `yolov8s.pt`, `yolov8m.pt`.

## Consequence

The machine has a visible GPU, but the active training environment is CPU-only. Therefore, G4a can run on CPU using the current environment, but G4b with YOLOv8s/YOLOv8m at 640 px should be treated as blocked until either:

1. a CUDA-enabled PyTorch/Ultralytics environment is installed and smoke-tested; or
2. a separate GPU environment/cloud machine is used; or
3. the target route is explicitly downgraded so that G4b is no longer a submission gate.

## Remaining G4a Work

The existing R08 run can be treated as seed `20260512` only. To complete G4a as defined in `configs/g4_evidence_matrix.yaml`, the remaining minimum CPU runs are:

- seed `20260513`: one ordinary run plus seven LODO runs;
- seed `20260514`: one ordinary run plus seven LODO runs.

This is 16 additional YOLOv8n subset runs at 4 epochs, 320 px, batch 8, CPU, followed by prediction export, calibration diagnostics, image-level coverage, and label-boundary overlap summaries.

## Dry-Run Command

```powershell
python scripts\24_run_g4_evidence_layer.py `
  --suite g4a_r08_repeat `
  --models yolov8n.pt `
  --seeds 20260513 20260514 `
  --train-per-domain 160 `
  --val-per-domain 80 `
  --epochs 4 `
  --imgsz 320 `
  --batch 8 `
  --device cpu `
  --workers 0 `
  --copy-mode hardlink `
  --postprocess `
  --dry-run
```

## Actual Run Command

Run only when the machine can be occupied for a long CPU job:

```powershell
python scripts\24_run_g4_evidence_layer.py `
  --suite g4a_r08_repeat `
  --models yolov8n.pt `
  --seeds 20260513 20260514 `
  --train-per-domain 160 `
  --val-per-domain 80 `
  --epochs 4 `
  --imgsz 320 `
  --batch 8 `
  --device cpu `
  --workers 0 `
  --copy-mode hardlink `
  --postprocess
```

## G4b Bridge Command Template

Use only after `yolov8s.pt` or `yolov8m.pt` exists and CUDA or acceptable CPU wall time has been confirmed:

```powershell
python scripts\24_run_g4_evidence_layer.py `
  --suite g4b_bridge `
  --models yolov8s.pt `
  --seeds 20260512 `
  --train-per-domain 160 `
  --val-per-domain 80 `
  --epochs 8 `
  --imgsz 640 `
  --batch 8 `
  --device cuda `
  --workers 0 `
  --copy-mode hardlink `
  --postprocess
```

## Submission Decision

Until G4a and at least one G4b bridge matrix complete, the manuscript remains protocol-ready only. If G4b cannot be completed, the rational options are to downgrade the target, keep the work as a reproducibility/preprint package, or reframe the paper as a pilot protocol demonstration without high-selectivity EAAI claims.
