from __future__ import annotations

import argparse
import csv
import math
import random
import time
from dataclasses import dataclass
from pathlib import Path

import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision.models.detection import (
    FasterRCNN_MobileNet_V3_Large_320_FPN_Weights,
    fasterrcnn_mobilenet_v3_large_320_fpn,
)
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.ops import box_iou
from torchvision.transforms import functional as F


ROOT = Path(__file__).resolve().parents[1]
CLASS_NAMES = ["D00", "D10", "D20", "D40"]


@dataclass
class Prediction:
    image_id: int
    score: float
    box: torch.Tensor


class YoloDetectionDataset(Dataset):
    def __init__(self, dataset_root: Path, split: str, max_images: int | None = None, seed: int = 20260518):
        self.dataset_root = dataset_root
        self.split = split
        self.image_dir = dataset_root / "images" / split
        self.label_dir = dataset_root / "labels" / split
        exts = {".jpg", ".jpeg", ".png"}
        self.images = [p for p in sorted(self.image_dir.iterdir()) if p.suffix.lower() in exts]
        if max_images is not None and max_images < len(self.images):
            rng = random.Random(seed)
            self.images = sorted(rng.sample(self.images, max_images))

    def __len__(self) -> int:
        return len(self.images)

    def __getitem__(self, idx: int):
        image_path = self.images[idx]
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            width, height = img.size
            image = F.to_tensor(img)

        boxes = []
        labels = []
        label_path = self.label_dir / f"{image_path.stem}.txt"
        if label_path.exists():
            for line in label_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                cls, xc, yc, bw, bh = line.split()[:5]
                cls_i = int(cls)
                xc, yc, bw, bh = map(float, (xc, yc, bw, bh))
                x1 = max(0.0, (xc - bw / 2.0) * width)
                y1 = max(0.0, (yc - bh / 2.0) * height)
                x2 = min(float(width), (xc + bw / 2.0) * width)
                y2 = min(float(height), (yc + bh / 2.0) * height)
                if x2 > x1 and y2 > y1 and 0 <= cls_i < len(CLASS_NAMES):
                    boxes.append([x1, y1, x2, y2])
                    labels.append(cls_i + 1)  # Faster R-CNN reserves 0 for background.

        target = {
            "boxes": torch.tensor(boxes, dtype=torch.float32),
            "labels": torch.tensor(labels, dtype=torch.int64),
            "image_id": torch.tensor([idx], dtype=torch.int64),
            "source_path": str(image_path.relative_to(ROOT)),
        }
        return image, target


def collate(batch):
    images, targets = zip(*batch)
    return list(images), list(targets)


def make_model(num_classes: int, pretrained: bool) -> torch.nn.Module:
    weights = FasterRCNN_MobileNet_V3_Large_320_FPN_Weights.DEFAULT if pretrained else None
    model = fasterrcnn_mobilenet_v3_large_320_fpn(weights=weights)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    return model


def train_one_setting(
    dataset_root: Path,
    out_dir: Path,
    device: torch.device,
    epochs: int,
    batch_size: int,
    lr: float,
    max_train: int | None,
    max_val: int | None,
    score_threshold: float,
    pretrained: bool,
    seed: int,
) -> dict[str, object]:
    torch.manual_seed(seed)
    random.seed(seed)
    train_ds = YoloDetectionDataset(dataset_root, "train", max_train, seed)
    val_ds = YoloDetectionDataset(dataset_root, "val", max_val, seed)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0, collate_fn=collate)
    val_loader = DataLoader(val_ds, batch_size=1, shuffle=False, num_workers=0, collate_fn=collate)

    model = make_model(num_classes=len(CLASS_NAMES) + 1, pretrained=pretrained).to(device)
    optimizer = torch.optim.SGD([p for p in model.parameters() if p.requires_grad], lr=lr, momentum=0.9, weight_decay=0.0005)

    start = time.time()
    model.train()
    last_loss = math.nan
    for epoch in range(epochs):
        losses = []
        for images, targets in train_loader:
            images = [img.to(device) for img in images]
            moved = []
            for target in targets:
                moved.append({k: v.to(device) if hasattr(v, "to") else v for k, v in target.items() if k != "source_path"})
            loss_dict = model(images, moved)
            loss = sum(loss for loss in loss_dict.values())
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            losses.append(float(loss.detach().cpu()))
        last_loss = sum(losses) / max(1, len(losses))
        print(f"{dataset_root.name} epoch {epoch + 1}/{epochs}: loss={last_loss:.4f}", flush=True)

    metrics = evaluate(model, val_loader, device, score_threshold)
    elapsed = time.time() - start
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save({"model": model.state_dict(), "class_names": CLASS_NAMES}, out_dir / "checkpoint.pt")
    return {
        "dataset_root": str(dataset_root.relative_to(ROOT)),
        "train_images": len(train_ds),
        "val_images": len(val_ds),
        "epochs": epochs,
        "batch_size": batch_size,
        "lr": lr,
        "pretrained_coco": pretrained,
        "score_threshold": score_threshold,
        "train_loss": last_loss,
        "elapsed_sec": elapsed,
        **metrics,
    }


