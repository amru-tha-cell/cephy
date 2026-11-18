
"""ISBI 2015 dataset loader.

Supported annotations:
1. ISBI TXT: 19 coordinate lines followed by 8 classification values.
2. CSV: image,x0,y0,...,x18,y18
3. JSON: [{"image": "...", "landmarks": [[x,y], ...]}]

Uses:
- CLAHE preprocessing
- Aspect-ratio-preserving resize and padding
- Gaussian landmark heatmaps
- Per-pixel offset regression targets
- Photometric augmentation for training only
"""

import csv
import json
import random
from pathlib import Path

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset

from app.core.config import IMAGE_SIZE, NUM_LANDMARKS
from app.training.preprocessing import (
    preprocess_image,
    transform_points,
)


NUM_CLASSIFICATIONS = 8


class CephDataset(Dataset):

    def __init__(
        self,
        image_dir,
        annotations,
        training=False,
        image_size=IMAGE_SIZE,
        sigma=5.0,
    ):
        self.image_dir = Path(image_dir)
        self.annotation_path = Path(annotations)

        self.training = training
        self.size = image_size
        self.sigma = sigma

        if self.size <= 0:
            raise ValueError("image_size must be positive.")

        if self.sigma <= 0:
            raise ValueError("sigma must be positive.")

        if not self.image_dir.is_dir():
            raise FileNotFoundError(
                f"Image directory not found: {self.image_dir}"
            )

        self.items = []

        if self.annotation_path.is_dir():
            self._load_txt_directory()

        elif self.annotation_path.suffix.lower() == ".json":
            self._load_json()

        elif self.annotation_path.suffix.lower() == ".csv":
            self._load_csv()

        elif self.annotation_path.suffix.lower() == ".txt":
            self._load_single_txt()

        else:
            raise ValueError(
                "Annotations must be a TXT directory, "
                "TXT file, CSV or JSON."
            )

        if not self.items:
            raise ValueError("No valid annotation records found.")

        print(
            f"Loaded {len(self.items)} images "
            f"from {self.annotation_path}"
        )

    # --------------------------------------------------
    # Annotation validation
    # --------------------------------------------------

    def _validate_record(self, name, points, classifications):

        image_name = Path(name)

        # Prevent accidental references outside the image directory.
        if image_name.name != str(name) or image_name.suffix.lower() != ".bmp":
            raise ValueError(
                f"Invalid image filename: {name}. "
                "Expected a BMP filename without directory components."
            )

        points = np.asarray(points, dtype=np.float32)

        if points.shape != (NUM_LANDMARKS, 2):
            raise ValueError(
                f"{name}: expected {NUM_LANDMARKS} coordinate pairs, "
                f"got {points.shape}"
            )

        if not np.isfinite(points).all():
            raise ValueError(
                f"{name}: coordinates contain NaN or infinite values."
            )

        classifications = np.asarray(
            classifications,
            dtype=np.int64
        )

        if classifications.shape != (NUM_CLASSIFICATIONS,):
            raise ValueError(
                f"{name}: expected {NUM_CLASSIFICATIONS} classifications."
            )

        self.items.append(
            (
                self.image_dir / image_name,
                points,
                classifications
            )
        )

    # --------------------------------------------------
    # ISBI TXT parser
    # --------------------------------------------------

    def _parse_txt(self, annotation_file):

        lines = [
            line.strip()
            for line in annotation_file.read_text(
                encoding="utf-8-sig"
            ).splitlines()
            if line.strip()
        ]

        expected = NUM_LANDMARKS + NUM_CLASSIFICATIONS

        if len(lines) != expected:
            raise ValueError(
                f"{annotation_file.name}: expected {expected} "
                f"non-empty lines, got {len(lines)}"
            )

        points = []

        for line in lines[:NUM_LANDMARKS]:

            values = [value.strip() for value in line.split(",")]

            if len(values) != 2:
                raise ValueError(
                    f"{annotation_file.name}: invalid coordinate line: {line}"
                )

            try:
                x, y = float(values[0]), float(values[1])
            except ValueError as exc:
                raise ValueError(
                    f"{annotation_file.name}: invalid coordinates: {line}"
                ) from exc

            points.append([x, y])

        try:
            classifications = [
                int(value)
                for value in lines[NUM_LANDMARKS:]
            ]
        except ValueError as exc:
            raise ValueError(
                f"{annotation_file.name}: classifications must be integers."
            ) from exc

        return points, classifications

    def _load_txt_directory(self):

        image_files = sorted(
            self.image_dir.glob("*.bmp")
        )

        if not image_files:
            raise ValueError(
                f"No BMP images found in {self.image_dir}"
            )

        for image_path in image_files:

            annotation_file = (
                self.annotation_path / f"{image_path.stem}.txt"
            )

            if not annotation_file.exists():
                raise FileNotFoundError(
                    f"Missing annotation: {annotation_file}"
                )

            points, classifications = self._parse_txt(
                annotation_file
            )

            self._validate_record(
                image_path.name,
                points,
                classifications
            )

    def _load_single_txt(self):

        points, classifications = self._parse_txt(
            self.annotation_path
        )

        image_name = self.annotation_path.stem + ".bmp"

        self._validate_record(
            image_name,
            points,
            classifications
        )

    # --------------------------------------------------
    # JSON parser
    # --------------------------------------------------

    def _load_json(self):

        rows = json.loads(
            self.annotation_path.read_text(
                encoding="utf-8"
            )
        )

        if not isinstance(rows, list):
            raise ValueError(
                "JSON annotations must contain a list of records."
            )

        for index, row in enumerate(rows):

            if not isinstance(row, dict):
                raise ValueError(
                    f"JSON record {index} must be an object."
                )

            name = (
                row.get("image")
                or row.get("filename")
                or row.get("file")
            )

            if not name:
                raise ValueError(
                    f"JSON record {index} has no image filename."
                )

            points = row.get("landmarks")

            if points is None:
                raise ValueError(
                    f"{name}: missing landmarks."
                )

            classifications = row.get(
                "classifications",
                row.get("classes", [0] * NUM_CLASSIFICATIONS)
            )

            self._validate_record(
                name,
                points,
                classifications
            )

    # --------------------------------------------------
    # CSV parser
    # --------------------------------------------------

    def _load_csv(self):

        with self.annotation_path.open(
            newline="",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(file)
            rows = list(reader)

            if reader.fieldnames is None:
                raise ValueError("CSV file has no header.")

        for index, row in enumerate(rows):

            name = (
                row.get("image")
                or row.get("filename")
                or row.get("file")
            )

            if not name:
                raise ValueError(
                    f"CSV record {index} has no image filename."
                )

            try:
                points = [
                    [
                        float(row[f"x{i}"]),
                        float(row[f"y{i}"])
                    ]
                    for i in range(NUM_LANDMARKS)
                ]

                if all(
                    f"c{i}" in row and row[f"c{i}"] not in (None, "")
                    for i in range(NUM_CLASSIFICATIONS)
                ):
                    classifications = [
                        int(row[f"c{i}"])
                        for i in range(NUM_CLASSIFICATIONS)
                    ]
                else:
                    classifications = [
                        0
                    ] * NUM_CLASSIFICATIONS

            except (KeyError, ValueError, TypeError) as exc:
                raise ValueError(
                    f"CSV record {index}: invalid coordinate "
                    "or classification columns."
                ) from exc

            self._validate_record(
                name,
                points,
                classifications
            )

    # --------------------------------------------------
    # Dataset length
    # --------------------------------------------------

    def __len__(self):
        return len(self.items)

    # --------------------------------------------------
    # Image augmentation
    # --------------------------------------------------

    def _augment_image(self, image):

        # Random brightness and contrast variation.
        if random.random() < 0.5:

            contrast = random.uniform(0.85, 1.15)
            brightness = random.uniform(-0.04, 0.04)

            image = np.clip(
                image * contrast + brightness,
                0,
                1
            )

        # Small Gaussian noise.
        if random.random() < 0.3:

            noise = np.random.normal(
                0,
                0.012,
                image.shape
            ).astype(np.float32)

            image = np.clip(
                image + noise,
                0,
                1
            )

        return image.astype(np.float32)

    # --------------------------------------------------
    # Main data loading
    # --------------------------------------------------

    def __getitem__(self, index):

        path, original_points, classifications = self.items[index]

        image = cv2.imread(
            str(path),
            cv2.IMREAD_GRAYSCALE
        )

        if image is None:
            raise FileNotFoundError(
                f"Could not read image: {path}"
            )

        h, w = image.shape

        # Validate coordinates against original image dimensions.
        if (
            np.any(original_points[:, 0] < 0)
            or np.any(original_points[:, 0] >= w)
            or np.any(original_points[:, 1] < 0)
            or np.any(original_points[:, 1] >= h)
        ):
            raise ValueError(
                f"{path.name}: landmark coordinates exceed "
                "image boundaries."
            )

        # CLAHE preprocessing.
        image = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        ).apply(image)

        # Resize and pad while preserving aspect ratio.
        image, transform = preprocess_image(
            image,
            image_size=self.size
        )

        # Apply the exact same geometric transformation to landmarks.
        points = transform_points(
            original_points,
            transform
        )

        # Normalize pixel values to [0, 1].
        image = image.astype(np.float32) / 255.0

        # Training-only photometric augmentation.
        # No geometric augmentation or horizontal flipping.
        if self.training:
            image = self._augment_image(image)

        # --------------------------------------------------
        # Generate heatmaps and offset targets
        # --------------------------------------------------

        heatmaps = np.zeros(
            (
                NUM_LANDMARKS,
                self.size,
                self.size
            ),
            dtype=np.float32
        )

        offsets = np.zeros(
            (
                NUM_LANDMARKS,
                2,
                self.size,
                self.size
            ),
            dtype=np.float32
        )

        yy, xx = np.mgrid[
            0:self.size,
            0:self.size
        ]

        for j, (x, y) in enumerate(points):

            # Gaussian heatmap centered at the landmark.
            gaussian = np.exp(
                -(
                    (xx - x) ** 2 +
                    (yy - y) ** 2
                ) / (2 * self.sigma ** 2)
            )

            heatmaps[j] = gaussian.astype(np.float32)

            # Offset from every pixel to the landmark.
            offsets[j, 0] = x - xx
            offsets[j, 1] = y - yy

        # --------------------------------------------------
        # Return tensors
        # --------------------------------------------------

        return {
            "image": torch.from_numpy(
                image[None].copy()
            ),

            "heatmaps": torch.from_numpy(
                heatmaps
            ),

            "offsets": torch.from_numpy(
                offsets
            ),

            "points": torch.from_numpy(
                points.copy()
            ),

            "original_points": torch.from_numpy(
                original_points.copy()
            ),

            "classifications": torch.tensor(
                classifications,
                dtype=torch.long
            ),

            "path": str(path),

            "scale_x": torch.tensor(
                transform["scale_x"],
                dtype=torch.float32
            ),

            "scale_y": torch.tensor(
                transform["scale_y"],
                dtype=torch.float32
            ),

            "pad_x": torch.tensor(
                transform["pad_x"],
                dtype=torch.float32
            ),

            "pad_y": torch.tensor(
                transform["pad_y"],
                dtype=torch.float32
            )
        }
