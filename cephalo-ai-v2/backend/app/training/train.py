
"""Train the Swin-Attention U-Net on the ISBI training dataset.

Example:
python -m app.training.train --images ../data/isbi2015/RawImage/TrainingData --annotations ../data/isbi2015/AnnotationsByMD/400_senior
"""

import argparse
import random

import numpy as np
import torch

from torch.utils.data import DataLoader, Subset

from app.training.dataset import CephDataset
from app.training.model import SwinAttentionUNet
from app.training.losses import multitask_loss
from app.core.config import WEIGHT_DIR, IMAGE_SIZE, NUM_LANDMARKS


# ISBI benchmark convention. Verify against the official evaluation protocol.
PIXELS_PER_MM = 10.0


def decode_landmarks(predicted_heatmaps, predicted_offsets=None):
    """
    Decode landmark coordinates from heatmap maxima.

    If offsets are supplied, use the offset vector at each
    heatmap maximum to refine the predicted coordinate.

    Returns:
        Tensor of shape [B, NUM_LANDMARKS, 2]
    """

    batch_size, num_landmarks, height, width = (
        predicted_heatmaps.shape
    )

    heat = torch.sigmoid(predicted_heatmaps)

    batch_points = []

    for batch_index in range(batch_size):

        points = []

        for landmark_index in range(num_landmarks):

            flat = heat[
                batch_index,
                landmark_index
            ].flatten()

            index = flat.argmax()

            y = index // width
            x = index % width

            if predicted_offsets is not None:

                offset = predicted_offsets[
                    batch_index,
                    landmark_index,
                    :,
                    y,
                    x
                ]

                point = torch.stack([
                    x.to(offset.dtype) + offset[0],
                    y.to(offset.dtype) + offset[1]
                ])

            else:

                point = torch.stack([
                    x.to(torch.float32),
                    y.to(torch.float32)
                ])

            points.append(point)

        batch_points.append(torch.stack(points))

    return torch.stack(batch_points)


def calculate_validation_metrics(errors_px):
    """Calculate MRE and SDR from original-image pixel errors."""

    if len(errors_px) == 0:
        return {}

    errors_px = np.asarray(
        errors_px,
        dtype=np.float64
    )

    errors_mm = errors_px / PIXELS_PER_MM

    return {
        "mre_px": float(errors_px.mean()),
        "mre_mm": float(errors_mm.mean()),
        "sdr": {
            threshold: float(
                (errors_mm <= threshold).mean() * 100
            )
            for threshold in (2.0, 2.5, 3.0, 4.0)
        }
    }


def calculate_original_coordinate_errors(
    predicted_points,
    batch
):
    """
    Convert model-space predictions to original-image coordinates
    and calculate per-landmark Euclidean errors.

    predicted_points: [B, NUM_LANDMARKS, 2]
    """

    device = predicted_points.device

    scale_x = batch["scale_x"].to(device)
    scale_y = batch["scale_y"].to(device)
    pad_x = batch["pad_x"].to(device)
    pad_y = batch["pad_y"].to(device)

    predicted_original = predicted_points.clone()

    predicted_original[:, :, 0] = (
        predicted_points[:, :, 0] - pad_x[:, None]
    ) / scale_x[:, None]

    predicted_original[:, :, 1] = (
        predicted_points[:, :, 1] - pad_y[:, None]
    ) / scale_y[:, None]

    truth_original = batch["original_points"].to(device)

    distances = torch.linalg.norm(
        predicted_original - truth_original,
        dim=-1
    )

    return distances.reshape(-1).cpu().numpy().tolist()


