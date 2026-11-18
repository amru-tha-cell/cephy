
import torch

from app.training.losses import (
    heatmap_focal_loss,
    multitask_loss
)


def test_heatmap_focal_loss_is_finite():

    logits = torch.randn(2, 19, 64, 64)

    targets = torch.zeros(2, 19, 64, 64)

    # Fractional landmark coordinates.
    x, y = 20.7, 30.7

    yy, xx = torch.meshgrid(
        torch.arange(64),
        torch.arange(64),
        indexing="ij"
    )

    gaussian = torch.exp(
        -((xx - x) ** 2 + (yy - y) ** 2) / 50
    )

    targets[:, 0] = gaussian

    loss = heatmap_focal_loss(logits, targets)

    assert torch.isfinite(loss)
    assert loss.item() >= 0


def test_multitask_loss_returns_components():

    predictions = {
        "heatmaps": torch.randn(2, 19, 64, 64),
        "offsets": torch.randn(2, 19, 2, 64, 64)
    }

    target_heat = torch.zeros(2, 19, 64, 64)
    target_offsets = torch.zeros(2, 19, 2, 64, 64)

    target_heat[:, :, 32, 32] = 1.0

    loss, components = multitask_loss(
        predictions,
        target_heat,
        target_offsets
    )

    assert torch.isfinite(loss)
    assert "heatmap_loss" in components
    assert "offset_loss" in components
    assert loss.item() >= 0
