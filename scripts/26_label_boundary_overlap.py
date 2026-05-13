from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


PRIMARY_LABELS = {"D00", "D10", "D20", "D40"}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def original_stem_from_prediction(row: dict[str, str]) -> str:
    image_id = row.get("image_id", "") or Path(row.get("image_path", "")).stem
    domain = row.get("domain", "")
    if domain:
        pattern = rf"^\d+_{re.escape(domain)}_"
        stripped = re.sub(pattern, "", image_id)
        if stripped != image_id:
            return stripped
    return re.sub(r"^\d+_[A-Za-z_]+?_", "", image_id)


def original_stem_from_box(row: dict[str, str]) -> str:
    return Path(row.get("image_path", "")).stem


def iou(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    inter = iw * ih
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    denom = area_a + area_b - inter
    return inter / denom if denom > 0 else 0.0


def pred_box(row: dict[str, str]) -> tuple[float, float, float, float]:
    return (
        as_float(row.get("pred_xmin", "")),
        as_float(row.get("pred_ymin", "")),
        as_float(row.get("pred_xmax", "")),
        as_float(row.get("pred_ymax", "")),
    )


def xml_box(row: dict[str, str]) -> tuple[float, float, float, float]:
    return (
        as_float(row.get("xmin", "")),
        as_float(row.get("ymin", "")),
        as_float(row.get("xmax", "")),
        as_float(row.get("ymax", "")),
    )


def non_primary_box_index(box_rows: list[dict[str, str]], primary_labels: set[str]) -> dict[tuple[str, str], list[dict[str, str]]]:
    index: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in box_rows:
        if row.get("label") in primary_labels:
            continue
        key = (row.get("domain", ""), original_stem_from_box(row))
        index[key].append(row)
    return index


def summarize(
    prediction_rows: list[dict[str, str]],
    boxes_by_image: dict[tuple[str, str], list[dict[str, str]]],
    thresholds: list[float],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    fp_rows = [row for row in prediction_rows if row.get("outcome") == "FP" and row.get("pred_id")]
    annotated: list[dict[str, str]] = []
    summary_rows: list[dict[str, str]] = []
    label_counts_by_threshold: dict[float, Counter[str]] = {threshold: Counter() for threshold in thresholds}
    overlap_counts = {threshold: 0 for threshold in thresholds}
    domain_counts: dict[float, Counter[str]] = {threshold: Counter() for threshold in thresholds}

    for row in fp_rows:
        key = (row.get("domain", ""), original_stem_from_prediction(row))
        candidates = boxes_by_image.get(key, [])
        pbox = pred_box(row)
        best_label = ""
        best_iou = 0.0
        for box in candidates:
            overlap = iou(pbox, xml_box(box))
            if overlap > best_iou:
                best_iou = overlap
                best_label = box.get("label", "")
        annotated.append(
            {
                "image_id": row.get("image_id", ""),
                "domain": row.get("domain", ""),
                "pred_class": row.get("pred_class", ""),
                "confidence": row.get("confidence", ""),
                "best_non_primary_label": best_label,
                "best_non_primary_iou": f"{best_iou:.6f}",
            }
        )
        for threshold in thresholds:
            if best_iou >= threshold:
                overlap_counts[threshold] += 1
                label_counts_by_threshold[threshold][best_label or "unknown"] += 1
                domain_counts[threshold][row.get("domain", "unknown")] += 1

    total_fp = len(fp_rows)
    for threshold in thresholds:
        labels = "; ".join(f"{label}:{count}" for label, count in label_counts_by_threshold[threshold].most_common())
        domains = "; ".join(f"{domain}:{count}" for domain, count in domain_counts[threshold].most_common())
        count = overlap_counts[threshold]
        summary_rows.append(
            {
                "iou_threshold": f"{threshold:.3f}",
                "false_positive_predictions": str(total_fp),
                "fp_overlapping_non_primary_xml": str(count),
                "share_of_fp": f"{count / total_fp:.6f}" if total_fp else "0.000000",
                "non_primary_label_counts": labels,
                "domain_counts": domains,
            }
        )
    return summary_rows, annotated


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows: list[dict[str, str]], output: Path, args: argparse.Namespace) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Label-Boundary Overlap Summary",
        "",
        f"Generated: {generated}, local time",
        "",
        "## Configuration",
        "",
        f"- Prediction table: `{args.predictions}`",
        f"- XML box table: `{args.boxes}`",
        f"- Primary labels excluded from boundary boxes: `{', '.join(sorted(args.primary_labels))}`",
        "",
        "## False-Positive Overlap With Non-Primary XML Boxes",
        "",
        "| IoU threshold | FP predictions | FP overlapping non-primary XML | Share of FP | Non-primary labels | Domains |",
        "| ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {iou_threshold} | {false_positive_predictions} | {fp_overlapping_non_primary_xml} | {share_of_fp} | {non_primary_label_counts} | {domain_counts} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This post-processing audit asks whether predictions counted as false positives in the four-class task overlap labels that were present in XML but excluded from the supervised label set. It does not redefine the primary task and does not replace a full exclude-vs-merge training sensitivity study.",
        ]
    )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit false positives that overlap non-primary XML label boxes.")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--boxes", default="data_processed/rdd2022_boxes.csv")
    parser.add_argument("--primary-labels", nargs="*", default=sorted(PRIMARY_LABELS))
    parser.add_argument("--iou-thresholds", nargs="*", type=float, default=[0.1, 0.3, 0.5])
    parser.add_argument("--csv", required=True)
    parser.add_argument("--annotated-csv", default=None)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()

    primary_labels = set(args.primary_labels)
    box_index = non_primary_box_index(read_rows(Path(args.boxes)), primary_labels)
    summary_rows, annotated_rows = summarize(read_rows(Path(args.predictions)), box_index, args.iou_thresholds)
    write_csv(summary_rows, Path(args.csv))
    if args.annotated_csv:
        write_csv(annotated_rows, Path(args.annotated_csv))
    write_summary(summary_rows, Path(args.summary), args)
    print(f"Wrote {args.csv}")
    if args.annotated_csv:
        print(f"Wrote {args.annotated_csv}")
    print(f"Wrote {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
