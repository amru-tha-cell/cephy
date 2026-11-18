
import cv2
import numpy as np


def preprocess_image(image, image_size=512):
    """
    Resize an X-ray while preserving aspect ratio.
    Pad the result to image_size x image_size.

    Returns:
        padded: 512x512 grayscale image
        transform: metadata required to reverse coordinate mapping
    """
    if image is None or image.ndim != 2:
        raise ValueError("Expected a valid grayscale image")

    h, w = image.shape

    scale = min(image_size / w, image_size / h)

    new_w = round(w * scale)
    new_h = round(h * scale)

    resized = cv2.resize(
        image,
        (new_w, new_h),
        interpolation=cv2.INTER_AREA
    )

    pad_x = (image_size - new_w) // 2
    pad_y = (image_size - new_h) // 2

    padded = np.zeros(
        (image_size, image_size),
        dtype=np.uint8
    )

    padded[
        pad_y:pad_y + new_h,
        pad_x:pad_x + new_w
    ] = resized

    transform = {
        "original_width": w,
        "original_height": h,
        "resized_width": new_w,
        "resized_height": new_h,
        "scale_x": new_w / w,
        "scale_y": new_h / h,
        "pad_x": pad_x,
        "pad_y": pad_y,
        "image_size": image_size
    }

    return padded, transform


def transform_points(points, transform):
    """Map original-image coordinates to model-image coordinates."""
    result = np.asarray(points, dtype=np.float32).copy()

    result[:, 0] = (
        result[:, 0] * transform["scale_x"]
        + transform["pad_x"]
    )

    result[:, 1] = (
        result[:, 1] * transform["scale_y"]
        + transform["pad_y"]
    )

    return result


def inverse_transform_points(points, transform):
    """Map model-image coordinates back to original-image coordinates."""
    result = np.asarray(points, dtype=np.float32).copy()

    result[:, 0] = (
        result[:, 0] - transform["pad_x"]
    ) / transform["scale_x"]

    result[:, 1] = (
        result[:, 1] - transform["pad_y"]
    ) / transform["scale_y"]

    return result
