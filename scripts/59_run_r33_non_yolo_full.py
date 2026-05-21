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
    RetinaNet_ResNet50_FPN_Weights,
    fasterrcnn_mobilenet_v3_large_320_fpn,
    retinanet_resnet50_fpn,
)
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.retinanet import RetinaNetClassificationHead
from torchvision.ops import box_iou
from torchvision.transforms import functional as F


ROOT = Path(__file__).resolve().parents[1]
CLASS_NAMES = ["D00", "D10", "D20", "D40"]
SETTINGS = [
    "ordinary",
    "heldout_China_Drone",
    "heldout_China_MotorBike",
    "heldout_Czech_Republic",
    "heldout_India",
    "heldout_Japan",
    "heldout_Norway",
    "heldout_United_States",
]


@dataclass
class Prediction:
    image_id: int
    score: float
    box: torch.Tensor


class YoloDetectionDataset(Dataset):
    def __init__(
        self,
        dataset_root: Path,
        split: str,
        label_offset: int,
        max_images: int | None = None,
        seed: int = 20260521,
    ):
        self.dataset_root = dataset_root
        self.split = split
        self.label_offset = label_offset
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

        boxes: list[list[float]] = []
        labels: list[int] = []
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
                    labels.append(cls_i + self.label_offset)

        target = {
            "boxes": torch.tensor(boxes, dtype=torch.float32).reshape(-1, 4),
            "labels": torch.tensor(labels, dtype=torch.int64),
            "image_id": torch.tensor([idx], dtype=torch.int64),
            "source_path": str(image_path.relative_to(ROOT)),
        }
        return image, target


def collate(batch):
    images, targets = zip(*batch)
    return list(images), list(targets)


def make_model(model_name: str, pretrained: bool) -> tuple[torch.nn.Module, int]:
    if model_name == "fasterrcnn_mobilenet320":
        weights = FasterRCNN_MobileNet_V3_Large_320_FPN_Weights.DEFAULT if pretrained else None
        model = fasterrcnn_mobilenet_v3_large_320_fpn(weights=weights)
        in_features = model.roi_heads.box_predictor.cls_score.in_features
        model.roi_heads.box_predictor = FastRCNNPredictor(in_features, len(CLASS_NAMES) + 1)
        return model, 1

    if model_name == "retinanet_resnet50_fpn":
        weights = RetinaNet_ResNet50_FPN_Weights.DEFAULT if pretrained else None
        model = retinanet_resnet50_fpn(
            weights=weights,
            min_size=320,
            max_size=640,
            trainable_backbone_layers=3 if pretrained else None,
        )
        num_anchors = model.head.classification_head.num_anchors
        in_channels = model.backbone.out_channels
        model.head.classification_head = RetinaNetClassificationHead(
            in_channels,
            num_anchors,
            len(CLASS_NAMES),
        )
        return model, 0

    raise ValueError(f"Unknown model_name: {model_name}")


def dataset_root_for_setting(suite_prefix: str, setting: str) -> Path:
    if setting == "ordinary":
        return ROOT / "data_processed" / "g4" / f"{suite_prefix}_ordinary"
    if setting.startswith("heldout_"):
        return ROOT / "data_processed" / "g4" / f"{suite_prefix}_lodo" / setting
    raise ValueError(setting)


def train_one_setting(
    model_name: str,
    suite_prefix: str,
    setting: str,
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
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.benchmark = True

    model, label_offset = make_model(model_name, pretrained)
    model.to(device)
    dataset_root = dataset_root_for_setting(suite_prefix, setting)
    train_ds = YoloDetectionDataset(dataset_root, "train", label_offset=label_offset, max_images=max_train, seed=seed)
    val_ds = YoloDetectionDataset(dataset_root, "val", label_offset=label_offset, max_images=max_val, seed=seed)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0, collate_fn=collate)
    val_loader = DataLoader(val_ds, batch_size=1, shuffle=False, num_workers=0, collate_fn=collate)
    optimizer = torch.optim.SGD(
        [p for p in model.parameters() if p.requires_grad],
        lr=lr,
        momentum=0.9,
        weight_decay=0.0005,
    )

    start = time.time()
    losses_by_epoch: list[float] = []
    for epoch in range(epochs):
        model.train()
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
        epoch_loss = sum(losses) / max(1, len(losses))
        losses_by_epoch.append(epoch_loss)
        print(
            f"{model_name} {setting} epoch {epoch + 1}/{epochs}: loss={epoch_loss:.4f}",
            flush=True,
        )

    metrics = evaluate(model, val_loader, device, label_offset, score_threshold)
    elapsed = time.time() - start
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model": model.state_dict(),
            "class_names": CLASS_NAMES,
            "model_name": model_name,
            "label_offset": label_offset,
            "suite_prefix": suite_prefix,
            "setting": setting,
            "epochs": epochs,
            "seed": seed,
            "losses_by_epoch": losses_by_epoch,
        },
        out_dir / "checkpoint.pt",
    )
    return {
        "model_name": model_name,
        "suite_prefix": suite_prefix,
        "setting": setting,
        "dataset_root": str(dataset_root.relative_to(ROOT)),
        "train_images": len(train_ds),
        "val_images": len(val_ds),
        "epochs": epochs,
        "batch_size": batch_size,
        "lr": lr,
        "pretrained_coco": pretrained,
        "score_threshold": score_threshold,
        "train_loss": losses_by_epoch[-1] if losses_by_epoch else math.nan,
        "elapsed_sec": elapsed,
        **metrics,
    }


