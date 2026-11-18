# Cephalo AI v2

A new, modular research implementation of an AI-assisted cephalometric landmark detection and analysis workflow. It keeps the requested model topology:

**Swin Transformer-style window-attention encoder → Attention U-Net decoder → 19 heatmaps + 2D offset regression → coordinate extraction/sub-pixel offset refinement → Monte Carlo dropout uncertainty → reliability bands.**

The system includes a vanilla HTML/CSS/JavaScript dashboard, FastAPI/PyTorch backend, SQLAlchemy persistence (SQLite by default; PostgreSQL via `DATABASE_URL`), dataset loader, training/validation loop, coordinate correction, angle calculations, ground-truth evaluation, comparison endpoint and JSON report export.

> **Research prototype only.** It is not a medical device. Do not use its outputs for diagnosis or treatment. A checkpoint must be trained on correctly mapped annotations, validated on a held-out set, and externally reviewed before any clinical interpretation.

## 1. Requirements

- Python 3.10+ (3.11 recommended)
- PyTorch 2.2+; install a CUDA-enabled build if you have a supported NVIDIA GPU
- A copy of the ISBI 2015 Cephalometric X-ray dataset obtained under its applicable terms
- 19 correctly ordered landmark annotations per image

The repository intentionally does **not** contain the ISBI dataset or a fabricated trained checkpoint.

## 2. Install and start the backend

From the repository root:

### Windows PowerShell

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### macOS / Linux

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs: http://127.0.0.1:8000/docs  
Health: http://127.0.0.1:8000/api/health

SQLite database and uploads are created automatically under `database/` and `data/`.

## 3. Open the frontend

With the backend running, open `frontend/index.html` in a browser. The default API URL is `http://127.0.0.1:8000`. To override it, set `window.CEPHALO_API` before `app.js` is loaded, or edit the `API` constant at the top of `frontend/js/app.js`.

Upload a lateral cephalometric image. If the checkpoint is absent, the dashboard displays the image but **does not fabricate landmark predictions**. Once a checkpoint is trained and installed, it displays the 19 predictions, confidence proxy, uncertainty/reliability, heatmap, coordinate editing and recalculated angles.

## 4. Prepare annotation CSV

The loader accepts CSV or JSON. CSV is the easiest interchange format. Coordinates must be in **original-image pixel coordinates**, and point indices must exactly follow the `LANDMARK_NAMES` order in `backend/app/core/config.py`.

CSV header:

```csv
image,x0,y0,x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,x6,y6,x7,y7,x8,y8,x9,y9,x10,y10,x11,y11,x12,y12,x13,y13,x14,y14,x15,y15,x16,y16,x17,y17,x18,y18
```

Generate a blank template from your image folder:

```bash
python scripts/make_annotation_template.py /path/to/images --output annotations.csv
```

Fill every x/y cell from the official annotation files after verifying the coordinate convention, image association and landmark ordering. Do not assume that an annotation export uses the same order or origin without checking it. JSON is also accepted:

```json
[
  {"image":"case001.png", "landmarks":[[120,90],[220,80]]}
]
```

The JSON example above is abbreviated for readability; each image must contain exactly 19 `[x,y]` pairs.

## 5. Train the model

Place images in one folder and create the annotation CSV. Then run from `backend/` with the virtual environment active:

```bash
python -m app.training.train --images ../data/images --annotations ../data/annotations.csv --epochs 80 --batch-size 2 --lr 0.0001 --val-ratio 0.2
```

The trainer:

- creates a deterministic train/validation split (default 80/20)
- applies augmentation to training data only; validation data has no augmentation
- uses intensity normalization, CLAHE and 512×512 resizing
- avoids horizontal flipping because that would require a verified left/right landmark-index permutation
- trains heatmap MSE plus heatmap-weighted offset L1 loss
- clips gradients and saves the best validation-loss checkpoint

Checkpoint output: `weights/swin_attention_unet.pt`. Restart the API after training so the inference service loads it.

**Important dataset caveat:** this project does not guess the official ISBI annotation-file format. Convert the official files into the documented canonical CSV/JSON format, then visually verify a sample of converted coordinates overlaid on their source images before training. A coordinate-order or image-scaling mistake can make a model appear to train while learning the wrong targets.

## 6. Core API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | API and checkpoint status |
| POST | `/api/cases` | Upload image and run inference |
| POST | `/api/cases/{id}/inference` | Re-run inference after installing a trained checkpoint |
| GET | `/api/cases/{id}` | Retrieve case |
| PATCH | `/api/cases/{id}/landmarks/{index}` | Correct a landmark; recalculate measurements |
| POST | `/api/cases/{id}/ground-truth` | Supply 19 ground-truth points and calculate MRE/SDR |
| GET | `/api/cases/{id}/comparison` | Initial vs corrected landmarks/measurements/errors |
| GET | `/api/cases/{id}/report` | Structured report payload |
| GET | `/api/analytics/summary` | Case and reliability summary |

Ground-truth request body:

```json
{"points":[[100,120],[130,110]]}
```

The request above is abbreviated; send exactly 19 points. You may also send objects with `x` and `y` fields. Coordinates must use the original uploaded image's pixel space.

## 7. Measurement and metric interpretation

- SNA uses Sella–Nasion–A-point (indices 0, 1, 4).
- SNB uses Sella–Nasion–B-point (indices 0, 1, 5).
- ANB = SNA − SNB.
- These are computed from pixel coordinates. Angular geometry is scale invariant, but clinical validity still depends on correct landmark definitions, image orientation and annotation protocol.
- MRE and SDR in this prototype are reported in **pixels**, not millimetres. Convert to millimetres only when a valid image calibration factor is available.
- Reliability currently uses Monte Carlo coordinate spread with provisional thresholds (<2 px High, <5 px Moderate, otherwise Low). The confidence value is a heuristic derived from spread, not a calibrated probability. Calibrate thresholds and confidence on a held-out validation cohort before reporting them as clinical reliability.

## 8. What still requires research validation

1. Confirm exact ISBI 2015 landmark ordering and annotation-coordinate conventions from the official dataset documentation.
2. Verify the Swin-style encoder against the exact paper/specification expected by your project; this compact implementation uses alternating regular/shifted window attention with learned relative-position bias and patch downsampling; it is not a pretrained official Swin checkpoint.
3. Run multi-seed experiments and report held-out MRE/SDR per landmark, not only aggregate loss.
4. Calibrate uncertainty and reliability against actual localization error.
5. Add clinically validated image calibration and complete the measurement set only after the exact landmark definitions are agreed.
6. Validate with a qualified clinician and follow dataset licensing, privacy and institutional requirements.

## 9. Tests

From `backend/`:

```bash
pip install pytest
pytest
```

## 10. PostgreSQL (optional)

Install a PostgreSQL driver (`pip install psycopg[binary]`) and set:

```bash
# PowerShell
$env:DATABASE_URL = "postgresql+psycopg://user:password@localhost:5432/cephalo"

# bash
export DATABASE_URL='postgresql+psycopg://user:password@localhost:5432/cephalo'
```

Start the API. SQLAlchemy creates the tables on startup.
