from __future__ import annotations

import argparse
import subprocess
import sys
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a matrix of YOLO leave-one-domain-out subsets.")
    parser.add_argument("--root", default="data_raw/RDD2022_extracted")
    parser.add_argument("--out-root", default="data_processed/yolo_lodo_smoke")
    parser.add_argument("--max-train-per-domain", type=int, default=80)
    parser.add_argument("--max-val", type=int, default=240)
    parser.add_argument("--seed", type=int, default=20260512)
    parser.add_argument("--copy-mode", choices=["copy", "hardlink", "symlink"], default="copy")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--domains", nargs="*", default=DOMAINS)
    args = parser.parse_args()

    script = Path(__file__).with_name("08_make_yolo_subset.py")
    out_root = Path(args.out_root)
    for domain in args.domains:
        out_dir = out_root / f"heldout_{domain}"
        command = [
            sys.executable,
            str(script),
            "--root",
            args.root,
            "--out",
            str(out_dir),
            "--heldout-domain",
            domain,
            "--max-train-per-domain",
            str(args.max_train_per_domain),
            "--max-val",
            str(args.max_val),
            "--seed",
            str(args.seed),
            "--copy-mode",
            args.copy_mode,
        ]
        if args.overwrite:
            command.append("--overwrite")
        print("Running:", " ".join(command))
        completed = subprocess.run(command, check=False)
        if completed.returncode != 0:
            return completed.returncode
    print(f"Built {len(args.domains)} leave-one-domain-out YOLO subsets under {out_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
