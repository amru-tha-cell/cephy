
import torch
import numpy as np
import cv2

from app.training.model import SwinAttentionUNet
from app.training.preprocessing import (
    preprocess_image,
    inverse_transform_points
)
from app.core.config import (
    WEIGHT_DIR,
    IMAGE_SIZE,
    NUM_LANDMARKS,
    LANDMARK_NAMES
)


class Predictor:

    def __init__(self):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.model = SwinAttentionUNet().to(self.device)

        self.checkpoint = WEIGHT_DIR / "swin_attention_unet.pt"
        self.loaded = False

        if self.checkpoint.exists():

            checkpoint = torch.load(
                self.checkpoint,
                map_location=self.device,
                weights_only=False
            )

            self.model.load_state_dict(checkpoint["model"])
            self.loaded = True

            print(
                f"Loaded checkpoint from epoch "
                f"{checkpoint.get('epoch', 'unknown')}"
            )

        self.model.eval()

    def predict(self, image_path, mc_samples=12):

        # 1. Read original X-ray
        original = cv2.imread(
            str(image_path),
            cv2.IMREAD_GRAYSCALE
        )

        if original is None:
            raise ValueError("Could not read uploaded image")

        original_h, original_w = original.shape

        # 2. Apply the same CLAHE preprocessing used during training
        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )

        enhanced = clahe.apply(original)

        # 3. Apply the exact training resize and padding pipeline
        processed, transform = preprocess_image(
            enhanced,
            image_size=IMAGE_SIZE
        )

        # 4. Normalize and create model input
        x = processed.astype(np.float32) / 255.0

        tensor = torch.from_numpy(
            x[None, None]
        ).to(self.device)

        if not self.loaded:
            return {
                "model_loaded": False,
                "message": "No trained checkpoint found.",
                "points": [],
                "heatmaps": [],
                "image_width": original_w,
                "image_height": original_h
            }

        # 5. Monte Carlo Dropout inference
        samples = []
        heatmap_samples = []

        with torch.no_grad():

            for _ in range(max(2, mc_samples)):

                self.model.eval()

                for module in self.model.modules():
                    if isinstance(
                        module,
                        (torch.nn.Dropout, torch.nn.Dropout2d)
                    ):
                        module.train()

                output = self.model(tensor)

                heatmaps = torch.sigmoid(
                    output["heatmaps"]
                )[0]

                coordinates = []

                for k in range(NUM_LANDMARKS):

                    # Heatmap-only prediction.
                    # Offset refinement is intentionally disabled.
                    flat_index = int(
                        heatmaps[k].flatten().argmax()
                    )

                    yy, xx = divmod(
                        flat_index,
                        IMAGE_SIZE
                    )

                    coordinates.append([
                        float(xx),
                        float(yy)
                    ])

                samples.append(coordinates)

                heatmap_samples.append(
                    heatmaps.cpu().numpy()
                )

        # 6. Calculate mean coordinates and uncertainty
        arr = np.asarray(samples)

        mean_coordinates = arr.mean(axis=0)
        coordinate_std = arr.std(axis=0)

        # 7. Reverse letterbox transformation
        original_coordinates = inverse_transform_points(
            mean_coordinates,
            transform
        )

        # Approximate uncertainty in original-image pixels.
        uncertainty_scale_x = 1.0 / transform["scale_x"]
        uncertainty_scale_y = 1.0 / transform["scale_y"]

        points = []

        for i, (xy, sd) in enumerate(
            zip(original_coordinates, coordinate_std)
        ):

            unc = float(
                np.linalg.norm([
                    sd[0] * uncertainty_scale_x,
                    sd[1] * uncertainty_scale_y
                ])
            )

            reliability = (
                "High" if unc < 2
                else "Moderate" if unc < 5
                else "Low"
            )

            points.append({
                "index": i,
                "name": LANDMARK_NAMES[i],
                "x": round(float(xy[0]), 2),
                "y": round(float(xy[1]), 2),
                "uncertainty_px": round(unc, 2),
                "confidence": round(
                    float(np.exp(-unc / 10)), 3
                ),
                "reliability": reliability
            })

        # 8. Average heatmaps for visualization
        mean_heatmaps = np.mean(
            heatmap_samples,
            axis=0
        )

        resized_heatmaps = [
            cv2.resize(
                hm,
                (128, 128),
                interpolation=cv2.INTER_AREA
            ).tolist()
            for hm in mean_heatmaps
        ]

        return {
            "model_loaded": True,
            "points": points,
            "heatmaps": resized_heatmaps,
            "image_width": original_w,
            "image_height": original_h,
            "mc_samples": len(samples)
        }
