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
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


def source_lodo_root(domain: str, suite_prefix: str) -> Path:
    return ROOT / "data_processed" / "g4" / f"{suite_prefix}_lodo" / f"heldout_{domain}"


def source_weight_path(domain: str, suite_prefix: str, seed: int) -> Path:
    return (
        ROOT
        / "runs"
        / "detect"
        / "outputs"
        / "g4"
        / f"{suite_prefix}_lodo_train"
        / f"heldout_{domain}_yolov8s_seed{seed}_8ep_640px"
        / "weights"
        / "best.pt"
    )


def safe_link_or_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def image_files(path: Path) -> list[Path]:
    return [p for p in sorted(path.iterdir()) if p.is_file() and p.suffix.lower() in IMAGE_EXTS]


def count_images(dataset_root: Path, split: str) -> int:
    return len(image_files(dataset_root / "images" / split))


def count_boxes(label_dir: Path) -> int:
    total = 0
    for label_path in label_dir.glob("*.txt"):
        text = label_path.read_text(encoding="utf-8").strip()
        if text:
            total += len(text.splitlines())
    return total


def write_dataset_yaml(dataset_root: Path) -> None:
    yaml_text = (
        f"path: {dataset_root.as_posix()}\n"
        "train: images/train\n"
        "val: images/val\n"
        "names:\n"
        "  0: D00\n"
        "  1: D10\n"
        "  2: D20\n"
        "  3: D40\n"
    )
    (dataset_root / "dataset.yaml").write_text(yaml_text, encoding="utf-8")


def build_target_evidence_dataset(domain: str, suite_prefix: str, target_k: int, seed: int, overwrite: bool) -> Path:
    source_root = source_lodo_root(domain, suite_prefix)
    if not source_root.exists():
        raise FileNotFoundError(source_root)
    out_root = ROOT / "data_processed" / "r36_target_domain_evidence" / f"heldout_{domain}_targetk{target_k}_seed{seed}"
    manifest_path = out_root / "target_evidence_manifest.csv"
    if out_root.exists() and manifest_path.exists() and not overwrite:
        return out_root
    if out_root.exists() and overwrite:
        shutil.rmtree(out_root)

    rng = random.Random(seed + sum(ord(ch) for ch in domain))
    source_train = image_files(source_root / "images" / "train")
    target_val = image_files(source_root / "images" / "val")
    if target_k >= len(target_val):
        raise ValueError(f"target_k={target_k} leaves no target validation images for {domain}")
    target_train = sorted(rng.sample(target_val, target_k))
    target_train_names = {p.name for p in target_train}
    target_eval = [p for p in target_val if p.name not in target_train_names]

    rows: list[dict[str, object]] = []
    for image_path in source_train:
        label_path = source_root / "labels" / "train" / f"{image_path.stem}.txt"
        dst_image = out_root / "images" / "train" / image_path.name
        dst_label = out_root / "labels" / "train" / f"{image_path.stem}.txt"
        safe_link_or_copy(image_path, dst_image)
        if label_path.exists():
            safe_link_or_copy(label_path, dst_label)
        rows.append(
            {
                "split": "train",
                "role": "source_lodo_train",
                "domain": inferred_domain_from_name(image_path.name),
                "source_image": str(image_path),
                "dest_image": str(dst_image),
            }
        )

    for idx, image_path in enumerate(target_train):
        label_path = source_root / "labels" / "val" / f"{image_path.stem}.txt"
        target_stem = f"tcal_{idx:03d}_{domain}"
        dst_image = out_root / "images" / "train" / f"{target_stem}{image_path.suffix.lower()}"
        dst_label = out_root / "labels" / "train" / f"{target_stem}.txt"
        safe_link_or_copy(image_path, dst_image)
        if label_path.exists():
            safe_link_or_copy(label_path, dst_label)
        rows.append(
            {
                "split": "train",
                "role": "target_domain_calibration",
                "domain": domain,
                "source_image": str(image_path),
                "dest_image": str(dst_image),
            }
        )

    for image_path in target_eval:
        label_path = source_root / "labels" / "val" / f"{image_path.stem}.txt"
        dst_image = out_root / "images" / "val" / image_path.name
        dst_label = out_root / "labels" / "val" / f"{image_path.stem}.txt"
        safe_link_or_copy(image_path, dst_image)
        if label_path.exists():
            safe_link_or_copy(label_path, dst_label)
        rows.append(
            {
                "split": "val",
                "role": "target_domain_evaluation",
                "domain": domain,
                "source_image": str(image_path),
                "dest_image": str(dst_image),
            }
        )

    write_dataset_yaml(out_root)
    write_csv(rows, manifest_path)
    return out_root


