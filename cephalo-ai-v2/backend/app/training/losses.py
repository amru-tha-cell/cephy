
import torch


def heatmap_focal_loss(pred_logits, target_heatmaps):
    """
    CenterNet-style focal loss for landmark heatmap prediction.

    pred_logits:     [B, K, H, W]
    target_heatmaps: [B, K, H, W]
    """

    if pred_logits.shape != target_heatmaps.shape:
        raise ValueError(
            "Prediction and target heatmap shapes must match."
        )

    pred = torch.sigmoid(pred_logits)
    pred = pred.clamp(min=1e-6, max=1 - 1e-6)

    # Select the maximum-valued pixel for each landmark.
    # This guarantees at least one positive pixel per landmark.
    max_values = target_heatmaps.amax(
        dim=(-2, -1),
        keepdim=True
    )

    positive_mask = target_heatmaps == max_values

    negative_mask = ~positive_mask

    # Down-weight negative pixels near Gaussian peaks.
    negative_weights = (
        1 - target_heatmaps
    ).pow(4)

    positive_loss = (
        torch.log(pred)
        * (1 - pred).pow(2)
        * positive_mask
    )

    negative_loss = (
        torch.log(1 - pred)
        * pred.pow(2)
        * negative_weights
        * negative_mask
    )

    num_positive = positive_mask.sum().clamp(min=1)

    loss = -(
        positive_loss.sum() + negative_loss.sum()
    ) / num_positive

    return loss


def multitask_loss(
    pred,
    target_heat,
    target_offsets,
    offset_weight=0.01
):
    """
    Combined heatmap and offset regression loss.
    """

    if pred["heatmaps"].shape != target_heat.shape:
        raise ValueError(
            "Predicted and target heatmap shapes do not match."
        )

    if pred["offsets"].shape != target_offsets.shape:
        raise ValueError(
            "Predicted and target offset shapes do not match."
        )

    hm = heatmap_focal_loss(
        pred["heatmaps"],
        target_heat
    )

    # Give more importance to offset predictions near landmarks.
    weights = target_heat.unsqueeze(2)

    offset_error = torch.abs(
        pred["offsets"] - target_offsets
    )

    off = (
        offset_error * weights
    ).sum() / (
        weights.sum() * 2 + 1e-6
    )

    total = hm + offset_weight * off

    return total, {
        "heatmap_loss": hm.detach(),
        "offset_loss": off.detach()
    }
