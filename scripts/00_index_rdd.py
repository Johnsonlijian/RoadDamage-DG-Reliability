from __future__ import annotations

import argparse
import csv
import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}
ANNOT_EXTS = {".xml", ".txt", ".json"}


def infer_split(path: Path) -> str:
    parts = {p.lower() for p in path.parts}
    for name in ("train", "training", "val", "valid", "validation", "test", "testing"):
        if name in parts:
            return name
    return "unknown"


KNOWN_DOMAINS = {
    "china": "China",
    "china_drone": "China_Drone",
    "china_motorbike": "China_MotorBike",
    "czech": "Czech_Republic",
    "czech_republic": "Czech_Republic",
    "india": "India",
    "japan": "Japan",
    "norway": "Norway",
    "united_states": "United_States",
    "usa": "United_States",
    "us": "United_States",
}


def normalize_part(part: str) -> str:
    return part.strip().lower().replace("-", "_").replace(" ", "_")


def infer_domain(path: Path, root: Path) -> str:
    rel_parts = path.relative_to(root).parts
    normalized = [normalize_part(part) for part in rel_parts]
    for part in normalized:
        if part in KNOWN_DOMAINS:
            return KNOWN_DOMAINS[part]
    for part in rel_parts:
        cleaned = part.strip()
        lower = normalize_part(cleaned)
        if lower in {"images", "image", "imgs", "annotations", "annotation", "labels", "label"}:
            continue
        if lower in {"train", "training", "val", "valid", "validation", "test", "testing"}:
            continue
        return cleaned
    return "unknown"


def parse_pascal_xml(path: Path) -> tuple[int | None, int | None, list[str]]:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return None, None, []
    width = root.findtext("size/width")
    height = root.findtext("size/height")
    labels = []
    for obj in root.findall("object"):
        label = obj.findtext("name")
        if label:
            labels.append(label.strip())
    return int(width) if width else None, int(height) if height else None, labels


def parse_yolo_txt(path: Path) -> list[str]:
    labels = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        parts = line.strip().split()
        if parts:
            labels.append(parts[0])
    return labels


def build_annotation_index(root: Path) -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = defaultdict(list)
    for path in root.rglob("*"):
        if path.suffix.lower() in ANNOT_EXTS:
            index[path.stem].append(path)
    return index


def find_annotation(image: Path, ann_index: dict[str, list[Path]]) -> Path | None:
    stem = image.stem
    candidates = [p for p in ann_index.get(stem, []) if p != image]
    if not candidates:
        return None
    def score(p: Path) -> tuple[int, int]:
        same_parent = 0 if p.parent == image.parent else 1
        return same_parent, len(p.parts)
    return sorted(candidates, key=score)[0]


def parse_annotation(path: Path | None) -> tuple[int | None, int | None, list[str], str]:
    if path is None:
        return None, None, [], "missing"
    if path.suffix.lower() == ".xml":
        width, height, labels = parse_pascal_xml(path)
        return width, height, labels, "pascal_xml"
    if path.suffix.lower() == ".txt":
        labels = parse_yolo_txt(path)
        return None, None, labels, "yolo_txt"
    if path.suffix.lower() == ".json":
        return None, None, [], "json_unparsed"
    return None, None, [], "unknown"


def build_inventory(root: Path) -> list[dict[str, str | int | None]]:
    images = sorted(p for p in root.rglob("*") if p.suffix.lower() in IMAGE_EXTS)
    ann_index = build_annotation_index(root)
    rows = []
    for image in images:
        ann = find_annotation(image, ann_index)
        width, height, labels, ann_type = parse_annotation(ann)
        label_counts = Counter(labels)
        rows.append(
            {
                "image_path": str(image),
                "annotation_path": str(ann) if ann else "",
                "domain": infer_domain(image, root),
                "split": infer_split(image),
                "annotation_type": ann_type,
                "width": width,
                "height": height,
                "n_objects": len(labels),
                "labels": ";".join(labels),
                "label_counts_json": json.dumps(dict(label_counts), ensure_ascii=False, sort_keys=True),
            }
        )
    return rows


def write_csv(rows: list[dict[str, str | int | None]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "image_path",
        "annotation_path",
        "domain",
        "split",
        "annotation_type",
        "width",
        "height",
        "n_objects",
        "labels",
        "label_counts_json",
    ]
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows: list[dict[str, str | int | None]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    by_domain = Counter(str(row["domain"]) for row in rows)
    by_split = Counter(str(row["split"]) for row in rows)
    by_ann_type = Counter(str(row["annotation_type"]) for row in rows)
    labels = Counter()
    for row in rows:
        for label in str(row["labels"]).split(";"):
            if label:
                labels[label] += 1
    lines = [
        "# RDD Inventory Summary",
        "",
        f"- Images indexed: {len(rows)}",
        "",
        "## By Domain",
        "",
    ]
    for key, value in sorted(by_domain.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## By Split", ""])
    for key, value in sorted(by_split.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## By Annotation Type", ""])
    for key, value in sorted(by_ann_type.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Labels", ""])
    for key, value in sorted(labels.items()):
        lines.append(f"- {key}: {value}")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Index RDD-style road damage datasets.")
    parser.add_argument("--root", required=True, help="Dataset root directory.")
    parser.add_argument("--csv", required=True, help="Output CSV path.")
    parser.add_argument("--summary", required=True, help="Output Markdown summary path.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"Dataset root does not exist: {root}", file=sys.stderr)
        return 2

    rows = build_inventory(root)
    write_csv(rows, Path(args.csv))
    write_summary(rows, Path(args.summary))
    print(f"Indexed {len(rows)} images from {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
