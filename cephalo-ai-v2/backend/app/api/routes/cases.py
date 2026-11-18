
from pathlib import Path
import uuid
import cv2
import numpy as np

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException
)
from sqlalchemy.orm import Session

from app.core.config import UPLOAD_DIR
from app.core.dependencies import predictor
from app.db.database import get_db
from app.services.case_service import create_case
from app.schemas.case import CaseUploadResponse


router = APIRouter(prefix="/api/cases", tags=["Cases"])

ALLOWED_TYPES = {
    "image/png",
    "image/jpeg",
    "image/tiff",
    "image/bmp"
}

MAX_FILE_SIZE = 25 * 1024 * 1024


@router.post("", response_model=CaseUploadResponse)
async def upload_case(
    file: UploadFile = File(...),
    patient_code: str = Form("DEMO"),
    db: Session = Depends(get_db)
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Upload a PNG, JPEG, TIFF or BMP X-ray image."
        )

    data = await file.read()

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Maximum upload size is 25 MB."
        )

    image = cv2.imdecode(
        np.frombuffer(data, dtype=np.uint8),
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a readable image."
        )

    height, width = image.shape

    suffix = Path(file.filename or "xray.png").suffix.lower()

    if not suffix:
        suffix = ".png"

    filename = f"{uuid.uuid4().hex}{suffix}"
    target = UPLOAD_DIR / filename

    try:
        target.write_bytes(data)

        case = create_case(
            db,
            patient_code,
            target,
            width,
            height
        )

    except Exception:
        target.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="Could not create the case."
        )

    return {
        "case_id": case.id,
        "patient_code": case.patient_code,
        "image_url": f"/uploads/{filename}",
        "image_width": width,
        "image_height": height,
        "status": "uploaded",
        "model_loaded": predictor.loaded,
        "points": [],
        "measurements": {}
    }