def evaluate(model: torch.nn.Module, loader: DataLoader, device: torch.device, score_threshold: float) -> dict[str, object]:
    model.eval()
    gt_by_class: dict[int, dict[int, torch.Tensor]] = {i + 1: {} for i in range(len(CLASS_NAMES))}
    pred_by_class: dict[int, list[Prediction]] = {i + 1: [] for i in range(len(CLASS_NAMES))}

    with torch.no_grad():
        for images, targets in loader:
            image = images[0].to(device)
            target = targets[0]
            image_id = int(target["image_id"].item())
            gt_boxes = target["boxes"]
            gt_labels = target["labels"]
            for cls in gt_by_class:
                gt_by_class[cls][image_id] = gt_boxes[gt_labels == cls].cpu()

            pred = model([image])[0]
            boxes = pred["boxes"].detach().cpu()
            scores = pred["scores"].detach().cpu()
            labels = pred["labels"].detach().cpu()
            keep = scores >= score_threshold
            for box, score, label in zip(boxes[keep], scores[keep], labels[keep]):
                cls = int(label.item())
                if cls in pred_by_class:
                    pred_by_class[cls].append(Prediction(image_id=image_id, score=float(score), box=box))

    ap_values = {}
    total_tp = 0
    total_fp = 0
    total_gt = 0
    for cls, preds in pred_by_class.items():
        ap, tp, fp, gt_count = ap50_for_class(preds, gt_by_class[cls])
        ap_values[f"AP50_{CLASS_NAMES[cls - 1]}"] = ap
        total_tp += tp
        total_fp += fp
        total_gt += gt_count
    valid_aps = [v for v in ap_values.values() if not math.isnan(v)]
    precision = total_tp / (total_tp + total_fp) if total_tp + total_fp else 0.0
    recall = total_tp / total_gt if total_gt else 0.0
    return {
        "mAP50": sum(valid_aps) / len(valid_aps) if valid_aps else math.nan,
        "precision": precision,
        "recall": recall,
        "tp": total_tp,
        "fp": total_fp,
        "gt": total_gt,
        **ap_values,
    }


