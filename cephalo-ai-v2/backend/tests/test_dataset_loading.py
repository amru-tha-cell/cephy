
import cv2
import numpy as np

from app.training.dataset import CephDataset


def test_dataset_item_output(tmp_path):

    image_dir = tmp_path / "images"
    annotation_dir = tmp_path / "annotations"

    image_dir.mkdir()
    annotation_dir.mkdir()

    # Create a synthetic grayscale X-ray.
    image = np.random.randint(
        0, 256, (2400, 1935), dtype=np.uint8
    )

    cv2.imwrite(
        str(image_dir / "001.bmp"),
        image
    )

    # Create 19 landmarks.
    coordinates = [
        f"{835 + i},{996 + i}"
        for i in range(19)
    ]

    classifications = [
        "3", "3", "2", "3", "3", "1", "2", "3"
    ]

    annotation = annotation_dir / "001.txt"

    annotation.write_text(
        "\n".join(coordinates + classifications)
    )

    dataset = CephDataset(
        image_dir=image_dir,
        annotations=annotation_dir,
        training=False
    )

    sample = dataset[0]

    assert sample["image"].shape == (1, 512, 512)
    assert sample["heatmaps"].shape == (19, 512, 512)
    assert sample["offsets"].shape == (19, 2, 512, 512)
    assert sample["points"].shape == (19, 2)
    assert sample["original_points"].shape == (19, 2)
    assert sample["classifications"].shape == (8,)

    assert sample["image"].dtype == __import__("torch").float32
