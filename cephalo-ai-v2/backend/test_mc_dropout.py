
import torch
from app.training.model import SwinAttentionUNet

torch.manual_seed(42)

model = SwinAttentionUNet()
model.eval()

# Activate dropout without changing BatchNorm evaluation mode.
for module in model.modules():
    if isinstance(module, (torch.nn.Dropout, torch.nn.Dropout2d)):
        module.train()

x = torch.randn(1, 1, 512, 512)

predictions = []

with torch.no_grad():
    for _ in range(5):
        output = model(x)
        predictions.append(output["heatmaps"])

predictions = torch.stack(predictions)

variation = predictions.std(dim=0).mean().item()

print("Prediction shape:", predictions.shape)
print("Mean prediction variation:", variation)
print("Dropout stochasticity:", variation > 0)
