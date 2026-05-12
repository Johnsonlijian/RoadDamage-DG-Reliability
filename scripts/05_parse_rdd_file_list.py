from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}
ANNOT_EXTS = {".xml", ".txt", ".json"}

KNOWN_DOMAINS = {
    "China": "China",
    "China_Drone": "China_Drone",
    "China_MotorBike": "China_MotorBike",
    "Czech": "Czech_Republic",
    "Czech_Republic": "Czech_Republic",
    "India": "India",
    "Japan": "Japan",
    "Norway": "Norway",
    "United_States": "United_States",
    "United States": "United_States",
    "USA": "United_States",
}


def normalize(part: str) -> str:
    return part.strip().replace("\\", "/")


def infer_domain(path: str) -> str:
    parts = [p for p in normalize(path).split("/") if p]
    for part in parts:
        key = part.strip()
        if key in KNOWN_DOMAINS:
            return KNOWN_DOMAINS[key]
        key2 = key.replace("-", "_").replace(" ", "_")
        if key2 in KNOWN_DOMAINS:
            return KNOWN_DOMAINS[key2]
    for part in parts:
        lower = part.lower()
        if lower not in {"train", "test", "images", "annotations", "xmls", "jpegimages"}:
            return part
    return "unknown"


def infer_split(path: str) -> str:
    lower_parts = {p.lower() for p in normalize(path).split("/")}
    if "train" in lower_parts or "training" in lower_parts:
        return "train"
    if "test" in lower_parts or "testing" in lower_parts:
        return "test"
    if "val" in lower_parts or "validation" in lower_parts or "valid" in lower_parts:
        return "val"
    return "unknown"


def infer_kind(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext in IMAGE_EXTS:
        return "image"
    if ext in ANNOT_EXTS:
        return "annotation_or_metadata"
    return "other"


def tree_level(line: str, marker_index: int) -> int:
    if marker_index <= 0:
        return 0
    return max(0, (marker_index - 1) // 4)


def extract_paths_from_tree(text: str) -> list[str]:
    paths: list[str] = []
    stack: list[str] = []
    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("Folder PATH") or stripped.startswith("Volume serial") or stripped == "C:.":
            continue
        marker_index = line.find("---")
        if marker_index >= 0:
            name = line[marker_index + 3 :].strip()
            level = tree_level(line, marker_index)
            stack = stack[:level]
            stack.append(name)
            if Path(name).suffix:
                paths.append("/".join(stack))
                stack.pop()
            continue
        name = stripped.lstrip("|").strip()
        if Path(name).suffix:
            paths.append("/".join(stack + [name]))
    return paths


def read_file_list(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    paths = extract_paths_from_tree(text)
    if paths:
        return paths
    return [line.strip() for line in text.splitlines() if line.strip()]


def write_inventory(paths: list[str], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["path", "kind", "domain", "split", "extension"]
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for path in paths:
            writer.writerow(
                {
                    "path": path,
                    "kind": infer_kind(path),
                    "domain": infer_domain(path),
                    "split": infer_split(path),
                    "extension": Path(path).suffix.lower(),
                }
            )


def write_summary(paths: list[str], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    kinds = Counter(infer_kind(p) for p in paths)
    domains = Counter(infer_domain(p) for p in paths if infer_kind(p) == "image")
    splits = Counter(infer_split(p) for p in paths if infer_kind(p) == "image")
    exts = Counter(Path(p).suffix.lower() or "[none]" for p in paths)
    lines = [
        "# RDD2022 File-List Summary",
        "",
        f"- Paths listed: {len(paths)}",
        "",
        "## Kinds",
        "",
    ]
    for key, value in sorted(kinds.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Image Domains", ""])
    for key, value in sorted(domains.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Image Splits", ""])
    for key, value in sorted(splits.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Extensions", ""])
    for key, value in sorted(exts.items()):
        lines.append(f"- {key}: {value}")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse RDD2022 file-list metadata without extracting the full zip.")
    parser.add_argument("--file-list", required=True, help="File_List_CRDDC_RDD2022.txt path.")
    parser.add_argument("--inventory", required=True, help="Output CSV path.")
    parser.add_argument("--summary", required=True, help="Output Markdown path.")
    args = parser.parse_args()

    paths = read_file_list(Path(args.file_list))
    write_inventory(paths, Path(args.inventory))
    write_summary(paths, Path(args.summary))
    print(f"Parsed {len(paths)} paths")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
