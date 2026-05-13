from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


BOUNDARY_SPECS = [
    ("YOLOv8n seed20260512", "ordinary", "g3_frozen_subset_ordinary"),
    ("YOLOv8n seed20260512", "lodo_all", "g3_frozen_subset_lodo_all"),
    ("YOLOv8n seed20260513", "ordinary", "g4a_r08_repeat_yolov8n_seed20260513_ordinary"),
    ("YOLOv8n seed20260513", "lodo_all", "g4a_r08_repeat_yolov8n_seed20260513_lodo_all"),
    ("YOLOv8n seed20260514", "ordinary", "g4a_r08_repeat_yolov8n_seed20260514_ordinary"),
    ("YOLOv8n seed20260514", "lodo_all", "g4a_r08_repeat_yolov8n_seed20260514_lodo_all"),
    ("YOLOv8s seed20260512", "ordinary", "g4b_bridge_yolov8s_seed20260512_ordinary"),
    ("YOLOv8s seed20260512", "lodo_all", "g4b_bridge_yolov8s_seed20260512_lodo_all"),
    ("YOLOv8s seed20260513", "ordinary", "g4b_bridge_yolov8s_seed20260513_ordinary"),
    ("YOLOv8s seed20260513", "lodo_all", "g4b_bridge_yolov8s_seed20260513_lodo_all"),
    ("YOLOv8s seed20260514", "ordinary", "g4b_bridge_yolov8s_seed20260514_ordinary"),
    ("YOLOv8s seed20260514", "lodo_all", "g4b_bridge_yolov8s_seed20260514_lodo_all"),
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def fmt(value: object, digits: int = 4) -> str:
    try:
        val = float(value)
    except (TypeError, ValueError):
        return str(value)
    if pd.isna(val):
        return "NA"
    return f"{val:.{digits}f}"


def markdown_table(df: pd.DataFrame, columns: list[str], digits: int = 4) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in df[columns].iterrows():
        lines.append("| " + " | ".join(fmt(row[col], digits) for col in columns) + " |")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize G4 label-boundary overlap CSVs.")
    parser.add_argument("--data-out-dir", default="data_processed/g4")
    parser.add_argument("--out-dir", default="outputs/g4")
    args = parser.parse_args()

    root = project_root()
    rows: list[dict[str, object]] = []
    missing: list[str] = []
    for model_label, split, prefix in BOUNDARY_SPECS:
        path = root / "data_processed" / "calibration" / f"{prefix}_label_boundary_overlap.csv"
        if not path.exists():
            missing.append(str(path.relative_to(root)))
            continue
        df = pd.read_csv(path)
        for _, row in df.iterrows():
            rec = row.to_dict()
            rec.update(
                {
                    "model_label": model_label,
                    "split": split,
                    "source_csv": str(path.relative_to(root)),
                }
            )
            rows.append(rec)

    out_dir = root / args.out_dir
    data_out_dir = root / args.data_out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    data_out_dir.mkdir(parents=True, exist_ok=True)

    summary = pd.DataFrame(rows)
    if not summary.empty:
        summary["iou_threshold_num"] = pd.to_numeric(summary["iou_threshold"], errors="coerce")
        summary["share_of_fp_num"] = pd.to_numeric(summary["share_of_fp"], errors="coerce")
        summary = summary.sort_values(["model_label", "split", "iou_threshold_num"])
        summary.drop(columns=["iou_threshold_num", "share_of_fp_num"], inplace=True)
    summary.to_csv(data_out_dir / "g4_label_boundary_overlap_summary.csv", index=False)

    lines = [
        "# G4 Label-Boundary Overlap Summary",
        "",
        "Boundary: this is post-processing of false-positive prediction rows against non-primary XML boxes. It does not merge labels, retrain a detector, or define an alternative benchmark task.",
        "",
    ]
    if summary.empty:
        lines.extend(["No label-boundary overlap CSVs were found.", ""])
    else:
        view = summary[
            [
                "model_label",
                "split",
                "iou_threshold",
                "false_positive_predictions",
                "fp_overlapping_non_primary_xml",
                "share_of_fp",
                "non_primary_label_counts",
                "domain_counts",
            ]
        ].copy()
        lines.extend(markdown_table(view, list(view.columns)))
        lines.extend(["", "## Compact Interpretation", ""])
        at_01 = summary[pd.to_numeric(summary["iou_threshold"], errors="coerce").round(3) == 0.1].copy()
        if not at_01.empty:
            at_01["share"] = pd.to_numeric(at_01["share_of_fp"], errors="coerce")
            max_row = at_01.sort_values("share", ascending=False).iloc[0]
            min_row = at_01.sort_values("share", ascending=True).iloc[0]
            lines.append(
                f"At IoU 0.100, the highest non-primary-overlap share is {fmt(max_row['share'])} for {max_row['model_label']} / {max_row['split']}; the lowest is {fmt(min_row['share'])} for {min_row['model_label']} / {min_row['split']}."
            )
            lines.append(
                "Across completed runs, non-primary XML labels explain a small but nonzero share of false positives; this supports label-boundary transparency rather than a claim that relabeling would solve the detector errors."
            )
    if missing:
        lines.extend(["", "## Missing Expected Files", ""])
        for path in missing:
            lines.append(f"- `{path}`")
    lines.extend(["", "## Output File", "", "- `data_processed/g4/g4_label_boundary_overlap_summary.csv`"])

    out_path = out_dir / "g4_label_boundary_overlap_summary.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
