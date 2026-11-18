
import numpy as np

from app.training.dataset import CephDataset


def test_heatmap_peak_matches_landmark():
    dataset = CephDataset.__new__(CephDataset)
    dataset.size = 512
    dataset.sigma = 5.0

    x, y = 200.0, 150.0

    yy, xx = np.mgrid[0:512, 0:512]

    gaussian = np.exp(
        -((xx - x) ** 2 + (yy - y) ** 2)
        / (2 * dataset.sigma ** 2)
    )

    peak_y, peak_x = np.unravel_index(
        np.argmax(gaussian),
        gaussian.shape
    )

    assert peak_x == 200
    assert peak_y == 150
    assert np.isclose(gaussian[150, 200], 1.0)


def test_offset_targets_are_correct():
    x, y = 200.4, 150.7

    pixel_x, pixel_y = 200, 150

    offset_x = x - pixel_x
    offset_y = y - pixel_y

    assert np.isclose(offset_x, 0.4)
    assert np.isclose(offset_y, 0.7)
