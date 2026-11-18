
from pathlib import Path

import cv2
import numpy as np

from app.core.config import HEATMAP_DIR, LANDMARK_NAMES


def save_heatmaps(case_id: int, heatmaps: list) -> list[dict]:
    """
    Save individual predicted landmark heatmaps as grayscale PNG files.
    """

    case_dir = HEATMAP_DIR / f"case_{case_id}"
    case_dir.mkdir(parents=True, exist_ok=True)

    saved_heatmaps = []

    for index, heatmap in enumerate(heatmaps):

        heatmap = np.asarray(
            heatmap,
            dtype=np.float32
        ).squeeze()

        if heatmap.ndim != 2:
            raise ValueError(
                f"Expected a 2D heatmap for landmark {index}, "
                f"received shape {heatmap.shape}"
            )

        if not np.isfinite(heatmap).all():
            raise ValueError(
                f"Heatmap {index} contains invalid values"
            )

        heatmap = np.clip(heatmap, 0.0, 1.0)

        heatmap_image = (
            heatmap * 255
        ).astype(np.uint8)

        filename = f"landmark_{index:02d}.png"
        file_path = case_dir / filename

        success = cv2.imwrite(
            str(file_path),
            heatmap_image
        )

        if not success:
            raise RuntimeError(
                f"Could not save heatmap: {file_path}"
            )

        landmark_name = (
            LANDMARK_NAMES[index]
            if index < len(LANDMARK_NAMES)
            else f"Landmark {index + 1}"
        )

        saved_heatmaps.append({
            "index": index,
            "name": landmark_name,
            "url": f"/heatmaps/case_{case_id}/{filename}"
        })

    return saved_heatmaps


def get_confidence_color(confidence):
    """
    Return BGR colour based on model confidence.

    Confidence is expected in the range 0 to 1.
    """

    if confidence is None:
        return (255, 255, 255)

    confidence = float(confidence)

    if not np.isfinite(confidence):
        return (255, 255, 255)

    if confidence <= 1:
        confidence *= 100

    if confidence < 40:
        return (0, 0, 255)       # Red

    if confidence < 60:
        return (0, 165, 255)     # Orange

    if confidence < 75:
        return (0, 255, 255)     # Yellow

    return (0, 200, 0)           # Green


def save_heatmap_overlay(
    case_id: int,
    image_path,
    heatmaps: list,
    points: list
) -> str:
    """
    Generate a transparent colour-coded heatmap overlay.

    Each landmark receives a colour based on its prediction
    confidence. Spatial intensity comes from its predicted
    heatmap activation.

    Returns the URL of the transparent PNG overlay.
    """

    case_dir = HEATMAP_DIR / f"case_{case_id}"
    case_dir.mkdir(parents=True, exist_ok=True)

    original = cv2.imread(
        str(image_path),
        cv2.IMREAD_GRAYSCALE
    )

    if original is None:
        raise ValueError(
            f"Could not read original image: {image_path}"
        )

    original_height, original_width = original.shape

    if len(heatmaps) != len(points):
        raise ValueError(
            "Number of heatmaps and predicted points must match."
        )

    # Transparent BGRA overlay.
    overlay = np.zeros(
        (original_height, original_width, 4),
        dtype=np.uint8
    )

    # Stores the strongest activation at each pixel.
    strongest_activation = np.zeros(
        (original_height, original_width),
        dtype=np.float32
    )

    for index, heatmap in enumerate(heatmaps):

        heatmap = np.asarray(
            heatmap,
            dtype=np.float32
        ).squeeze()

        if heatmap.ndim != 2:
            raise ValueError(
                f"Invalid heatmap shape at index {index}: "
                f"{heatmap.shape}"
            )

        if not np.isfinite(heatmap).all():
            raise ValueError(
                f"Heatmap {index} contains invalid values"
            )

        heatmap = np.clip(heatmap, 0.0, 1.0)

        # Resize the 128x128 heatmap to original X-ray dimensions.
        resized = cv2.resize(
            heatmap,
            (original_width, original_height),
            interpolation=cv2.INTER_CUBIC
        )

        # Smooth the heatmap for a visually continuous overlay.
        resized = cv2.GaussianBlur(
            resized,
            (0, 0),
            sigmaX=max(1.0, original_width / 500)
        )

        # Normalize each landmark's activation for visualization.
        minimum = float(resized.min())
        maximum = float(resized.max())

        if maximum - minimum < 1e-8:
            continue

        normalized = (
            resized - minimum
        ) / (maximum - minimum)

        # Suppress weak background activations.
        threshold = 0.20

        activation = np.clip(
            (normalized - threshold) / (1.0 - threshold),
            0.0,
            1.0
        )

        # Ignore very weak activations.
        active = activation > 0

        # Only the strongest landmark activation colours each pixel.
        stronger = active & (
            activation > strongest_activation
        )

        if not np.any(stronger):
            continue

        confidence = points[index].get("confidence")

        color_b, color_g, color_r = get_confidence_color(
            confidence
        )

        strongest_activation[stronger] = activation[stronger]

        overlay[stronger, 0] = color_b
        overlay[stronger, 1] = color_g
        overlay[stronger, 2] = color_r

        # Alpha follows spatial activation intensity.
        overlay[stronger, 3] = (
            activation[stronger] * 180
        ).astype(np.uint8)

    filename = "confidence_heatmap_overlay.png"

    file_path = case_dir / filename

    success = cv2.imwrite(
        str(file_path),
        overlay
    )

    if not success:
        raise RuntimeError(
            f"Could not save composite heatmap: {file_path}"
        )

    return (
        f"/heatmaps/case_{case_id}/{filename}"
    )
