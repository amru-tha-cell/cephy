
import numpy as np

from app.training.preprocessing import (
    preprocess_image,
    transform_points,
    inverse_transform_points,
)


def test_preprocessing_preserves_image_size():
    image = np.zeros((2400, 1935), dtype=np.uint8)

    processed, transform = preprocess_image(image, 512)

    assert processed.shape == (512, 512)
    assert transform["resized_width"] == 413
    assert transform["resized_height"] == 512


def test_coordinate_transformation():
    points = np.array([
        [835.0, 996.0]
    ], dtype=np.float32)

    _, transform = preprocess_image(
        np.zeros((2400, 1935), dtype=np.uint8),
        512
    )

    transformed = transform_points(points, transform)

    assert transformed.shape == (1, 2)
    assert np.allclose(
        transformed[0],
        [227.22, 212.48],
        atol=0.1
    )


def test_inverse_coordinate_transformation():
    original_points = np.array([
        [835.0, 996.0],
        [1200.0, 1500.0],
        [500.0, 800.0]
    ], dtype=np.float32)

    _, transform = preprocess_image(
        np.zeros((2400, 1935), dtype=np.uint8),
        512
    )

    transformed = transform_points(
        original_points, transform
    )

    recovered = inverse_transform_points(
        transformed, transform
    )

    assert np.allclose(
        original_points,
        recovered,
        atol=1e-4
    )
