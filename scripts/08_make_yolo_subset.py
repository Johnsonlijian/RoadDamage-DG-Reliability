from __future__ import annotations

import argparse
import csv
import os
import random
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


KNOWN_DOMAINS = {
    "China_Drone",
    "China_MotorBike",
    "Czech",
    "Czech_Republic",
    "India",
    "Japan",
    "Norway",
    "United_States",
}


def normalize_domain(domain: str) -> str:
    return "Czech_Republic" if domain == "Czech" else domain


def infer_domain(path: Path, root: Path) -> str:
    for part in path.relative_to(root).parts:
        if part in KNOWN_DOMAINS:
            return normalize_domain(part)
    return "unknown"


def infer_split(path: Path) -> str:
    lower_parts = {p.lower() for p in path.parts}
    if "train" in lower_parts:
        return "train"
    if "test" in lower_parts:
        return "test"
    if "val" in lower_parts or "valid" in lower_parts or "validation" in lower_parts:
        return "val"
    return "unknown"


def infer_image_path(xml_path: Path) -> Path:
    parts = list(xml_path.parts)
    for i, part in enumerate(parts):
        if part.lower() in {"annotations", "annotation"}:
            parts[i] = "images"
            if i + 1 < len(parts) and parts[i + 1].lower() == "xmls":
                del parts[i + 1]
            return Path(*parts).with_suffix(".jpg")
    return xml_path.with_suffix(".jpg")


def parse_label_map(path: Path) -> dict[str, int]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    entries = re.findall(r"id:\s*(\d+)\s+name:\s*'([^']+)'", text)
    if not entries:
        raise ValueError(f"No label_map entries found in {path}")
    return {name: int(raw_id) - 1 for raw_id, name in entries}


def parse_xml_boxes(
    xml_path: Path, class_map: dict[str, int]
) -> tuple[int | None, int | None, list[str], list[str], int, int]:
    try:
        root = ET.parse(xml_path).getroot()
    except ET.ParseError:
        return None, None, [], [], 0, 0
    width_text = root.findtext("size/width")
    height_text = root.findtext("size/height")
    if not width_text or not height_text:
        return None, None, [], [], 0, 0
    width = int(float(width_text))
    height = int(float(height_text))
    if width <= 0 or height <= 0:
        return width, height, [], [], 0, 0
    labels: list[str] = []
    yolo_lines: list[str] = []
    clipped = 0
    ignored = 0
    for obj in root.findall("object"):
        label = (obj.findtext("name") or "").strip()
        bnd = obj.find("bndbox")
        if not label or bnd is None:
            continue
        if label not in class_map:
            ignored += 1
            continue
        try:
            xmin = float(bnd.findtext("xmin") or 0)
            ymin = float(bnd.findtext("ymin") or 0)
            xmax = float(bnd.findtext("xmax") or 0)
            ymax = float(bnd.findtext("ymax") or 0)
        except ValueError:
            continue
        raw = (xmin, ymin, xmax, ymax)
        xmin = min(max(xmin, 0.0), float(width))
        xmax = min(max(xmax, 0.0), float(width))
        ymin = min(max(ymin, 0.0), float(height))
        ymax = min(max(ymax, 0.0), float(height))
        if raw != (xmin, ymin, xmax, ymax):
            clipped += 1
        box_w = xmax - xmin
        box_h = ymax - ymin
        if box_w <= 0 or box_h <= 0:
            continue
        x_center = ((xmin + xmax) / 2.0) / width
        y_center = ((ymin + ymax) / 2.0) / height
        yolo_w = box_w / width
        yolo_h = box_h / height
        labels.append(label)
        yolo_lines.append(
            f"{class_map[label]} {x_center:.8f} {y_center:.8f} {yolo_w:.8f} {yolo_h:.8f}"
        )
    return width, height, labels, yolo_lines, clipped, ignored


