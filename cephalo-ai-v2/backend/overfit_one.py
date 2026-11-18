
import torch
from torch.utils.data import Subset, DataLoader

from app.training.dataset import CephDataset
from app.training.model import SwinAttentionUNet
from app.training.losses import heatmap_focal_loss


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

IMAGE_DIR = "../data/isbi2015/RawImage/TrainingData"
ANNOTATION_DIR = "../data/isbi2015/AnnotationsByMD/400_senior"

EPOCHS = 100
LEARNING_RATE = 1e-4

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# --------------------------------------------------
# HEATMAP DECODER
# --------------------------------------------------

def decode_heatmaps(heatmaps):

    B, L, H, W = heatmaps.shape

    flattened = heatmaps.reshape(B, L, -1)

    indices = flattened.argmax(dim=-1)

    x = indices % W
    y = indices // W

    return torch.stack(
        [x, y],
        dim=-1
    ).float()


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print("Device:", DEVICE)

    # Load one image
    dataset = CephDataset(
        IMAGE_DIR,
        ANNOTATION_DIR,
        training=False
    )

    loader = DataLoader(
        Subset(dataset, [0]),
        batch_size=1,
        shuffle=False
    )

    batch = next(iter(loader))

    images = batch["image"].to(DEVICE)
    target_heatmaps = batch["heatmaps"].to(DEVICE)
    target_points = batch["points"].to(DEVICE)

    print("\n--- DATASET ---")

    print("Image:", images.shape)
    print("Heatmaps:", target_heatmaps.shape)
    print("Points:", target_points.shape)

    # --------------------------------------------------
    # MODEL
    # --------------------------------------------------

    model = SwinAttentionUNet().to(DEVICE)

    print(
        "\nInitial heatmap bias:",
        model.heatmap_head.bias.mean().item()
    )

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=0
    )

    # --------------------------------------------------
    # INITIAL EVALUATION
    # --------------------------------------------------

    model.eval()

    with torch.no_grad():

        initial_output = model(images)

        initial_points = decode_heatmaps(
            torch.sigmoid(initial_output["heatmaps"])
        )

        initial_mre = torch.linalg.vector_norm(
            initial_points - target_points,
            dim=-1
        ).mean()

    print("\nInitial MRE:", initial_mre.item())

    # --------------------------------------------------
    # TRAINING
    # --------------------------------------------------

    print("\n--- TRAINING ---\n")

    for epoch in range(1, EPOCHS + 1):

        model.train()

        optimizer.zero_grad()

        output = model(images)

        loss = heatmap_focal_loss(
            output["heatmaps"],
            target_heatmaps
        )

        loss.backward()

        optimizer.step()

        # --------------------------------------------------
        # EVALUATION
        # --------------------------------------------------

        if epoch % 10 == 0 or epoch == 1:

            model.eval()

            with torch.no_grad():

                predictions = model(images)

                predicted_heatmaps = torch.sigmoid(
                    predictions["heatmaps"]
                )

                predicted_points = decode_heatmaps(
                    predicted_heatmaps
                )

                errors = torch.linalg.vector_norm(
                    predicted_points - target_points,
                    dim=-1
                )

                mre = errors.mean().item()

                peak = predicted_heatmaps.amax(
                    dim=(-2, -1)
                ).mean().item()

            print(
                f"Epoch {epoch:03d} | "
                f"Loss: {loss.item():.6f} | "
                f"MRE: {mre:.2f} pixels | "
                f"Mean peak: {peak:.4f}"
            )

    # --------------------------------------------------
    # FINAL DIAGNOSTICS
    # --------------------------------------------------

    model.eval()

    with torch.no_grad():

        output = model(images)

        probabilities = torch.sigmoid(
            output["heatmaps"]
        )

        predicted_points = decode_heatmaps(
            probabilities
        )

        errors = torch.linalg.vector_norm(
            predicted_points - target_points,
            dim=-1
        )

    print("\n--- FINAL LANDMARK RESULTS ---")

    for i in range(19):

        target = target_points[0, i].cpu().numpy()

        prediction = predicted_points[0, i].cpu().numpy()

        error = errors[0, i].item()

        print(
            f"Landmark {i}: "
            f"Target={target} | "
            f"Prediction={prediction} | "
            f"Error={error:.2f}px"
        )

    print("\nFinal MRE:", errors.mean().item())

    # Save diagnostic checkpoint
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "final_mre": errors.mean().item(),
            "epochs": EPOCHS
        },
        "overfit_one_checkpoint.pt"
    )

    print("\nCheckpoint saved.")


if __name__ == "__main__":
    main()
