
import cv2
import torch
import numpy as np
from pathlib import Path

from app.inference.predictor import Predictor

# Initialize trained model
predictor = Predictor()

assert predictor.loaded, "Checkpoint was not loaded!"

# Change this to an actual X-ray image path
IMAGE_PATH = Path("C:/Users/srini/OneDrive/Desktop/sem 4-1/Capstone/cephalo-ai-v2/data/ISBI2015/RawImage/Test1Data/160.bmp")

# Run prediction
result = predictor.predict(
    IMAGE_PATH,
    mc_samples=12
)

print("\nMODEL PREDICTION RESULTS")
print("-----------------------")

print("Model loaded:", result["model_loaded"])
print("Image dimensions:",
      result["image_width"], "x", result["image_height"])

print("Number of landmarks:", len(result["points"]))

for point in result["points"]:
    print(
        f"{point['index'] + 1:02d}. "
        f"{point['name']}: "
        f"({point['x']}, {point['y']}) | "
        f"Uncertainty: {point['uncertainty_px']} px | "
        f"Reliability: {point['reliability']}"
    )

# Visualize predicted landmarks
image = cv2.imread(
    str(IMAGE_PATH),
    cv2.IMREAD_GRAYSCALE
)

visualization = cv2.cvtColor(
    image,
    cv2.COLOR_GRAY2BGR
)

for point in result["points"]:
    x = int(round(point["x"]))
    y = int(round(point["y"]))

    cv2.circle(
        visualization,
        (x, y),
        7,
        (0, 0, 255),
        -1
    )

    cv2.putText(
        visualization,
        str(point["index"] + 1),
        (x + 8, y - 8),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        1
    )

cv2.imwrite(
    "prediction_visualization160.png",
    visualization
)

print("\nSaved: prediction_visualization160.png")