def discover_records(root: Path, class_map: dict[str, int]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for xml_path in sorted(root.rglob("*.xml")):
        split = infer_split(xml_path)
        if split != "train":
            continue
        image_path = infer_image_path(xml_path)
        domain = infer_domain(xml_path, root)
        width, height, labels, yolo_lines, clipped, ignored = parse_xml_boxes(xml_path, class_map)
        records.append(
            {
                "xml_path": xml_path,
                "image_path": image_path,
                "domain": domain,
                "split": split,
                "width": width,
                "height": height,
                "labels": labels,
                "yolo_lines": yolo_lines,
                "clipped": clipped,
                "ignored": ignored,
                "image_exists": image_path.exists(),
            }
        )
    return records


def select_records(
    records: list[dict[str, object]],
    heldout_domain: str,
    max_train_per_domain: int,
    max_val: int,
    seed: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rng = random.Random(seed)
    by_domain: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        if record["image_exists"] and record["yolo_lines"]:
            by_domain[str(record["domain"])].append(record)
    heldout_domain = normalize_domain(heldout_domain)
    if heldout_domain not in by_domain:
        raise ValueError(f"Held-out domain not found or has no usable XML/images: {heldout_domain}")
    train: list[dict[str, object]] = []
    for domain, domain_records in sorted(by_domain.items()):
        rng.shuffle(domain_records)
        if domain == heldout_domain:
            continue
        train.extend(domain_records[:max_train_per_domain])
    val_records = by_domain[heldout_domain][:]
    rng.shuffle(val_records)
    val = val_records[:max_val]
    return train, val


def ensure_clean_subset_dirs(out_dir: Path) -> None:
    for split in ("train", "val"):
        (out_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (out_dir / "labels" / split).mkdir(parents=True, exist_ok=True)


def reset_output_dir(out_dir: Path, overwrite: bool) -> None:
    generated_paths = [
        out_dir / "images",
        out_dir / "labels",
        out_dir / "dataset.yaml",
        out_dir / "subset_manifest.csv",
        out_dir / "subset_summary.md",
    ]
    existing = [path for path in generated_paths if path.exists()]
    if existing and not overwrite:
        names = ", ".join(str(path) for path in existing[:5])
        raise RuntimeError(
            f"Output directory already contains generated subset files: {names}. "
            "Use --overwrite to rebuild this generated subset."
        )
    if overwrite:
        for path in generated_paths:
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()


def copy_image(src: Path, dst: Path, mode: str) -> None:
    if dst.exists():
        return
    if mode == "copy":
        shutil.copy2(src, dst)
    elif mode == "hardlink":
        os.link(src, dst)
    elif mode == "symlink":
        os.symlink(src, dst)
    else:
        raise ValueError(f"Unsupported copy mode: {mode}")


def safe_stem(record: dict[str, object], index: int) -> str:
    domain = re.sub(r"[^A-Za-z0-9_]+", "_", str(record["domain"]))
    stem = re.sub(r"[^A-Za-z0-9_]+", "_", Path(record["image_path"]).stem)
    return f"{index:06d}_{domain}_{stem}"


def materialize_subset(
    rows: list[dict[str, object]],
    out_dir: Path,
    split: str,
    copy_mode: str,
    start_index: int,
) -> list[dict[str, str | int]]:
    manifest_rows: list[dict[str, str | int]] = []
    for offset, record in enumerate(rows):
        index = start_index + offset
        src_image = Path(record["image_path"])
        src_xml = Path(record["xml_path"])
        dest_stem = safe_stem(record, index)
        dest_image = out_dir / "images" / split / f"{dest_stem}{src_image.suffix.lower()}"
        dest_label = out_dir / "labels" / split / f"{dest_stem}.txt"
        copy_image(src_image, dest_image, copy_mode)
        dest_label.write_text("\n".join(record["yolo_lines"]) + "\n", encoding="utf-8")
        labels = list(record["labels"])
        manifest_rows.append(
            {
                "subset_split": split,
                "domain": str(record["domain"]),
                "source_image": str(src_image),
                "source_xml": str(src_xml),
                "dest_image": str(dest_image),
                "dest_label": str(dest_label),
                "n_boxes": len(labels),
                "labels": ";".join(labels),
                "n_clipped_boxes": int(record["clipped"]),
                "n_ignored_non_task_boxes": int(record["ignored"]),
            }
        )
    return manifest_rows


def write_dataset_yaml(out_dir: Path, class_map: dict[str, int]) -> None:
    names_by_id = {idx: name for name, idx in class_map.items()}
    lines = [
        f"path: {out_dir.resolve().as_posix()}",
        "train: images/train",
        "val: images/val",
        "names:",
    ]
    for idx in sorted(names_by_id):
        lines.append(f"  {idx}: {names_by_id[idx]}")
    (out_dir / "dataset.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifest(rows: list[dict[str, str | int]], output: Path) -> None:
    fieldnames = [
        "subset_split",
        "domain",
        "source_image",
        "source_xml",
        "dest_image",
        "dest_label",
        "n_boxes",
        "labels",
        "n_clipped_boxes",
        "n_ignored_non_task_boxes",
    ]
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(
    out_dir: Path,
    root: Path,
    heldout_domain: str,
    class_map: dict[str, int],
    train: list[dict[str, object]],
    val: list[dict[str, object]],
    all_records: list[dict[str, object]],
    copy_mode: str,
) -> None:
    by_domain: dict[str, int] = defaultdict(int)
    usable_by_domain: dict[str, int] = defaultdict(int)
    ignored_by_domain: dict[str, int] = defaultdict(int)
    for record in all_records:
        domain = str(record["domain"])
        by_domain[domain] += 1
        if record["image_exists"] and record["yolo_lines"]:
            usable_by_domain[domain] += 1
        ignored_by_domain[domain] += int(record["ignored"])
    lines = [
        "# YOLO Subset Summary",
        "",
        f"- Source root: `{root}`",
        f"- Output: `{out_dir}`",
        f"- Held-out validation domain: `{heldout_domain}`",
        f"- Copy mode: `{copy_mode}`",
        f"- Train images: `{len(train)}`",
        f"- Validation images: `{len(val)}`",
        "",
        "## Classes",
        "",
    ]
    for name, idx in sorted(class_map.items(), key=lambda item: item[1]):
        lines.append(f"- {idx}: {name}")
    lines.extend(["", "## XML Records By Domain", ""])
    for domain in sorted(by_domain):
        lines.append(
            f"- {domain}: {usable_by_domain[domain]} usable / {by_domain[domain]} XML; "
            f"ignored non-task boxes={ignored_by_domain[domain]}"
        )
    (out_dir / "subset_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a small YOLO sanity-check subset from extracted RDD2022.")
    parser.add_argument("--root", required=True, help="Extracted RDD2022 root, or parent containing RDD2022.")
    parser.add_argument("--out", default="data_processed/yolo_sanity_japan", help="Output YOLO subset directory.")
    parser.add_argument("--label-map", default="data_raw/RDD2022_metadata/label_map.pbtxt", help="RDD label_map.pbtxt.")
    parser.add_argument("--heldout-domain", default="Japan", help="Domain used as validation set.")
    parser.add_argument("--max-train-per-domain", type=int, default=80, help="Max training images per non-held-out domain.")
    parser.add_argument("--max-val", type=int, default=240, help="Max validation images from held-out domain.")
    parser.add_argument("--seed", type=int, default=20260512)
    parser.add_argument("--copy-mode", choices=["copy", "hardlink", "symlink"], default="copy")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite generated files in the output dir.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"Root does not exist: {root}", file=sys.stderr)
        return 2
    if (root / "RDD2022").exists():
        root = (root / "RDD2022").resolve()
    class_map = parse_label_map(Path(args.label_map))
    records = discover_records(root, class_map)
    train, val = select_records(records, args.heldout_domain, args.max_train_per_domain, args.max_val, args.seed)
    out_dir = Path(args.out).resolve()
    reset_output_dir(out_dir, args.overwrite)
    ensure_clean_subset_dirs(out_dir)
    manifest_rows = []
    manifest_rows.extend(materialize_subset(train, out_dir, "train", args.copy_mode, 0))
    manifest_rows.extend(materialize_subset(val, out_dir, "val", args.copy_mode, len(train)))
    write_dataset_yaml(out_dir, class_map)
    write_manifest(manifest_rows, out_dir / "subset_manifest.csv")
    write_summary(out_dir, root, normalize_domain(args.heldout_domain), class_map, train, val, records, args.copy_mode)
    print(f"Created YOLO subset at {out_dir}; train={len(train)} val={len(val)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
