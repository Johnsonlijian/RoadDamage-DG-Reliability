from __future__ import annotations

import argparse
import csv
import os
import random
import shutil
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOMAINS = [
    "China_Drone",
    "China_MotorBike",
    "Czech_Republic",
    "India",
    "Japan",
    "Norway",
    "United_States",
]
SETTINGS = ["ordinary"] + [f"heldout_{domain}" for domain in DOMAINS]


def dataset_root_for_setting(suite_prefix: str, setting: str) -> Path:
    if setting == "ordinary":
        return ROOT / "data_processed" / "g4" / f"{suite_prefix}_ordinary"
    if setting.startswith("heldout_"):
        return ROOT / "data_processed" / "g4" / f"{suite_prefix}_lodo" / setting
    raise ValueError(setting)


def safe_stem(text: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in Path(text).stem)


def run_dir(project: Path, name: str) -> Path:
    return project / name


def results_csv_for(project: Path, name: str) -> Path | None:
    candidates = [
        project / name / "results.csv",
        ROOT / "runs" / "detect" / project / name / "results.csv",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def read_last_result(results_csv: Path) -> dict[str, str]:
    with results_csv.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"Empty results file: {results_csv}")
    return {str(k).strip(): str(v).strip() for k, v in rows[-1].items()}


def existing_rows(csv_path: Path) -> list[dict[str, str]]:
    if not csv_path.exists():
        return []
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(rows: list[dict[str, object]], csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def as_float(row: dict[str, object], key: str) -> float:
    try:
        return float(row[key])
    except (KeyError, TypeError, ValueError):
        return 0.0


def as_int(row: dict[str, object], key: str) -> int:
    try:
        return int(float(row[key]))
    except (KeyError, TypeError, ValueError):
        return 0


def write_summary(rows: list[dict[str, object]], summary_path: Path) -> None:
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# R34 RT-DETR-L 640-Subset LODO Validation Summary",
        "",
        "This summary reports an Ultralytics RT-DETR-L transformer-family check on the frozen 640-image/source-domain subsets.",
        "The run is a detector-family reliability check, not a tuned detector leaderboard.",
        "",
        "| setting | train images | val images | epochs | imgsz | batch | mAP50 | precision | recall | mAP50-95 | elapsed sec |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['setting']} | {as_int(row, 'train_images')} | {as_int(row, 'val_images')} | "
            f"{as_int(row, 'epochs')} | {as_int(row, 'imgsz')} | {as_int(row, 'batch')} | "
            f"{as_float(row, 'mAP50_B'):.4f} | {as_float(row, 'precision_B'):.4f} | "
            f"{as_float(row, 'recall_B'):.4f} | {as_float(row, 'mAP50_95_B'):.4f} | "
            f"{as_float(row, 'elapsed_sec'):.1f} |"
        )
    ordinary = [row for row in rows if row.get("setting") == "ordinary"]
    lodo = [row for row in rows if str(row.get("setting")).startswith("heldout_")]
    lines.extend(["", "## Ordinary vs mean LODO", ""])
    lines.append("| ordinary mAP50 | mean LODO mAP50 | gap | n LODO | weakest LODO domain | weakest mAP50 |")
    lines.append("| ---: | ---: | ---: | ---: | --- | ---: |")
    if ordinary and lodo:
        ordinary_map = as_float(ordinary[0], "mAP50_B")
        mean_lodo = sum(as_float(row, "mAP50_B") for row in lodo) / len(lodo)
        weak = min(lodo, key=lambda row: as_float(row, "mAP50_B"))
        lines.append(
            f"| {ordinary_map:.4f} | {mean_lodo:.4f} | {ordinary_map - mean_lodo:.4f} | "
            f"{len(lodo)} | {str(weak['setting']).replace('heldout_', '')} | {as_float(weak, 'mAP50_B'):.4f} |"
        )
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def count_images(dataset_root: Path, split: str) -> int:
    image_dir = dataset_root / "images" / split
    exts = {".jpg", ".jpeg", ".png"}
    return sum(1 for p in image_dir.iterdir() if p.suffix.lower() in exts)


def maybe_make_sample_dataset(dataset_root: Path, setting: str, max_train: int | None, max_val: int | None, seed: int) -> Path:
    if max_train is None and max_val is None:
        return dataset_root
    out_root = ROOT / "data_processed" / "r34_rtdetr_sampled" / f"{setting}_train{max_train or 'all'}_val{max_val or 'all'}"
    if out_root.exists():
        return out_root
    rng = random.Random(seed)
    exts = {".jpg", ".jpeg", ".png"}
    for split, max_count in [("train", max_train), ("val", max_val)]:
        src_img = dataset_root / "images" / split
        src_lbl = dataset_root / "labels" / split
        dst_img = out_root / "images" / split
        dst_lbl = out_root / "labels" / split
        dst_img.mkdir(parents=True, exist_ok=True)
        dst_lbl.mkdir(parents=True, exist_ok=True)
        images = [p for p in sorted(src_img.iterdir()) if p.suffix.lower() in exts]
        if max_count is not None and max_count < len(images):
            images = sorted(rng.sample(images, max_count))
        for image_path in images:
            dst_image = dst_img / image_path.name
            if not dst_image.exists():
                try:
                    os.link(image_path, dst_image)
                except OSError:
                    shutil.copy2(image_path, dst_image)
            label_path = src_lbl / f"{image_path.stem}.txt"
            if label_path.exists():
                dst_label = dst_lbl / label_path.name
                if not dst_label.exists():
                    try:
                        os.link(label_path, dst_label)
                    except OSError:
                        shutil.copy2(label_path, dst_label)
    yaml_text = (
        f"path: {out_root.as_posix()}\n"
        "train: images/train\n"
        "val: images/val\n"
        "names:\n"
        "  0: D00\n"
        "  1: D10\n"
        "  2: D20\n"
        "  3: D40\n"
    )
    (out_root / "dataset.yaml").write_text(yaml_text, encoding="utf-8")
    return out_root