def inferred_domain_from_name(name: str) -> str:
    for domain in DOMAINS:
        if f"_{domain}_" in name or name.startswith(f"{domain}_") or f"_{domain.split('_')[0]}_" in name:
            return domain
    if "United_States" in name:
        return "United_States"
    return "source"


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


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(rows: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def as_float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def baseline_by_domain(path: Path) -> dict[str, dict[str, str]]:
    rows = read_csv(path)
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        domain = str(row.get("heldout_domain") or row.get("domain") or "").strip()
        if domain:
            out[domain] = row
    return out


def train_one(args: argparse.Namespace, domain: str, target_k: int, baselines: dict[str, dict[str, str]]) -> dict[str, object]:
    from ultralytics import YOLO

    source_root = source_lodo_root(domain, args.suite_prefix)
    source_weight = source_weight_path(domain, args.suite_prefix, args.seed)
    if not source_weight.exists():
        raise FileNotFoundError(source_weight)
    dataset_root = build_target_evidence_dataset(
        domain=domain,
        suite_prefix=args.suite_prefix,
        target_k=target_k,
        seed=args.seed,
        overwrite=args.rebuild_dataset,
    )
    data_yaml = dataset_root / "dataset.yaml"
    project = ROOT / args.project
    name = f"heldout_{domain}_targetk{target_k}_yolov8s_ft{args.epochs}ep_seed{args.seed}_{args.imgsz}px"
    existing = results_csv_for(project, name)
    status = "existing"
    start = time.time()
    if existing is None or args.overwrite:
        print(
            f"Running R36 target evidence check: domain={domain} target_k={target_k} "
            f"weights={source_weight} data={data_yaml}",
            flush=True,
        )
        model = YOLO(str(source_weight))
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
    base = baselines.get(domain, {})
    base_map50 = as_float(base.get("mAP50_B", ""))
    ft_map50 = as_float(last.get("metrics/mAP50(B)", ""))
    delta = ft_map50 - base_map50
    recovery = ""
    ordinary_map = 0.3325
    if ordinary_map > base_map50:
        recovery = f"{delta / (ordinary_map - base_map50):.6f}"

    return {
        "domain": domain,
        "target_k": target_k,
        "status": status,
        "init": "source_lodo_best_yolov8s",
        "source_weight": str(source_weight.relative_to(ROOT)),
        "dataset_root": str(dataset_root.relative_to(ROOT)),
        "source_train_images": count_images(source_root, "train"),
        "target_train_images": target_k,
        "target_eval_images": count_images(dataset_root, "val"),
        "target_train_boxes": count_boxes(dataset_root / "labels" / "train") - count_boxes(source_root / "labels" / "train"),
        "target_eval_boxes": count_boxes(dataset_root / "labels" / "val"),
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "workers": args.workers,
        "device": args.device,
        "seed": args.seed,
        "elapsed_sec": f"{elapsed:.3f}",
        "baseline_lodo_mAP50_B": f"{base_map50:.6f}",
        "target_ft_mAP50_B": f"{ft_map50:.6f}",
        "delta_mAP50_B": f"{delta:.6f}",
        "ordinary_endpoint_mAP50_B": f"{ordinary_map:.6f}",
        "ordinary_gap_recovery_fraction": recovery,
        "precision_B": last.get("metrics/precision(B)", ""),
        "recall_B": last.get("metrics/recall(B)", ""),
        "mAP50_95_B": last.get("metrics/mAP50-95(B)", ""),
        "val_box_loss": last.get("val/box_loss", ""),
        "val_cls_loss": last.get("val/cls_loss", ""),
        "val_dfl_loss": last.get("val/dfl_loss", ""),
        "results_csv": str(existing.relative_to(ROOT)),
    }


def write_summary(rows: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(rows, key=lambda row: (str(row["domain"]), int(row["target_k"])))
    lines = [
        "# R36 Small Target-Domain Evidence Check",
        "",
        "This round fine-tunes each frozen YOLOv8s 640-image/source-domain LODO checkpoint with a small number of labelled images from the held-out target domain.",
        "The target-domain images used for local evidence are removed from the target evaluation split; results are therefore evaluated on the remaining target-domain images.",
        "The check is used to test whether limited local evidence changes the validation-boundary interpretation; it is not reported as a domain-adaptation leaderboard.",
        "",
        "| domain | target images | eval images | target boxes | baseline LODO mAP50 | target-evidence mAP50 | delta | gap recovery | precision | recall |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in ordered:
        recovery = row.get("ordinary_gap_recovery_fraction") or ""
        recovery_text = "" if recovery == "" else f"{float(recovery):.3f}"
        lines.append(
            f"| {row['domain']} | {int(row['target_train_images'])} | {int(row['target_eval_images'])} | "
            f"{int(row['target_train_boxes'])} | {float(row['baseline_lodo_mAP50_B']):.4f} | "
            f"{float(row['target_ft_mAP50_B']):.4f} | {float(row['delta_mAP50_B']):+.4f} | "
            f"{recovery_text} | {float(row['precision_B']):.4f} | {float(row['recall_B']):.4f} |"
        )
    if ordered:
        deltas = [float(row["delta_mAP50_B"]) for row in ordered]
        base = [float(row["baseline_lodo_mAP50_B"]) for row in ordered]
        ft = [float(row["target_ft_mAP50_B"]) for row in ordered]
        lines.extend(
            [
                "",
                "## Aggregate",
                "",
                f"- Mean baseline LODO mAP50: {sum(base) / len(base):.4f}.",
                f"- Mean target-evidence mAP50: {sum(ft) / len(ft):.4f}.",
                f"- Mean delta mAP50: {sum(deltas) / len(deltas):+.4f}.",
                f"- Improved domains: {sum(1 for d in deltas if d > 0)} of {len(deltas)}.",
                f"- Degraded domains: {sum(1 for d in deltas if d < 0)} of {len(deltas)}.",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite-prefix", default="r14lc640_yolov8s_seed20260512")
    parser.add_argument("--domains", nargs="+", default=DOMAINS)
    parser.add_argument("--target-ks", nargs="+", type=int, default=[20])
    parser.add_argument("--epochs", type=int, default=4)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--device", default="0")
    parser.add_argument("--seed", type=int, default=20260512)
    parser.add_argument("--project", default="outputs/r36/yolov8s_target_domain_evidence")
    parser.add_argument("--baseline-csv", default="data_processed/g4/r14lc640_yolov8s_seed20260512_lodo_results.csv")
    parser.add_argument("--csv", default="data_processed/r36_target_domain_evidence/r36_yolov8s_targetk20_results.csv")
    parser.add_argument("--summary", default="outputs/r36/r36_target_domain_evidence_summary.md")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--rebuild-dataset", action="store_true")
    args = parser.parse_args()

    os.environ["YOLO_CONFIG_DIR"] = str(ROOT / "UltralyticsConfig")
    os.environ["MPLCONFIGDIR"] = str(ROOT / ".mplconfig")

    csv_path = ROOT / args.csv
    summary_path = ROOT / args.summary
    rows: list[dict[str, object]] = [dict(row) for row in read_csv(csv_path)]
    done = {(str(row.get("domain")), int(row.get("target_k", 0))) for row in rows}
    baselines = baseline_by_domain(ROOT / args.baseline_csv)
    for domain in args.domains:
        for target_k in args.target_ks:
            key = (domain, target_k)
            if args.skip_existing and key in done:
                print(f"Skipping existing {domain} target_k={target_k}", flush=True)
                continue
            row = train_one(args, domain, target_k, baselines)
            rows = [
                old
                for old in rows
                if not (str(old.get("domain")) == domain and int(old.get("target_k", 0)) == target_k)
            ]
            rows.append(row)
            write_csv(rows, csv_path)
            write_summary(rows, summary_path)
            print(f"Wrote {csv_path}", flush=True)
            print(f"Wrote {summary_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