def evaluate(
    model: torch.nn.Module,
    loader: DataLoader,
    device: torch.device,
    label_offset: int,
    score_threshold: float,
) -> dict[str, object]:
    model.eval()
    internal_classes = [i + label_offset for i in range(len(CLASS_NAMES))]
    gt_by_class: dict[int, dict[int, torch.Tensor]] = {cls: {} for cls in internal_classes}
    pred_by_class: dict[int, list[Prediction]] = {cls: [] for cls in internal_classes}

    with torch.no_grad():
        for images, targets in loader:
            image = images[0].to(device)
            target = targets[0]
            image_id = int(target["image_id"].item())
            gt_boxes = target["boxes"]
            gt_labels = target["labels"]
            for cls in internal_classes:
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
        class_name = CLASS_NAMES[cls - label_offset]
        ap, tp, fp, gt_count = ap50_for_class(preds, gt_by_class[cls])
        ap_values[f"AP50_{class_name}"] = ap
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


def write_summary(rows: list[dict[str, object]], summary_path: Path) -> None:
    def as_int(row: dict[str, object], key: str) -> int:
        return int(float(row[key]))

    def as_float(row: dict[str, object], key: str) -> float:
        return float(row[key])

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# R33 Non-YOLO Minimal LODO Validation Summary",
        "",
        "This summary reports non-YOLO detector-family checks on the frozen 640-image/source-domain subsets.",
        "Faster R-CNN is run for the requested 8 epochs. RetinaNet is a minimal LODO architecture check when selected.",
        "",
        "| model | setting | train images | val images | epochs | mAP50 | precision | recall | gt | tp | fp | elapsed sec |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['model_name']} | {row['setting']} | {as_int(row, 'train_images')} | "
            f"{as_int(row, 'val_images')} | {as_int(row, 'epochs')} | {as_float(row, 'mAP50'):.4f} | "
            f"{as_float(row, 'precision'):.4f} | {as_float(row, 'recall'):.4f} | {as_int(row, 'gt')} | "
            f"{as_int(row, 'tp')} | {as_int(row, 'fp')} | {as_float(row, 'elapsed_sec'):.1f} |"
        )
    lines.extend(["", "## Ordinary vs mean LODO", ""])
    by_model: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        by_model.setdefault(str(row["model_name"]), []).append(row)
    lines.append("| model | ordinary mAP50 | mean LODO mAP50 | gap | n LODO | weakest LODO domain | weakest mAP50 |")
    lines.append("| --- | ---: | ---: | ---: | ---: | --- | ---: |")
    for model, model_rows in by_model.items():
        ordinary = [r for r in model_rows if r["setting"] == "ordinary"]
        lodo = [r for r in model_rows if str(r["setting"]).startswith("heldout_")]
        if not ordinary or not lodo:
            continue
        mean_lodo = sum(float(r["mAP50"]) for r in lodo) / len(lodo)
        weak = min(lodo, key=lambda r: float(r["mAP50"]))
        lines.append(
            f"| {model} | {float(ordinary[0]['mAP50']):.4f} | {mean_lodo:.4f} | {float(ordinary[0]['mAP50']) - mean_lodo:.4f} | {len(lodo)} | {str(weak['setting']).replace('heldout_', '')} | {float(weak['mAP50']):.4f} |"
        )
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=["fasterrcnn_mobilenet320"])
    parser.add_argument("--settings", nargs="+", default=SETTINGS)
    parser.add_argument("--suite-prefix", default="r14lc640_yolov8s_seed20260512")
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--retinanet-epochs", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--retinanet-batch-size", type=int, default=1)
    parser.add_argument("--lr", type=float, default=0.0025)
    parser.add_argument("--retinanet-lr", type=float, default=0.001)
    parser.add_argument("--max-train-images", type=int, default=None)
    parser.add_argument("--max-val-images", type=int, default=None)
    parser.add_argument("--score-threshold", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=20260521)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--no-pretrained", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--csv", default="data_processed/non_yolo/r33_non_yolo_640_lodo_results.csv")
    parser.add_argument("--summary", default="outputs/non_yolo/r33_non_yolo_640_lodo_summary.md")
    args = parser.parse_args()

    csv_path = ROOT / args.csv
    summary_path = ROOT / args.summary
    rows: list[dict[str, object]] = [dict(row) for row in existing_rows(csv_path)]
    done = {(str(r["model_name"]), str(r["setting"])) for r in rows if "model_name" in r and "setting" in r}
    device = torch.device(args.device)
    print(f"device={device}", flush=True)

    for model_name in args.models:
        epochs = args.retinanet_epochs if model_name == "retinanet_resnet50_fpn" and args.retinanet_epochs else args.epochs
        batch_size = args.retinanet_batch_size if model_name == "retinanet_resnet50_fpn" else args.batch_size
        lr = args.retinanet_lr if model_name == "retinanet_resnet50_fpn" else args.lr
        for setting in args.settings:
            key = (model_name, setting)
            if args.skip_existing and key in done:
                print(f"Skipping existing {model_name} {setting}", flush=True)
                continue
            out_dir = ROOT / "outputs" / "non_yolo" / "r33" / f"{model_name}_{setting}"
            print(f"Running {model_name}: {setting}", flush=True)
            result = train_one_setting(
                model_name=model_name,
                suite_prefix=args.suite_prefix,
                setting=setting,
                out_dir=out_dir,
                device=device,
                epochs=epochs,
                batch_size=batch_size,
                lr=lr,
                max_train=args.max_train_images,
                max_val=args.max_val_images,
                score_threshold=args.score_threshold,
                pretrained=not args.no_pretrained,
                seed=args.seed,
            )
            rows = [r for r in rows if (str(r.get("model_name")), str(r.get("setting"))) != key]
            rows.append(result)
            write_csv(rows, csv_path)
            write_summary(rows, summary_path)
    print(csv_path)
    print(summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
