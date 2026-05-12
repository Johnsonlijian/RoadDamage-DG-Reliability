from __future__ import annotations

import argparse
import csv
import os
import subprocess
from datetime import datetime
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def find_yolo_exe(root: Path, explicit: str | None) -> Path:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend(
        [
            root / ".venv-rdd" / "Scripts" / "yolo.exe",
            root / ".venv" / "Scripts" / "yolo.exe",
        ]
    )
    for candidate in candidates:
        candidate = candidate if candidate.is_absolute() else root / candidate
        if candidate.exists():
            return candidate
    raise FileNotFoundError("No yolo.exe found. Expected .venv-rdd or .venv in the project root.")


def run_dir_candidates(root: Path, project: str, name: str) -> list[Path]:
    project_path = Path(project)
    return [
        root / "runs" / "detect" / project_path / name,
        root / project_path / name,
        project_path / name if project_path.is_absolute() else root / project_path / name,
    ]


def find_results_csv(root: Path, project: str, name: str) -> Path | None:
    for run_dir in run_dir_candidates(root, project, name):
        results = run_dir / "results.csv"
        if results.exists():
            return results
    return None


def read_last_result(results_csv: Path) -> dict[str, str]:
    with results_csv.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"Empty YOLO results file: {results_csv}")
    return {key.strip(): value.strip() for key, value in rows[-1].items()}


def write_outputs(root: Path, args: argparse.Namespace, results_csv: Path, status: str) -> None:
    last = read_last_result(results_csv)
    row = {
        "name": args.name,
        "status": status,
        "data": args.data,
        "model": args.model,
        "epochs": str(args.epochs),
        "imgsz": str(args.imgsz),
        "batch": str(args.batch),
        "workers": str(args.workers),
        "device": str(args.device),
        "final_epoch": last.get("epoch", ""),
        "train_box_loss": last.get("train/box_loss", ""),
        "train_cls_loss": last.get("train/cls_loss", ""),
        "train_dfl_loss": last.get("train/dfl_loss", ""),
        "precision_B": last.get("metrics/precision(B)", ""),
        "recall_B": last.get("metrics/recall(B)", ""),
        "mAP50_B": last.get("metrics/mAP50(B)", ""),
        "mAP50_95_B": last.get("metrics/mAP50-95(B)", ""),
        "val_box_loss": last.get("val/box_loss", ""),
        "val_cls_loss": last.get("val/cls_loss", ""),
        "val_dfl_loss": last.get("val/dfl_loss", ""),
        "results_csv": str(results_csv.relative_to(root)),
    }
    csv_path = root / args.csv
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)

    summary = root / args.summary
    summary.parent.mkdir(parents=True, exist_ok=True)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# {args.title}",
        "",
        f"Generated: {generated}, local time",
        "",
        "## Configuration",
        "",
        f"- Data: `{args.data}`",
        f"- Model: `{args.model}`",
        f"- Epochs: `{args.epochs}`",
        f"- Image size: `{args.imgsz}`",
        f"- Batch: `{args.batch}`",
        f"- Device: `{args.device}`",
        f"- Workers: `{args.workers}`",
        f"- YOLO project: `{args.project}`",
        f"- Run name: `{args.name}`",
        "",
        "## Result",
        "",
        "| Precision | Recall | mAP50 | mAP50-95 |",
        "|---:|---:|---:|---:|",
        "| {precision:.4f} | {recall:.4f} | {map50:.4f} | {map5095:.4f} |".format(
            precision=float(row["precision_B"] or 0),
            recall=float(row["recall_B"] or 0),
            map50=float(row["mAP50_B"] or 0),
            map5095=float(row["mAP50_95_B"] or 0),
        ),
        "",
        "## Boundary",
        "",
        args.boundary,
    ]
    summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.csv}")
    print(f"Wrote {args.summary}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run or collect one YOLO detector training run.")
    parser.add_argument("--data", required=True)
    parser.add_argument("--model", default="yolov8n.pt")
    parser.add_argument("--project", default="outputs/yolo_single")
    parser.add_argument("--name", required=True)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--imgsz", type=int, default=320)
    parser.add_argument("--batch", type=int, default=4)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--yolo", default=None)
    parser.add_argument("--collect-only", action="store_true")
    parser.add_argument("--overwrite-run", action="store_true")
    parser.add_argument("--csv", default="data_processed/yolo_single_result.csv")
    parser.add_argument("--summary", default="outputs/yolo_single_result_summary.md")
    parser.add_argument("--title", default="YOLO Single-Run Summary")
    parser.add_argument(
        "--boundary",
        default="This is a reproducibility/pilot result only, not paper-grade detector performance.",
    )
    args = parser.parse_args()

    root = project_root()
    os.chdir(root)
    yolo = find_yolo_exe(root, args.yolo)
    data = Path(args.data)
    data_path = data if data.is_absolute() else root / data
    model = Path(args.model)
    model_path = model if model.is_absolute() else root / model
    if not data_path.exists():
        raise FileNotFoundError(f"Missing dataset YAML: {data_path}")
    if not model_path.exists():
        raise FileNotFoundError(f"Missing model weights: {model_path}")

    results_csv = None if args.overwrite_run else find_results_csv(root, args.project, args.name)
    status = "existing"
    if results_csv is None:
        if args.collect_only:
            raise FileNotFoundError(f"Missing result for collect-only mode: {args.name}")
        env = os.environ.copy()
        env["YOLO_CONFIG_DIR"] = str(root / "UltralyticsConfig")
        env["MPLCONFIGDIR"] = str(root / ".mplconfig")
        env["YOLO_OFFLINE"] = "true"
        command = [
            str(yolo),
            "detect",
            "train",
            f"data={data_path}",
            f"model={model_path}",
            f"epochs={args.epochs}",
            f"imgsz={args.imgsz}",
            f"batch={args.batch}",
            f"workers={args.workers}",
            f"device={args.device}",
            f"project={args.project}",
            f"name={args.name}",
            "exist_ok=True",
            "plots=False",
            "val=True",
        ]
        print("Running:", " ".join(command), flush=True)
        completed = subprocess.run(command, cwd=root, env=env, check=False)
        if completed.returncode != 0:
            return completed.returncode
        results_csv = find_results_csv(root, args.project, args.name)
        if results_csv is None:
            raise FileNotFoundError(f"YOLO completed but results.csv was not found for {args.name}")
        status = "ran"
    print(f"Collecting: {results_csv}", flush=True)
    write_outputs(root, args, results_csv, status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
