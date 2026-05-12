from __future__ import annotations

import argparse
import csv
import math
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def parse_simple_yolo_yaml(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    names: dict[int, str] = {}
    in_names = False
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if re.match(r"^\s*names\s*:\s*$", line):
            in_names = True
            continue
        if in_names and re.match(r"^\s+\d+\s*:", line):
            key, value = line.split(":", 1)
            names[int(key.strip())] = value.strip().strip("'\"")
            continue
        in_names = False
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip("'\"")
    if names:
        data["names"] = names
    return data


def resolve_split_dir(dataset_yaml: Path, split: str) -> Path:
    config = parse_simple_yolo_yaml(dataset_yaml)
    base = Path(config.get("path", dataset_yaml.parent))
    if not base.is_absolute():
        base = (dataset_yaml.parent / base).resolve()
    split_value = config.get(split)
    if not split_value:
        raise ValueError(f"Dataset YAML lacks split field {split!r}: {dataset_yaml}")
    split_path = Path(split_value)
    return split_path if split_path.is_absolute() else (base / split_path).resolve()


def names_from_yaml(dataset_yaml: Path) -> dict[int, str]:
    config = parse_simple_yolo_yaml(dataset_yaml)
    names = config.get("names", {})
    if not names:
        raise ValueError(f"Dataset YAML lacks class names: {dataset_yaml}")
    return {int(k): str(v) for k, v in names.items()}


def list_images(split_dir: Path) -> list[Path]:
    return sorted(path for path in split_dir.rglob("*") if path.suffix.lower() in IMAGE_EXTENSIONS)


def infer_label_path(image_path: Path) -> Path:
    parts = list(image_path.parts)
    for i, part in enumerate(parts):
        if part.lower() == "images":
            parts[i] = "labels"
            return Path(*parts).with_suffix(".txt")
    return image_path.with_suffix(".txt")


def infer_domain(image_path: Path) -> str:
    stem = image_path.stem
    match = re.match(
        r"^\d+_(China_Drone|China_MotorBike|Czech_Republic|India|Japan|Norway|United_States)_",
        stem,
    )
    if match:
        return match.group(1)
    for part in image_path.parts:
        if part in {
            "China_Drone",
            "China_MotorBike",
            "Czech_Republic",
            "India",
            "Japan",
            "Norway",
            "United_States",
        }:
            return part
    return "unknown"


def yolo_to_xyxy(values: list[float], width: int, height: int) -> tuple[float, float, float, float]:
    x_c, y_c, box_w, box_h = values
    xmin = (x_c - box_w / 2.0) * width
    ymin = (y_c - box_h / 2.0) * height
    xmax = (x_c + box_w / 2.0) * width
    ymax = (y_c + box_h / 2.0) * height
    return xmin, ymin, xmax, ymax


def parse_label_file(label_path: Path, width: int, height: int, names: dict[int, str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not label_path.exists():
        return rows
    for idx, line in enumerate(label_path.read_text(encoding="utf-8", errors="ignore").splitlines()):
        parts = line.split()
        if len(parts) < 5:
            continue
        class_id = int(float(parts[0]))
        coords = [float(value) for value in parts[1:5]]
        xmin, ymin, xmax, ymax = yolo_to_xyxy(coords, width, height)
        rows.append(
            {
                "gt_id": f"gt_{idx:04d}",
                "gt_class_id": class_id,
                "gt_class": names.get(class_id, str(class_id)),
                "gt_xmin": xmin,
                "gt_ymin": ymin,
                "gt_xmax": xmax,
                "gt_ymax": ymax,
            }
        )
    return rows


def iou(box_a: tuple[float, float, float, float], box_b: tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
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


def safe_float(value: Any) -> float:
    try:
        if hasattr(value, "item"):
            return float(value.item())
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def prediction_rows(result: Any, names: dict[int, str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    boxes = getattr(result, "boxes", None)
    if boxes is None or len(boxes) == 0:
        return rows
    xyxy = boxes.xyxy.cpu().numpy()
    confs = boxes.conf.cpu().numpy()
    classes = boxes.cls.cpu().numpy()
    for idx, (box, conf, cls_id) in enumerate(zip(xyxy, confs, classes)):
        class_id = int(cls_id)
        rows.append(
            {
                "pred_id": f"pred_{idx:04d}",
                "pred_class_id": class_id,
                "pred_class": names.get(class_id, str(class_id)),
                "confidence": safe_float(conf),
                "pred_xmin": float(box[0]),
                "pred_ymin": float(box[1]),
                "pred_xmax": float(box[2]),
                "pred_ymax": float(box[3]),
            }
        )
    rows.sort(key=lambda row: row["confidence"], reverse=True)
    return rows


def match_image(
    image_path: Path,
    width: int,
    height: int,
    preds: list[dict[str, Any]],
    gts: list[dict[str, Any]],
    iou_threshold: float,
    split: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    matched_gt: set[int] = set()
    image_id = image_path.stem
    domain = infer_domain(image_path)
    for pred in preds:
        pred_box = (
            pred["pred_xmin"],
            pred["pred_ymin"],
            pred["pred_xmax"],
            pred["pred_ymax"],
        )
        best_idx = None
        best_iou = 0.0
        for gt_idx, gt in enumerate(gts):
            if gt_idx in matched_gt:
                continue
            if int(gt["gt_class_id"]) != int(pred["pred_class_id"]):
                continue
            gt_box = (gt["gt_xmin"], gt["gt_ymin"], gt["gt_xmax"], gt["gt_ymax"])
            overlap = iou(pred_box, gt_box)
            if overlap > best_iou:
                best_iou = overlap
                best_idx = gt_idx
        if best_idx is not None and best_iou >= iou_threshold:
            gt = gts[best_idx]
            matched_gt.add(best_idx)
            outcome = "TP"
            error_type = "matched"
        else:
            gt = {}
            outcome = "FP"
            error_type = "class_or_localization_or_background"
        rows.append(
            {
                "image_id": image_id,
                "image_path": str(image_path),
                "domain": domain,
                "split": split,
                "image_width": width,
                "image_height": height,
                "outcome": outcome,
                "error_type": error_type,
                "iou": f"{best_iou:.6f}",
                **pred,
                "gt_id": gt.get("gt_id", ""),
                "gt_class_id": gt.get("gt_class_id", ""),
                "gt_class": gt.get("gt_class", ""),
                "gt_xmin": gt.get("gt_xmin", ""),
                "gt_ymin": gt.get("gt_ymin", ""),
                "gt_xmax": gt.get("gt_xmax", ""),
                "gt_ymax": gt.get("gt_ymax", ""),
            }
        )
    for gt_idx, gt in enumerate(gts):
        if gt_idx in matched_gt:
            continue
        rows.append(
            {
                "image_id": image_id,
                "image_path": str(image_path),
                "domain": domain,
                "split": split,
                "image_width": width,
                "image_height": height,
                "outcome": "FN",
                "error_type": "missed_ground_truth",
                "iou": "",
                "pred_id": "",
                "pred_class_id": "",
                "pred_class": "",
                "confidence": "",
                "pred_xmin": "",
                "pred_ymin": "",
                "pred_xmax": "",
                "pred_ymax": "",
                **gt,
            }
        )
    return rows


def write_csv(rows: list[dict[str, Any]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "image_id",
        "image_path",
        "domain",
        "split",
        "image_width",
        "image_height",
        "outcome",
        "error_type",
        "iou",
        "pred_id",
        "pred_class_id",
        "pred_class",
        "confidence",
        "pred_xmin",
        "pred_ymin",
        "pred_xmax",
        "pred_ymax",
        "gt_id",
        "gt_class_id",
        "gt_class",
        "gt_xmin",
        "gt_ymin",
        "gt_xmax",
        "gt_ymax",
    ]
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, int]]:
    summary: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: {"TP": 0, "FP": 0, "FN": 0})
    for row in rows:
        domain = str(row["domain"])
        cls = str(row.get("pred_class") or row.get("gt_class") or "unknown")
        outcome = str(row["outcome"])
        if outcome in {"TP", "FP", "FN"}:
            summary[(domain, cls)][outcome] += 1
    return summary


def write_summary(rows: list[dict[str, Any]], output: Path, args: argparse.Namespace) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    n_tp = sum(1 for row in rows if row["outcome"] == "TP")
    n_fp = sum(1 for row in rows if row["outcome"] == "FP")
    n_fn = sum(1 for row in rows if row["outcome"] == "FN")
    precision = n_tp / (n_tp + n_fp) if (n_tp + n_fp) else 0.0
    recall = n_tp / (n_tp + n_fn) if (n_tp + n_fn) else 0.0
    lines = [
        "# YOLO Prediction Export Summary",
        "",
        f"Generated: {generated}, local time",
        "",
        "## Configuration",
        "",
        f"- Weights: `{args.weights}`",
        f"- Dataset YAML: `{args.data}`",
        f"- Split: `{args.split}`",
        f"- Image size: `{args.imgsz}`",
        f"- Confidence threshold: `{args.conf}`",
        f"- IoU matching threshold: `{args.iou_threshold}`",
        "",
        "## Overall Match Counts",
        "",
        "| TP | FP | FN | Precision | Recall |",
        "|---:|---:|---:|---:|---:|",
        f"| {n_tp} | {n_fp} | {n_fn} | {precision:.4f} | {recall:.4f} |",
        "",
        "## Domain-Class Counts",
        "",
        "| Domain | Class | TP | FP | FN |",
        "|---|---|---:|---:|---:|",
    ]
    for (domain, cls), counts in sorted(summarize(rows).items()):
        lines.append(f"| {domain} | {cls} | {counts['TP']} | {counts['FP']} | {counts['FN']} |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This export table is an analysis artifact. It supports calibration and failure-taxonomy calculations but does not by itself define paper-grade performance.",
        ]
    )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export YOLO predictions and IoU-matched TP/FP/FN rows.")
    parser.add_argument("--weights", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--split", default="val")
    parser.add_argument("--imgsz", type=int, default=320)
    parser.add_argument("--conf", type=float, default=0.001)
    parser.add_argument("--iou-threshold", type=float, default=0.5)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--max-images", type=int, default=0)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()

    from ultralytics import YOLO

    dataset_yaml = Path(args.data).resolve()
    split_dir = resolve_split_dir(dataset_yaml, args.split)
    names = names_from_yaml(dataset_yaml)
    images = list_images(split_dir)
    if args.max_images > 0:
        images = images[: args.max_images]
    if not images:
        raise FileNotFoundError(f"No images found in split directory: {split_dir}")

    model = YOLO(str(Path(args.weights).resolve()))
    all_rows: list[dict[str, Any]] = []
    result_stream = model.predict(
        source=[str(path) for path in images],
        imgsz=args.imgsz,
        conf=args.conf,
        device=args.device,
        verbose=False,
        stream=True,
    )
    for image_path, result in zip(images, result_stream):
        image_path = image_path.resolve()
        orig_shape = getattr(result, "orig_shape", None)
        if orig_shape and len(orig_shape) == 2:
            height, width = int(orig_shape[0]), int(orig_shape[1])
        else:
            from PIL import Image

            with Image.open(image_path) as image:
                width, height = image.size
        label_path = infer_label_path(image_path)
        gts = parse_label_file(label_path, width, height, names)
        preds = prediction_rows(result, names)
        all_rows.extend(match_image(image_path, width, height, preds, gts, args.iou_threshold, args.split))

    write_csv(all_rows, Path(args.csv))
    write_summary(all_rows, Path(args.summary), args)
    print(f"Wrote {args.csv}")
    print(f"Wrote {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
