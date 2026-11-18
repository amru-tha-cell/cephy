
import time
import torch

from app.training.model import SwinAttentionUNet
from app.training.dataset import CephDataset
from app.training.losses import multitask_loss

device = torch.device("cpu")

dataset = CephDataset(
    "../data/isbi2015/RawImage/TrainingData",
    "../data/isbi2015/AnnotationsByMD/400_senior",
    training=True
)

model = SwinAttentionUNet().to(device)
optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=1e-4
)

batch = dataset[0]

images = batch["image"].unsqueeze(0).to(device)
heatmaps = batch["heatmaps"].unsqueeze(0).to(device)
offsets = batch["offsets"].unsqueeze(0).to(device)

print("Starting forward and backward pass...")

start = time.time()

model.train()

predictions = model(images)

loss, components = multitask_loss(
    predictions,
    heatmaps,
    offsets
)

loss.backward()
optimizer.step()

elapsed = time.time() - start

print("Device:", device)
print("Loss:", loss.item())
print("Heatmap loss:", components["heatmap_loss"].item())
print("Offset loss:", components["offset_loss"].item())
print("One training step:", round(elapsed, 2), "seconds")
