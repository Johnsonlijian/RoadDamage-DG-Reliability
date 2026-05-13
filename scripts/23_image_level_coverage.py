from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def summarize(rows: list[dict[str, str]], thresholds: list[float]) -> list[dict[str, str]]:
    images: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        image_id = row.get("image_id") or row.get("image_path") or "unknown"
        images[image_id].append(row)

    total_images = len(images)
    gt_positive_images = sum(
        1
        for image_rows in images.values()
        if any((r.get("outcome") or "").upper() in {"TP", "FN"} for r in image_rows)
    )
    pred_positive_images_full = sum(
        1
        for image_rows in images.values()
        if any((r.get("outcome") or "").upper() in {"TP", "FP"} for r in image_rows)
    )

    output: list[dict[str, str]] = []
    for threshold in thresholds:
        selected_images = 0
        selected_with_tp = 0
        selected_with_fp = 0
        gt_with_accepted_tp = 0
        gt_without_accepted_tp = 0
        accepted_predictions = 0

        for image_rows in images.values():
            accepted = [
                r
                for r in image_rows
                if (r.get("outcome") or "").upper() in {"TP", "FP"}
                and as_float(r.get("confidence", "")) >= threshold
            ]
            has_gt = any((r.get("outcome") or "").upper() in {"TP", "FN"} for r in image_rows)
            has_tp = any((r.get("outcome") or "").upper() == "TP" for r in accepted)
            has_fp = any((r.get("outcome") or "").upper() == "FP" for r in accepted)

            accepted_predictions += len(accepted)
            if accepted:
                selected_images += 1
            if has_tp:
                selected_with_tp += 1
            if has_fp:
                selected_with_fp += 1
            if has_gt and has_tp:
                gt_with_accepted_tp += 1
            if has_gt and not has_tp:
                gt_without_accepted_tp += 1

        image_review_coverage = selected_images / total_images if total_images else 0.0
        selected_image_tp_rate = selected_with_tp / selected_images if selected_images else 0.0
        selected_image_fp_flag_rate = selected_with_fp / selected_images if selected_images else 0.0
        gt_image_recall_proxy = gt_with_accepted_tp / gt_positive_images if gt_positive_images else 0.0
        gt_image_miss_proxy = gt_without_accepted_tp / gt_positive_images if gt_positive_images else 0.0

        output.append(
            {
                "threshold": f"{threshold:.3f}",
                "total_images": str(total_images),
                "gt_positive_images": str(gt_positive_images),
                "pred_positive_images_full": str(pred_positive_images_full),
                "selected_images": str(selected_images),
                "accepted_predictions": str(accepted_predictions),
                "image_review_coverage": f"{image_review_coverage:.6f}",
                "selected_image_tp_rate": f"{selected_image_tp_rate:.6f}",
                "selected_image_fp_flag_rate": f"{selected_image_fp_flag_rate:.6f}",
                "gt_image_recall_proxy": f"{gt_image_recall_proxy:.6f}",
                "gt_image_miss_proxy": f"{gt_image_miss_proxy:.6f}",
            }
        )
    return output


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows: list[dict[str, str]], path: Path, title: str, source: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# {title}",
        "",
        f"Generated: {generated}, local time",
        "",
        f"Source predictions: `{source}`",
        "",
        "This table converts prediction-row thresholding into an image-trigger proxy. It is closer to review workload than prediction-row coverage, but it is still not an agency work-order, road-segment, cost, or safety model.",
        "",
        "| Threshold | Selected images | Image review coverage | Selected-image TP rate | Selected-image FP flag rate | GT-image recall proxy |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {threshold} | {selected_images} | {image_review_coverage} | {selected_image_tp_rate} | {selected_image_fp_flag_rate} | {gt_image_recall_proxy} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Definitions",
            "",
            "- Image review coverage: fraction of validation images with at least one accepted prediction at the threshold.",
            "- Selected-image TP rate: among selected images, fraction with at least one accepted true-positive prediction.",
            "- Selected-image FP flag rate: among selected images, fraction with at least one accepted false-positive prediction.",
            "- GT-image recall proxy: fraction of ground-truth-positive images with at least one accepted true-positive prediction.",
            "",
            "## Boundary",
            "",
            "This is a post-processing workload proxy from existing prediction exports. It does not validate road-agency review cost, road-segment prioritization, or safety thresholds.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_thresholds(raw: str) -> list[float]:
    return [float(item.strip()) for item in raw.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute image-level threshold coverage from prediction exports.")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--title", default="Image-Level Coverage Summary")
    parser.add_argument("--thresholds", default="0,0.05,0.1,0.2,0.5")
    args = parser.parse_args()

    source = Path(args.predictions)
    rows = summarize(read_rows(source), parse_thresholds(args.thresholds))
    write_csv(rows, Path(args.csv))
    write_summary(rows, Path(args.summary), args.title, source)
    print(f"Wrote {args.csv}")
    print(f"Wrote {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