def train_setting(args: argparse.Namespace, setting: str) -> dict[str, object]:
    from ultralytics import RTDETR

    source_root = dataset_root_for_setting(args.suite_prefix, setting)
    dataset_root = maybe_make_sample_dataset(
        source_root,
        setting=setting,
        max_train=args.max_train_images,
        max_val=args.max_val_images,
        seed=args.seed,
    )
    data_yaml = dataset_root / "dataset.yaml"
    if not data_yaml.exists():
        raise FileNotFoundError(data_yaml)
    model_path = ROOT / args.model
    if not model_path.exists():
        RTDETR(args.model)
        downloaded = Path.cwd() / args.model
        if downloaded.exists() and downloaded.resolve() != model_path.resolve():
            shutil.move(str(downloaded), str(model_path))
    if not model_path.exists():
        raise FileNotFoundError(model_path)

    project = ROOT / args.project
    name = f"{safe_stem(args.model)}_{setting}_{args.epochs}ep_{args.imgsz}px"
    existing = results_csv_for(project, name)
    status = "existing"
    start = time.time()
    if existing is None or args.overwrite:
        model = RTDETR(str(model_path))
        print(f"Running RT-DETR {setting}: data={data_yaml} epochs={args.epochs} imgsz={args.imgsz} batch={args.batch}", flush=True)
        model.train(
            data=str(data_yaml),
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            workers=args.workers,
            device=args.device,
            project=str(project),
            name=name,
            exist_ok=True,
            plots=False,
            val=True,
            seed=args.seed,
            patience=0,
        )
        existing = results_csv_for(project, name)
        if existing is None:
            raise FileNotFoundError(f"Missing results.csv for {name}")
        status = "ran"
    elapsed = time.time() - start
    last = read_last_result(existing)
    return {
        "model_name": "rtdetr-l",
        "setting": setting,
        "status": status,
        "dataset_root": str(dataset_root.relative_to(ROOT)),
        "source_dataset_root": str(source_root.relative_to(ROOT)),
        "train_images": count_images(dataset_root, "train"),
        "val_images": count_images(dataset_root, "val"),
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "workers": args.workers,
        "device": args.device,
        "seed": args.seed,
        "elapsed_sec": elapsed,
        "final_epoch": last.get("epoch", ""),
        "train_box_loss": last.get("train/box_loss", ""),
        "train_cls_loss": last.get("train/cls_loss", ""),
        "train_dfl_loss": last.get("train/dfl_loss", ""),
        "precision_B": last.get("metrics/precision(B)", ""),
        "recall_B": last.get("metrics/recall(B)", ""),
        "mAP50_B": last.get("metrics/mAP50(B)", ""),
        "mAP50_95_B": last.get("metrics/mAP50-95(B)", ""),
        "val_box_loss": last.get("val/box_loss", ""),
        "val_cls_loss": last.get("val/cls_loss", ""),
        "val_dfl_loss": last.get("val/dfl_loss", ""),
        "results_csv": str(existing.relative_to(ROOT)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="rtdetr-l.pt")
    parser.add_argument("--suite-prefix", default="r14lc640_yolov8s_seed20260512")
    parser.add_argument("--settings", nargs="+", default=SETTINGS)
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=2)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--device", default="0")
    parser.add_argument("--seed", type=int, default=20260512)
    parser.add_argument("--max-train-images", type=int, default=None)
    parser.add_argument("--max-val-images", type=int, default=None)
    parser.add_argument("--project", default="outputs/r34/rtdetr_l_640_train")
    parser.add_argument("--csv", default="data_processed/non_yolo/r34_rtdetr_l_8ep_640_lodo_results.csv")
    parser.add_argument("--summary", default="outputs/non_yolo/r34_rtdetr_l_8ep_640_lodo_summary.md")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    os.environ["YOLO_CONFIG_DIR"] = str(ROOT / "UltralyticsConfig")
    os.environ["MPLCONFIGDIR"] = str(ROOT / ".mplconfig")

    csv_path = ROOT / args.csv
    summary_path = ROOT / args.summary
    rows: list[dict[str, object]] = [dict(row) for row in existing_rows(csv_path)]
    done = {str(row.get("setting")) for row in rows if row.get("setting")}
    for setting in args.settings:
        if args.skip_existing and setting in done:
            print(f"Skipping existing {setting}", flush=True)
            continue
        row = train_setting(args, setting)
        rows = [old for old in rows if str(old.get("setting")) != setting]
        rows.append(row)
        write_csv(rows, csv_path)
        write_summary(rows, summary_path)
        print(f"Wrote {csv_path}", flush=True)
        print(f"Wrote {summary_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
