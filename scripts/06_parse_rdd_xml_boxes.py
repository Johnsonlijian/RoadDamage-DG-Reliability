from __future__ import annotations

import argparse
import csv
import sys
import xml.etree.ElementTree as ET
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


def infer_domain(path: Path, root: Path) -> str:
    for part in path.relative_to(root).parts:
        if part in KNOWN_DOMAINS:
            return "Czech_Republic" if part == "Czech" else part
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


def infer_image_path(xml_path: Path) -> str:
    parts = list(xml_path.parts)
    try:
        ann_index = next(i for i, part in enumerate(parts) if part.lower() in {"annotations", "annotation"})
        parts[ann_index] = "images"
        if ann_index + 1 < len(parts) and parts[ann_index + 1].lower() == "xmls":
            del parts[ann_index + 1]
        candidate = Path(*parts).with_suffix(".jpg")
        return str(candidate)
    except StopIteration:
        return str(xml_path.with_suffix(".jpg"))


def parse_xml(path: Path) -> tuple[int | None, int | None, list[dict[str, str | int | float]]]:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return None, None, []
    width_text = root.findtext("size/width")
    height_text = root.findtext("size/height")
    width = int(float(width_text)) if width_text else None
    height = int(float(height_text)) if height_text else None
    boxes = []
    for obj in root.findall("object"):
        label = (obj.findtext("name") or "").strip()
        bnd = obj.find("bndbox")
        if not label or bnd is None:
            continue
        try:
            xmin = float(bnd.findtext("xmin") or 0)
            ymin = float(bnd.findtext("ymin") or 0)
            xmax = float(bnd.findtext("xmax") or 0)
            ymax = float(bnd.findtext("ymax") or 0)
        except ValueError:
            continue
        row: dict[str, str | int | float] = {
            "label": label,
            "xmin": xmin,
            "ymin": ymin,
            "xmax": xmax,
            "ymax": ymax,
        }
        if width and height and width > 0 and height > 0:
            row.update(
                {
                    "x_center_norm": ((xmin + xmax) / 2) / width,
                    "y_center_norm": ((ymin + ymax) / 2) / height,
                    "width_norm": (xmax - xmin) / width,
                    "height_norm": (ymax - ymin) / height,
                }
            )
        boxes.append(row)
    return width, height, boxes


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse RDD2022 Pascal VOC XML boxes into CSV.")
    parser.add_argument("--root", required=True, help="Extracted RDD2022 root.")
    parser.add_argument("--boxes", required=True, help="Output box-level CSV.")
    parser.add_argument("--image-summary", required=True, help="Output image-level CSV.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"Root does not exist: {root}", file=sys.stderr)
        return 2
    xmls = sorted(root.rglob("*.xml"))
    box_path = Path(args.boxes)
    image_path = Path(args.image_summary)
    box_path.parent.mkdir(parents=True, exist_ok=True)
    image_path.parent.mkdir(parents=True, exist_ok=True)

    box_fields = [
        "xml_path",
        "image_path",
        "domain",
        "split",
        "width",
        "height",
        "label",
        "xmin",
        "ymin",
        "xmax",
        "ymax",
        "x_center_norm",
        "y_center_norm",
        "width_norm",
        "height_norm",
    ]
    image_fields = ["xml_path", "image_path", "domain", "split", "width", "height", "n_boxes"]
    with box_path.open("w", encoding="utf-8", newline="") as bf, image_path.open(
        "w", encoding="utf-8", newline=""
    ) as imf:
        box_writer = csv.DictWriter(bf, fieldnames=box_fields)
        image_writer = csv.DictWriter(imf, fieldnames=image_fields)
        box_writer.writeheader()
        image_writer.writeheader()
        for xml in xmls:
            width, height, boxes = parse_xml(xml)
            image = infer_image_path(xml)
            domain = infer_domain(xml, root)
            split = infer_split(xml)
            image_writer.writerow(
                {
                    "xml_path": str(xml),
                    "image_path": image,
                    "domain": domain,
                    "split": split,
                    "width": width,
                    "height": height,
                    "n_boxes": len(boxes),
                }
            )
            for box in boxes:
                box_writer.writerow(
                    {
                        "xml_path": str(xml),
                        "image_path": image,
                        "domain": domain,
                        "split": split,
                        "width": width,
                        "height": height,
                        **box,
                    }
                )
    print(f"Parsed {len(xmls)} XML files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