def ap50_for_class(preds: list[Prediction], gt_by_image: dict[int, torch.Tensor]) -> tuple[float, int, int, int]:
    gt_count = sum(len(v) for v in gt_by_image.values())
    if gt_count == 0:
        return math.nan, 0, 0, 0
    matched = {image_id: torch.zeros(len(boxes), dtype=torch.bool) for image_id, boxes in gt_by_image.items()}
    preds = sorted(preds, key=lambda p: p.score, reverse=True)
    tp_flags = []
    fp_flags = []
    for pred in preds:
        gt_boxes = gt_by_image.get(pred.image_id, torch.empty((0, 4)))
        if len(gt_boxes) == 0:
            tp_flags.append(0)
            fp_flags.append(1)
            continue
        ious = box_iou(pred.box[None, :], gt_boxes).squeeze(0)
        best_iou, best_idx = torch.max(ious, dim=0)
        if float(best_iou) >= 0.5 and not bool(matched[pred.image_id][int(best_idx)]):
            matched[pred.image_id][int(best_idx)] = True
            tp_flags.append(1)
            fp_flags.append(0)
        else:
            tp_flags.append(0)
            fp_flags.append(1)
    if not preds:
        return 0.0, 0, 0, gt_count
    tp_cum = torch.tensor(tp_flags, dtype=torch.float32).cumsum(0)
    fp_cum = torch.tensor(fp_flags, dtype=torch.float32).cumsum(0)
    recalls = tp_cum / max(1, gt_count)
    precisions = tp_cum / torch.clamp(tp_cum + fp_cum, min=1)
    ap = voc_ap(recalls, precisions)
    return ap, int(tp_cum[-1].item()), int(fp_cum[-1].item()), gt_count


def voc_ap(recalls: torch.Tensor, precisions: torch.Tensor) -> float:
    mrec = torch.cat([torch.tensor([0.0]), recalls, torch.tensor([1.0])])
    mpre = torch.cat([torch.tensor([0.0]), precisions, torch.tensor([0.0])])
    for i in range(len(mpre) - 1, 0, -1):
        mpre[i - 1] = torch.maximum(mpre[i - 1], mpre[i])
    idx = torch.where(mrec[1:] != mrec[:-1])[0]
    return float(torch.sum((mrec[idx + 1] - mrec[idx]) * mpre[idx + 1]).item())


def write_summary(rows: list[dict[str, object]], csv_path: Path, summary_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Faster R-CNN Non-YOLO Probe Summary",
        "",
        "This is a bounded detector-family probe using torchvision Faster R-CNN MobileNetV3-320-FPN on existing frozen YOLO-format subsets.",
        "It is intended to test whether a non-YOLO pipeline can be audited with the same ordinary/LODO boundary logic; it is not a tuned detector-performance claim.",
        "",
        "| setting | train images | val images | epochs | mAP50 | precision | recall | gt | tp | fp | elapsed sec |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {setting} | {train_images} | {val_images} | {epochs} | {mAP50:.4f} | {precision:.4f} | {recall:.4f} | {gt} | {tp} | {fp} | {elapsed_sec:.1f} |".format(
                **row
            )
        )
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", nargs="+", default=["ordinary", "heldout_Norway", "heldout_India"])
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--lr", type=float, default=0.0025)
    parser.add_argument("--max-train-images", type=int, default=None)
    parser.add_argument("--max-val-images", type=int, default=None)
    parser.add_argument("--score-threshold", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=20260518)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--no-pretrained", action="store_true")
    parser.add_argument("--csv", default="data_processed/non_yolo/fasterrcnn_probe_results.csv")
    parser.add_argument("--summary", default="outputs/non_yolo/fasterrcnn_probe_summary.md")
    args = parser.parse_args()

    device = torch.device(args.device)
    rows = []
    for setting in args.settings:
        if setting == "ordinary":
            dataset_root = ROOT / "data_processed" / "yolo_g3_frozen_subset_ordinary"
        elif setting.startswith("heldout_"):
            dataset_root = ROOT / "data_processed" / "yolo_g3_frozen_subset_lodo" / setting
        else:
            raise ValueError(f"Unknown setting: {setting}")
        out_dir = ROOT / "outputs" / "non_yolo" / f"fasterrcnn_{setting}"
        print(f"Running Faster R-CNN probe: {setting}", flush=True)
        result = train_one_setting(
            dataset_root=dataset_root,
            out_dir=out_dir,
            device=device,
            epochs=args.epochs,
            batch_size=args.batch_size,
            lr=args.lr,
            max_train=args.max_train_images,
            max_val=args.max_val_images,
            score_threshold=args.score_threshold,
            pretrained=not args.no_pretrained,
            seed=args.seed,
        )
        rows.append({"setting": setting, **result})
    write_summary(rows, ROOT / args.csv, ROOT / args.summary)
    print(ROOT / args.csv)
    print(ROOT / args.summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
