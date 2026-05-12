from __future__ import annotations

import argparse
import csv
import importlib.util
import random
import sys
from collections import defaultdict
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


def load_subset_module():
    module_path = Path(__file__).with_name("08_make_yolo_subset.py")
    spec = importlib.util.spec_from_file_location("yolo_subset_builder", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def select_ordinary_split(
    records: list[dict[str, object]],
    domains: list[str],
    max_train_per_domain: int,
    max_val_per_domain: int,
    seed: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rng = random.Random(seed)
    by_domain: dict[str, list[dict[str, object]]] = defaultdict(list)
    domain_set = set(domains)
    for record in records:
        domain = str(record["domain"])
        if domain not in domain_set:
            continue
        if record["image_exists"] and record["yolo_lines"]:
            by_domain[domain].append(record)

    train: list[dict[str, object]] = []
    val: list[dict[str, object]] = []
    for domain in domains:
        rows = by_domain.get(domain, [])[:]
        if len(rows) < max_train_per_domain + max_val_per_domain:
            raise ValueError(
                f"Domain {domain} has {len(rows)} usable rows, fewer than "
                f"{max_train_per_domain + max_val_per_domain} required."
            )
        rng.shuffle(rows)
        train.extend(rows[:max_train_per_domain])
        val.extend(rows[max_train_per_domain : max_train_per_domain + max_val_per_domain])
    rng.shuffle(train)
    rng.shuffle(val)
    return train, val


def write_ordinary_summary(
    out_dir: Path,
    root: Path,
    class_map: dict[str, int],
    train: list[dict[str, object]],
    val: list[dict[str, object]],
    copy_mode: str,
    max_train_per_domain: int,
    max_val_per_domain: int,
) -> None:
    train_by_domain: dict[str, int] = defaultdict(int)
    val_by_domain: dict[str, int] = defaultdict(int)
    for record in train:
        train_by_domain[str(record["domain"])] += 1
    for record in val:
        val_by_domain[str(record["domain"])] += 1
    lines = [
        "# YOLO Ordinary Split Subset Summary",
        "",
        f"- Source root: `{root}`",
        f"- Output: `{out_dir}`",
        f"- Copy mode: `{copy_mode}`",
        f"- Train images: `{len(train)}`",
        f"- Validation images: `{len(val)}`",
        f"- Max train per domain: `{max_train_per_domain}`",
        f"- Max validation per domain: `{max_val_per_domain}`",
        "",
        "## Classes",
        "",
    ]
    for name, idx in sorted(class_map.items(), key=lambda item: item[1]):
        lines.append(f"- {idx}: {name}")
    lines.extend(["", "## Domain Counts", ""])
    for domain in DOMAINS:
        lines.append(f"- {domain}: train={train_by_domain[domain]}, val={val_by_domain[domain]}")
    (out_dir / "subset_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a small all-domain ordinary YOLO split from RDD2022.")
    parser.add_argument("--root", required=True, help="Extracted RDD2022 root, or parent containing RDD2022.")
    parser.add_argument("--out", default="data_processed/yolo_ordinary_smoke")
    parser.add_argument("--label-map", default="data_raw/RDD2022_metadata/label_map.pbtxt")
    parser.add_argument("--max-train-per-domain", type=int, default=80)
    parser.add_argument("--max-val-per-domain", type=int, default=34)
    parser.add_argument("--seed", type=int, default=20260512)
    parser.add_argument("--copy-mode", choices=["copy", "hardlink", "symlink"], default="copy")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--domains", nargs="*", default=DOMAINS)
    args = parser.parse_args()

    subset = load_subset_module()
    root = Path(args.root).resolve()
    if not root.exists():
        print(f"Root does not exist: {root}", file=sys.stderr)
        return 2
    if (root / "RDD2022").exists():
        root = (root / "RDD2022").resolve()
    class_map = subset.parse_label_map(Path(args.label_map))
    records = subset.discover_records(root, class_map)
    train, val = select_ordinary_split(
        records,
        args.domains,
        args.max_train_per_domain,
        args.max_val_per_domain,
        args.seed,
    )
    out_dir = Path(args.out).resolve()
    subset.reset_output_dir(out_dir, args.overwrite)
    subset.ensure_clean_subset_dirs(out_dir)
    manifest_rows = []
    manifest_rows.extend(subset.materialize_subset(train, out_dir, "train", args.copy_mode, 0))
    manifest_rows.extend(subset.materialize_subset(val, out_dir, "val", args.copy_mode, len(train)))
    subset.write_dataset_yaml(out_dir, class_map)
    subset.write_manifest(manifest_rows, out_dir / "subset_manifest.csv")
    write_ordinary_summary(
        out_dir,
        root,
        class_map,
        train,
        val,
        args.copy_mode,
        args.max_train_per_domain,
        args.max_val_per_domain,
    )
    print(f"Created ordinary YOLO subset at {out_dir}; train={len(train)} val={len(val)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
