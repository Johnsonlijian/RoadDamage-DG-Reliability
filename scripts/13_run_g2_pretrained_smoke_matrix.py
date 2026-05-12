from __future__ import annotations

import argparse
import csv
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


DOMAINS = [
    "China_Drone",
    "China_MotorBike",
    "Czech_Republic",
    "India",
    "Japan",
    "Norway",
    "United_States",
]


METRIC_KEYS = [
    "metrics/precision(B)",
    "metrics/recall(B)",
    "metrics/mAP50(B)",
    "metrics/mAP50-95(B)",
]


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


def safe_name(domain: str, suffix: str) -> str:
    clean_domain = re.sub(r"[^A-Za-z0-9_]+", "_", domain)
    clean_suffix = re.sub(r"[^A-Za-z0-9_]+", "_", suffix).strip("_")
    return f"heldout_{clean_domain}_{clean_suffix}" if clean_suffix else f"heldout_{clean_domain}"


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
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        raise ValueError(f"Empty YOLO results file: {results_csv}")
    return {key.strip(): value.strip() for key, value in rows[-1].items()}


def first_int_from_summary(summary: Path, label: str) -> str:
    if not summary.exists():
        return ""
    pattern = re.compile(rf"{re.escape(label)}:\s*`?(\d+)")
    for line in summary.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = pattern.search(line)
        if match:
            return match.group(1)
    return ""


def collect_row(
    root: Path,
    domain: str,
    model: str,
    subset_yaml: Path,
    subset_summary: Path,
    project: str,
    run_name: str,
    results_csv: Path,
    args: argparse.Namespace,
    status: str,
) -> dict[str, str]:
    last = read_last_result(results_csv)
    row = {
        "heldout_domain": domain,
        "status": status,
        "model": model,
        "epochs": str(args.epochs),
        "imgsz": str(args.imgsz),
        "batch": str(args.batch),
        "workers": str(args.workers),
        "device": str(args.device),
        "train_images": first_int_from_summary(subset_summary, "Train images"),
        "val_images": first_int_from_summary(subset_summary, "Validation images"),
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
        "subset_yaml": str(subset_yaml.relative_to(root)),
    }
    return row


