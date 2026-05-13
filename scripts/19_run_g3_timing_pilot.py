from __future__ import annotations

import argparse
import csv
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


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run(command: list[str], root: Path) -> None:
    print("Running:", " ".join(command), flush=True)
    completed = subprocess.run(command, cwd=root, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def write_combined_summary(root: Path, args: argparse.Namespace) -> None:
    ordinary_rows = read_csv(root / args.ordinary_csv)
    lodo_rows = read_csv(root / args.lodo_csv)
    ordinary = ordinary_rows[0] if ordinary_rows else {}
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# {args.summary_title}",
        "",
        f"Generated: {generated}, local time",
        "",
        args.purpose_text,
        "",
        "## Configuration",
        "",
        f"- Train images per domain: `{args.train_per_domain}`",
        f"- Validation images per domain: `{args.val_per_domain}`",
        f"- Epochs: `{args.epochs}`",
        f"- Image size: `{args.imgsz}`",
        f"- Batch: `{args.batch}`",
        f"- Device: `{args.device}`",
        f"- Model: `{args.model}`",
        "",
        "## Ordinary Reference",
        "",
        "| Split | Precision | Recall | mAP50 | mAP50-95 |",
        "|---|---:|---:|---:|---:|",
    ]
    if ordinary:
        lines.append(
            "| Ordinary mixed-domain | {precision:.4f} | {recall:.4f} | {map50:.4f} | {map5095:.4f} |".format(
                precision=as_float(ordinary.get("precision_B", "")),
                recall=as_float(ordinary.get("recall_B", "")),
                map50=as_float(ordinary.get("mAP50_B", "")),
                map5095=as_float(ordinary.get("mAP50_95_B", "")),
            )
        )
    else:
        lines.append("| Ordinary mixed-domain | [missing] | [missing] | [missing] | [missing] |")
    lines.extend(
        [
            "",
            "## LODO Matrix",
            "",
            "| Held-out domain | Precision | Recall | mAP50 | mAP50-95 |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in lodo_rows:
        lines.append(
            "| {domain} | {precision:.4f} | {recall:.4f} | {map50:.4f} | {map5095:.4f} |".format(
                domain=row.get("heldout_domain", "unknown"),
                precision=as_float(row.get("precision_B", "")),
                recall=as_float(row.get("recall_B", "")),
                map50=as_float(row.get("mAP50_B", "")),
                map5095=as_float(row.get("mAP50_95_B", "")),
            )
        )
    if lodo_rows:
        mean_map50 = sum(as_float(row.get("mAP50_B", "")) for row in lodo_rows) / len(lodo_rows)
        mean_map5095 = sum(as_float(row.get("mAP50_95_B", "")) for row in lodo_rows) / len(lodo_rows)
        lines.extend(
            [
                "",
                "## Aggregate Signal",
                "",
                f"- Mean LODO mAP50: `{mean_map50:.4f}`",
                f"- Mean LODO mAP50-95: `{mean_map5095:.4f}`",
            ]
        )
        if ordinary:
            lines.append(
                f"- Ordinary mAP50 minus mean LODO mAP50: `{as_float(ordinary.get('mAP50_B', '')) - mean_map50:.4f}`"
            )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            f"- {args.boundary_text}",
            "- It is not full-scale performance evidence unless the manuscript is explicitly framed as a subset-scale benchmark.",
            "- Prediction export and calibration must be run on any baseline that is used in the manuscript.",
        ]
    )
    output = root / args.combined_summary
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.combined_summary}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the G3 ordinary-vs-LODO timing pilot.")
    parser.add_argument("--model", default="yolov8n.pt")
    parser.add_argument("--train-per-domain", type=int, default=160)
    parser.add_argument("--val-per-domain", type=int, default=68)
    parser.add_argument("--seed", type=int, default=20260512)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--imgsz", type=int, default=320)
    parser.add_argument("--batch", type=int, default=4)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--copy-mode", choices=["copy", "hardlink", "symlink"], default="copy")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--ordinary-root", default="data_processed/yolo_g3_timing_ordinary")
    parser.add_argument("--lodo-root", default="data_processed/yolo_g3_timing_lodo")
    parser.add_argument("--ordinary-project", default="outputs/yolo_g3_timing_ordinary")
    parser.add_argument("--lodo-project", default="outputs/yolo_g3_timing_lodo")
    parser.add_argument("--ordinary-csv", default="data_processed/yolo_g3_timing_ordinary_result.csv")
    parser.add_argument("--lodo-csv", default="data_processed/yolo_g3_timing_lodo_results.csv")
    parser.add_argument("--ordinary-summary", default="outputs/yolo_g3_timing_ordinary_summary.md")
    parser.add_argument("--lodo-summary", default="outputs/yolo_g3_timing_lodo_summary.md")
    parser.add_argument("--combined-summary", default="outputs/g3_timing_pilot_summary.md")
    parser.add_argument("--summary-title", default="G3 Timing Pilot Summary")
    parser.add_argument(
        "--purpose-text",
        default="Purpose: estimate runtime and verify fixed ordinary-vs-LODO baseline plumbing before paper-grade training. These results are subset-scale pilot evidence only.",
    )
    parser.add_argument("--boundary-text", default="This timing pilot can guide G3 scale decisions and code QA.")
    parser.add_argument("--domains", nargs="*", default=DOMAINS)
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--skip-train", action="store_true")
    args = parser.parse_args()

    root = project_root()
    py = sys.executable
    if not args.skip_build:
        build_ordinary = [
            py,
            "scripts/15_make_yolo_ordinary_subset.py",
            "--root",
            "data_raw/RDD2022_extracted",
            "--out",
            args.ordinary_root,
            "--max-train-per-domain",
            str(args.train_per_domain),
            "--max-val-per-domain",
            str(args.val_per_domain),
            "--seed",
            str(args.seed),
            "--copy-mode",
            args.copy_mode,
        ]
        if args.overwrite:
            build_ordinary.append("--overwrite")
        run(build_ordinary, root)

        build_lodo = [
            py,
            "scripts/11_make_lodo_subset_matrix.py",
            "--root",
            "data_raw/RDD2022_extracted",
            "--out-root",
            args.lodo_root,
            "--max-train-per-domain",
            str(args.train_per_domain),
            "--max-val",
            str(args.val_per_domain),
            "--seed",
            str(args.seed),
            "--copy-mode",
            args.copy_mode,
            "--domains",
            *args.domains,
        ]
        if args.overwrite:
            build_lodo.append("--overwrite")
        run(build_lodo, root)

    if not args.skip_train:
        ordinary = [
            py,
            "scripts/16_run_yolo_once.py",
            "--data",
            str(Path(args.ordinary_root) / "dataset.yaml"),
            "--model",
            args.model,
            "--project",
            args.ordinary_project,
            "--name",
            f"ordinary_pretrained_{args.epochs}epoch",
            "--epochs",
            str(args.epochs),
            "--imgsz",
            str(args.imgsz),
            "--batch",
            str(args.batch),
            "--workers",
            str(args.workers),
            "--device",
            args.device,
            "--csv",
            args.ordinary_csv,
            "--summary",
            args.ordinary_summary,
            "--title",
            "G3 Timing Ordinary Baseline Summary",
            "--boundary",
            "This is a fixed subset-scale timing pilot, not full paper-grade performance.",
        ]
        run(ordinary, root)

        lodo = [
            py,
            "scripts/13_run_g2_pretrained_smoke_matrix.py",
            "--subset-root",
            args.lodo_root,
            "--model",
            args.model,
            "--project",
            args.lodo_project,
            "--run-suffix",
            f"pretrained_{args.epochs}epoch",
            "--epochs",
            str(args.epochs),
            "--imgsz",
            str(args.imgsz),
            "--batch",
            str(args.batch),
            "--workers",
            str(args.workers),
            "--device",
            args.device,
            "--csv",
            args.lodo_csv,
            "--summary",
            args.lodo_summary,
            "--domains",
            *args.domains,
        ]
        run(lodo, root)

    write_combined_summary(root, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
