from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = Path(os.getenv('CEPHALO_DATA_DIR', ROOT / 'data'))
UPLOAD_DIR = DATA_DIR / 'uploads'
WEIGHT_DIR = Path(os.getenv('CEPHALO_WEIGHT_DIR', ROOT / 'weights'))
DB_URL = os.getenv('DATABASE_URL', f"sqlite:///{(ROOT / 'database' / 'cephalo.db').as_posix()}")
IMAGE_SIZE = int(os.getenv('IMAGE_SIZE', '512'))
HEATMAP_DIR = DATA_DIR / "heatmaps"
NUM_LANDMARKS = 19
LANDMARK_NAMES = [
    'Sella', 'Nasion', 'Orbitale', 'Porion', 'Subspinale (A)',
    'Supramentale (B)', 'Pogonion', 'Menton', 'Gnathion', 'Gonion',
    'Incision Inferius', 'Incision Superius', 'Upper Lip', 'Lower Lip',
    'Subnasale', 'Soft Tissue Pogonion', 'Posterior Nasal Spine',
    'Anterior Nasal Spine', 'Articulare'
]
for p in (
    DATA_DIR,
    UPLOAD_DIR,
    HEATMAP_DIR,
    WEIGHT_DIR,
    ROOT / "database"
):
    p.mkdir(parents=True, exist_ok=True)
