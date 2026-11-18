
import pytest

from app.training.dataset import CephDataset


def test_parse_isbi_txt_annotation(tmp_path):
    annotation = tmp_path / "001.txt"

    coordinates = [
        f"{100 + i},{200 + i}"
        for i in range(19)
    ]

    classifications = [
        "3", "3", "2", "3", "3", "1", "2", "3"
    ]

    annotation.write_text(
        "\n".join(coordinates + classifications)
    )

    dataset = CephDataset.__new__(CephDataset)

    points, classes = dataset._parse_txt(annotation)

    assert len(points) == 19
    assert len(classes) == 8
    assert points[0] == [100.0, 200.0]
    assert classes == [3, 3, 2, 3, 3, 1, 2, 3]


def test_invalid_annotation_is_rejected(tmp_path):
    annotation = tmp_path / "002.txt"
    annotation.write_text("100,200\n")

    dataset = CephDataset.__new__(CephDataset)

    with pytest.raises(ValueError):
        dataset._parse_txt(annotation)
