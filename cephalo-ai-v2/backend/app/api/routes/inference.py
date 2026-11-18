
# import logging

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from app.core.dependencies import predictor, inference_lock
# from app.db.database import get_db
# from app.db.models import Case
# from app.services.case_service import save_prediction
# from app.schemas.inference import InferenceResponse
# from app.inference.heatmap_service import save_heatmaps

# logger = logging.getLogger(__name__)

# router = APIRouter(prefix="/api/cases", tags=["Inference"])

# import time

# @router.post("/{case_id}/inference")
# def run_inference(case_id: int, db: Session = Depends(get_db)):
#     start = time.perf_counter()
#     print("[INFERENCE] Started")

#     case = db.get(Case, case_id)

#     if not case:
#         raise HTTPException(404, "Case not found")

#     print("[INFERENCE] Case loaded:", time.perf_counter() - start)

#     with inference_lock:
#         print("[INFERENCE] Running model...")
#         result = predictor.predict(case.image_path)

#     print("[INFERENCE] Prediction finished:", time.perf_counter() - start)

#     if not result.get("model_loaded"):
#         raise HTTPException(409, "Model not loaded")

#     save_prediction(db, case, result["points"])
#     heatmap_urls = save_heatmaps(
#         case_id=case.id,
#         heatmaps=result["heatmaps"]
#     )
#     print("[INFERENCE] Database saved:", time.perf_counter() - start)

#     return {
#     "case_id": case.id,
#     "status": "completed",
#     "model_loaded": True,
#     "image_width": case.image_width,
#     "image_height": case.image_height,
#     "mc_samples": result["mc_samples"],
#     "points": result["points"],
#     "measurements": case.measurements,
#     "heatmaps": heatmap_urls
# }
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import predictor, inference_lock
from app.db.database import get_db
from app.db.models import Case
from app.services.case_service import save_prediction
from app.schemas.inference import InferenceResponse
from app.inference.heatmap_service import save_heatmaps
from app.services.clinical_analysis import generate_clinical_analysis
from app.inference.heatmap_service import (
    save_heatmaps,
    save_heatmap_overlay
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cases", tags=["Inference"])

import time

@router.post("/{case_id}/inference")
def run_inference(case_id: int, db: Session = Depends(get_db)):
    start = time.perf_counter()
    print("[INFERENCE] Started")

    case = db.get(Case, case_id)

    if not case:
        raise HTTPException(404, "Case not found")

    print("[INFERENCE] Case loaded:", time.perf_counter() - start)

    with inference_lock:
        print("[INFERENCE] Running model...")
        result = predictor.predict(case.image_path)

    print("[INFERENCE] Prediction finished:", time.perf_counter() - start)

    if not result.get("model_loaded"):
        raise HTTPException(409, "Model not loaded")

    save_prediction(db, case, result["points"])
    
    heatmap_urls = save_heatmaps(
        case_id=case.id,
        heatmaps=result["heatmaps"]
    )

    overlay_url = save_heatmap_overlay(
        case_id=case.id,
        image_path=case.image_path,
        heatmaps=result["heatmaps"],
        points=result["points"]
    )
    return {
        "case_id": case.id,
        "status": "completed",
        "model_loaded": True,
        "image_width": case.image_width,
        "image_height": case.image_height,
        "mc_samples": result["mc_samples"],
        "points": result["points"],
        "measurements": case.measurements,
        "clinical_analysis": (
            generate_clinical_analysis(case.measurements)
            if case.measurements
            else None
        ),
        "heatmaps": heatmap_urls,
        "heatmap_overlay_url": overlay_url
    }