def set_seed(seed):
    """Set random seeds for reproducibility."""

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--images", required=True)
    parser.add_argument("--annotations", required=True)

    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    if args.epochs < 1:
        raise ValueError("--epochs must be positive")

    if args.batch_size < 1:
        raise ValueError("--batch-size must be positive")

    if args.lr <= 0:
        raise ValueError("--lr must be positive")

    if not 0.05 <= args.val_ratio <= 0.5:
        raise ValueError(
            "--val-ratio must be between 0.05 and 0.5"
        )

    set_seed(args.seed)

    # --------------------------------------------------
    # DATASETS
    # --------------------------------------------------

    # Training dataset: photometric augmentation enabled.
    train_dataset = CephDataset(
        args.images,
        args.annotations,
        training=True
    )

    # Validation dataset: augmentation disabled.
    validation_dataset = CephDataset(
        args.images,
        args.annotations,
        training=False
    )

    if len(train_dataset) < 2:
        raise ValueError(
            "At least two annotated images are required."
        )

    if len(train_dataset) != len(validation_dataset):
        raise ValueError(
            "Training and validation datasets have different lengths."
        )

    # Ensure both datasets have identical image ordering.
    train_paths = [
        str(item[0]) for item in train_dataset.items
    ]

    validation_paths = [
        str(item[0]) for item in validation_dataset.items
    ]

    if train_paths != validation_paths:
        raise ValueError(
            "Training and validation image ordering differs."
        )

    # --------------------------------------------------
    # TRAIN / VALIDATION SPLIT
    # --------------------------------------------------

    total_count = len(train_dataset)

    validation_count = max(
        1,
        int(total_count * args.val_ratio)
    )

    training_count = total_count - validation_count

    if training_count < 1:
        raise ValueError(
            "The split must contain at least one training image."
        )

    generator = torch.Generator().manual_seed(args.seed)

    indices = torch.randperm(
        total_count,
        generator=generator
    ).tolist()

    train_indices = indices[:training_count]
    validation_indices = indices[training_count:]

    # Separate datasets ensure validation never receives augmentation.
    train_subset = Subset(
        train_dataset,
        train_indices
    )

    validation_subset = Subset(
        validation_dataset,
        validation_indices
    )

    train_loader = DataLoader(
        train_subset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0,
        pin_memory=torch.cuda.is_available()
    )

    validation_loader = DataLoader(
        validation_subset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
        pin_memory=torch.cuda.is_available()
    )

    # --------------------------------------------------
    # DEVICE AND MODEL
    # --------------------------------------------------

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print("\nDevice:", device)
    print("Total images:", total_count)
    print("Training images:", training_count)
    print("Validation images:", validation_count)
    print("Independent test sets are not loaded.")

    model = SwinAttentionUNet(
        num_landmarks=NUM_LANDMARKS
    ).to(device)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.lr,
        weight_decay=1e-4
    )

    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=args.epochs
    )

    WEIGHT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    checkpoint_path = (
        WEIGHT_DIR / "swin_attention_unet.pt"
    )

    best_mre = float("inf")

    # --------------------------------------------------
    # TRAINING LOOP
    # --------------------------------------------------

    for epoch in range(args.epochs):

        model.train()

        train_loss = 0.0

        for batch in train_loader:

            images = batch["image"].to(device)
            heatmaps = batch["heatmaps"].to(device)
            offsets = batch["offsets"].to(device)

            optimizer.zero_grad(set_to_none=True)

            predictions = model(images)

            loss, loss_parts = multitask_loss(
                predictions,
                heatmaps,
                offsets
            )

            loss.backward()

            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                max_norm=1.0
            )

            optimizer.step()

            train_loss += loss.item()

        train_loss /= max(1, len(train_loader))

        # --------------------------------------------------
        # VALIDATION
        # --------------------------------------------------

        model.eval()

        validation_loss = 0.0

        heatmap_errors_px = []
        refined_errors_px = []

        with torch.no_grad():

            for batch in validation_loader:

                images = batch["image"].to(device)
                heatmaps = batch["heatmaps"].to(device)
                offsets = batch["offsets"].to(device)

                predictions = model(images)

                loss, _ = multitask_loss(
                    predictions,
                    heatmaps,
                    offsets
                )

                validation_loss += loss.item()

                # Prediction using heatmap maxima only.
                heatmap_points = decode_landmarks(
                    predictions["heatmaps"]
                )

                # Prediction using heatmap maxima + offsets.
                refined_points = decode_landmarks(
                    predictions["heatmaps"],
                    predictions["offsets"]
                )

                heatmap_errors_px.extend(
                    calculate_original_coordinate_errors(
                        heatmap_points,
                        batch
                    )
                )

                refined_errors_px.extend(
                    calculate_original_coordinate_errors(
                        refined_points,
                        batch
                    )
                )

        validation_loss /= max(
            1,
            len(validation_loader)
        )

        heatmap_metrics = calculate_validation_metrics(
            heatmap_errors_px
        )

        refined_metrics = calculate_validation_metrics(
            refined_errors_px
        )

        scheduler.step()

        refined_mre = refined_metrics.get(
            "mre_mm",
            float("inf")
        )

        heatmap_mre = heatmap_metrics.get(
            "mre_mm",
            float("inf")
        )

        # --------------------------------------------------
        # EPOCH REPORT
        # --------------------------------------------------

        print(
            f"\nEpoch {epoch + 1:03d}/{args.epochs}"
        )

        print(
            f"Train Loss: {train_loss:.5f}"
        )

        print(
            f"Validation Loss: {validation_loss:.5f}"
        )

        print(
            f"Heatmap-only MRE: "
            f"{heatmap_metrics.get('mre_px', float('nan')):.2f}px "
            f"({heatmap_mre:.3f}mm)"
        )

        print(
            f"Heatmap-only SDR: "
            f"{heatmap_metrics.get('sdr', {})}"
        )

        print(
            f"Refined MRE: "
            f"{refined_metrics.get('mre_px', float('nan')):.2f}px "
            f"({refined_mre:.3f}mm)"
        )

        print(
            f"Refined SDR: "
            f"{refined_metrics.get('sdr', {})}"
        )

        # --------------------------------------------------
        # SAVE BEST CHECKPOINT
        # --------------------------------------------------

        if np.isfinite(refined_mre) and refined_mre < best_mre:

            best_mre = refined_mre

            torch.save(
                {
                    "model": model.state_dict(),
                    "epoch": epoch + 1,
                    "train_loss": train_loss,
                    "val_loss": validation_loss,

                    "heatmap_mre_mm": heatmap_mre,
                    "heatmap_mre_px": heatmap_metrics.get(
                        "mre_px"
                    ),

                    "refined_mre_mm": refined_mre,
                    "refined_mre_px": refined_metrics.get(
                        "mre_px"
                    ),

                    "heatmap_sdr": heatmap_metrics.get("sdr"),
                    "refined_sdr": refined_metrics.get("sdr"),

                    "image_size": IMAGE_SIZE,
                    "num_landmarks": NUM_LANDMARKS,
                    "pixels_per_mm": PIXELS_PER_MM,
                    "seed": args.seed
                },
                checkpoint_path
            )

            print("Saved new best checkpoint.")

    # --------------------------------------------------
    # TRAINING COMPLETE
    # --------------------------------------------------

    print("\nTraining completed.")

    print(
        "Best refined validation MRE:",
        best_mre,
        "mm"
    )

    print(
        "Checkpoint:",
        checkpoint_path
    )


if __name__ == "__main__":
    main()