def write_csv(rows: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "heldout_domain",
        "status",
        "model",
        "epochs",
        "imgsz",
        "batch",
        "workers",
        "device",
        "train_images",
        "val_images",
        "final_epoch",
        "train_box_loss",
        "train_cls_loss",
        "train_dfl_loss",
        "precision_B",
        "recall_B",
        "mAP50_B",
        "mAP50_95_B",
        "val_box_loss",
        "val_cls_loss",
        "val_dfl_loss",
        "results_csv",
        "subset_yaml",
    ]
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def write_summary(rows: list[dict[str, str]], output: Path, args: argparse.Namespace) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# G2 Pretrained Smoke Matrix Summary",
        "",
        f"Generated: {generated}, local time",
        "",
        "Purpose: verify that the pretrained-detector leave-one-domain-out pipeline can run across all seven RDD2022 domains and expose early cross-domain signal. This is not a full paper-grade result.",
        "",
        "## Configuration",
        "",
        f"- Subset root: `{args.subset_root}`",
        f"- Model: `{args.model}`",
        f"- Epochs: `{args.epochs}`",
        f"- Image size: `{args.imgsz}`",
        f"- Batch: `{args.batch}`",
        f"- Device: `{args.device}`",
        f"- Workers: `{args.workers}`",
        f"- YOLO project: `{args.project}`",
        "",
        "## Matrix",
        "",
        "| Held-out domain | Status | Train images | Val images | Precision | Recall | mAP50 | mAP50-95 |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {domain} | {status} | {train} | {val} | {precision:.4f} | {recall:.4f} | {map50:.4f} | {map5095:.4f} |".format(
                domain=row["heldout_domain"],
                status=row["status"],
                train=row["train_images"],
                val=row["val_images"],
                precision=as_float(row["precision_B"]),
                recall=as_float(row["recall_B"]),
                map50=as_float(row["mAP50_B"]),
                map5095=as_float(row["mAP50_95_B"]),
            )
        )
    if rows:
        mean_map50 = sum(as_float(row["mAP50_B"]) for row in rows) / len(rows)
        mean_map5095 = sum(as_float(row["mAP50_95_B"]) for row in rows) / len(rows)
        best = max(rows, key=lambda row: as_float(row["mAP50_B"]))
        worst = min(rows, key=lambda row: as_float(row["mAP50_B"]))
        lines.extend(
            [
                "",
                "## Smoke Signal",
                "",
                f"- Mean mAP50 across held-out domains: `{mean_map50:.4f}`",
                f"- Mean mAP50-95 across held-out domains: `{mean_map5095:.4f}`",
                f"- Highest held-out mAP50: `{best['heldout_domain']}` = `{as_float(best['mAP50_B']):.4f}`",
                f"- Lowest held-out mAP50: `{worst['heldout_domain']}` = `{as_float(worst['mAP50_B']):.4f}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Treat these numbers as a reproducibility and go/no-go signal only.",
            "- The run uses the subset sizes shown in the matrix; if those sizes are below the full dataset, label the result as subset-scale.",
            "- A manuscript claim still requires fixed full-scale training, saved predictions, calibration/selective-prediction analysis, and failure taxonomy.",
            "- Low absolute scores from short CPU runs do not invalidate the topic; cross-domain variation and pipeline viability are the useful signal at this gate.",
        ]
    )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run or collect G2 YOLOv8n pretrained smoke matrix results.")
    parser.add_argument("--subset-root", default="data_processed/yolo_lodo_smoke")
    parser.add_argument("--model", default="yolov8n.pt")
    parser.add_argument("--project", default="outputs/yolo_g2_smoke")
    parser.add_argument("--run-suffix", default="pretrained_1epoch")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--imgsz", type=int, default=320)
    parser.add_argument("--batch", type=int, default=4)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--domains", nargs="*", default=DOMAINS)
    parser.add_argument("--yolo", default=None, help="Optional explicit path to yolo.exe.")
    parser.add_argument("--overwrite-runs", action="store_true", help="Rerun even if a results.csv already exists.")
    parser.add_argument("--collect-only", action="store_true", help="Do not train; only collect existing result files.")
    parser.add_argument("--csv", default="data_processed/yolo_g2_smoke_results.csv")
    parser.add_argument("--summary", default="outputs/yolo_g2_smoke_results_summary.md")
    args = parser.parse_args()

    root = project_root()
    os.chdir(root)
    yolo = find_yolo_exe(root, args.yolo)
    model = Path(args.model)
    model_path = model if model.is_absolute() else root / model
    if not model_path.exists():
        raise FileNotFoundError(f"Missing model weights: {model_path}")

    env = os.environ.copy()
    env["YOLO_CONFIG_DIR"] = str(root / "UltralyticsConfig")
    env["MPLCONFIGDIR"] = str(root / ".mplconfig")
    env["YOLO_OFFLINE"] = "true"

    rows: list[dict[str, str]] = []
    for domain in args.domains:
        subset = root / args.subset_root / f"heldout_{domain}"
        subset_yaml = subset / "dataset.yaml"
        subset_summary = subset / "subset_summary.md"
        if not subset_yaml.exists():
            raise FileNotFoundError(f"Missing subset dataset.yaml for {domain}: {subset_yaml}")
        run_name = safe_name(domain, args.run_suffix)
        results_csv = find_results_csv(root, args.project, run_name)
        status = "existing"
        if args.overwrite_runs or results_csv is None:
            if args.collect_only:
                raise FileNotFoundError(f"Missing result for collect-only mode: {run_name}")
            command = [
                str(yolo),
                "detect",
                "train",
                f"data={subset_yaml}",
                f"model={model_path}",
                f"epochs={args.epochs}",
                f"imgsz={args.imgsz}",
                f"batch={args.batch}",
                f"workers={args.workers}",
                f"device={args.device}",
                f"project={args.project}",
                f"name={run_name}",
                "exist_ok=True",
                "plots=False",
                "val=True",
            ]
            print("Running:", " ".join(command), flush=True)
            completed = subprocess.run(command, cwd=root, env=env, check=False)
            if completed.returncode != 0:
                return completed.returncode
            results_csv = find_results_csv(root, args.project, run_name)
            if results_csv is None:
                raise FileNotFoundError(f"YOLO completed but results.csv was not found for {run_name}")
            status = "ran"
        print(f"Collecting {domain}: {results_csv}", flush=True)
        rows.append(
            collect_row(
                root=root,
                domain=domain,
                model=str(model_path.relative_to(root)),
                subset_yaml=subset_yaml,
                subset_summary=subset_summary,
                project=args.project,
                run_name=run_name,
                results_csv=results_csv,
                args=args,
                status=status,
            )
        )

    write_csv(rows, root / args.csv)
    write_summary(rows, root / args.summary, args)
    print(f"Wrote {args.csv}")
    print(f"Wrote {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
