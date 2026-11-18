
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.core.config import UPLOAD_DIR
from app.core.dependencies import predictor
from app.db.database import Base, engine, get_db
from app.db.models import Case

from app.api.router import api_router

from app.services.case_service import correct_landmark
from app.measurements.cephalometry import calculate_measurements
from app.training.metrics import localization_metrics
from app.core.config import HEATMAP_DIR
from app.services.clinical_analysis import generate_clinical_analysis
# =========================================================
# DATABASE INITIALIZATION
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Cephalo AI v2",
    version="2.0.0",
    description=(
        "Research prototype for cephalometric "
        "landmark detection and analysis."
    )
)


# =========================================================
# MIDDLEWARE
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to frontend origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# STATIC FILE SERVING
# =========================================================

app.mount(
    "/uploads",
    StaticFiles(directory=str(UPLOAD_DIR)),
    name="uploads"
)
app.mount(
    "/heatmaps",
    StaticFiles(directory=str(HEATMAP_DIR)),
    name="heatmaps"
)

# =========================================================
# API ROUTER REGISTRATION
# =========================================================

app.include_router(api_router)


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/api/health", tags=["Health"])
def health():

    return {
        "status": "ok",
        "model_loaded": predictor.loaded,
        "device": str(predictor.device),
        "landmarks": 19
    }


# =========================================================
# GET CASE DETAILS
# =========================================================

@app.get("/api/cases/{case_id}", tags=["Cases"])
def get_case(
    case_id: int,
    db: Session = Depends(get_db)
):

    case = db.get(Case, case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found."
        )

    return {
        "case_id": case.id,
        "patient_code": case.patient_code,
        "image_url": f"/uploads/{Path(case.image_path).name}",
        "width": case.image_width,
        "height": case.image_height,
        "points": case.landmarks or [],
        "measurements": case.measurements or {},
        "clinical_analysis": (
            generate_clinical_analysis(case.measurements)
            if case.measurements
            else None
        ),
        
        "history": case.history or [],
        "evaluation": case.evaluation or {}
    }


# =========================================================
# CORRECT LANDMARK
# =========================================================

@app.patch(
    "/api/cases/{case_id}/landmarks/{index}",
    tags=["Landmarks"]
)
def edit_landmark(
    case_id: int,
    index: int,
    payload: dict,
    db: Session = Depends(get_db)
):

    case = db.get(Case, case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found."
        )

    try:
        case = correct_landmark(
            db,
            case,
            index,
            payload["x"],
            payload["y"]
        )

    except (ValueError, KeyError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    return {
        "points": case.landmarks,
        "measurements": case.measurements,
        "clinical_analysis": (
            generate_clinical_analysis(case.measurements)
            if case.measurements
            else None
        ),
        "history": case.history,
        "evaluation": case.evaluation or {}
    }


# =========================================================
# RESET LANDMARK CORRECTIONS
# =========================================================

@app.post(
    "/api/cases/{case_id}/reset",
    tags=["Landmarks"]
)
def reset_case(
    case_id: int,
    db: Session = Depends(get_db)
):

    case = db.get(Case, case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found."
        )

    if not case.initial_landmarks:
        raise HTTPException(
            status_code=409,
            detail="No original AI prediction is stored for this case."
        )

    case.landmarks = case.initial_landmarks

    case.measurements = calculate_measurements(
        case.landmarks
    )

    case.history = (case.history or []) + [
        {
            "type": "restored original AI prediction"
        }
    ]

    # Recalculate evaluation against existing ground truth
    if case.ground_truth:
        predicted = [
            [point["x"], point["y"]]
            for point in case.landmarks
        ]

        truth = [
            [point["x"], point["y"]]
            if isinstance(point, dict)
            else point
            for point in case.ground_truth
        ]

        case.evaluation = localization_metrics(
            predicted,
            truth
        )
    else:
        case.evaluation = {}

    db.commit()
    db.refresh(case)

    return {
        "points": case.landmarks,
        "measurements": case.measurements,
        "clinical_analysis": (
            generate_clinical_analysis(case.measurements)
            if case.measurements
            else None
        ),
        "history": case.history,
        "evaluation": case.evaluation
    }


# =========================================================
# SET GROUND TRUTH AND EVALUATE
# =========================================================

@app.post(
    "/api/cases/{case_id}/ground-truth",
    tags=["Evaluation"]
)
def set_ground_truth(
    case_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):

    case = db.get(Case, case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found."
        )

    if not case.landmarks or len(case.landmarks) != 19:
        raise HTTPException(
            status_code=409,
            detail="Run inference before evaluation."
        )

    points = payload.get("points", [])

    if not isinstance(points, list) or len(points) != 19:
        raise HTTPException(
            status_code=400,
            detail="Exactly 19 ground-truth points are required."
        )

    try:
        truth = []

        for point in points:

            if isinstance(point, dict):
                x = float(point["x"])
                y = float(point["y"])
            else:
                x = float(point[0])
                y = float(point[1])

            if not (
                0 <= x < case.image_width
                and 0 <= y < case.image_height
            ):
                raise ValueError(
                    "Ground-truth coordinates must be within image boundaries."
                )

            truth.append([x, y])

        predicted = [
            [point["x"], point["y"]]
            for point in case.landmarks
        ]

        result = localization_metrics(
            predicted,
            truth
        )

        case.ground_truth = points
        case.evaluation = result

        db.commit()
        db.refresh(case)

        return result

    except (ValueError, KeyError, TypeError, IndexError) as error:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"Invalid ground-truth coordinates: {error}"
        )


# =========================================================
# ANALYTICS SUMMARY
# =========================================================

@app.get(
    "/api/analytics/summary",
    tags=["Analytics"]
)
def analytics(
    db: Session = Depends(get_db)
):

    cases = db.query(Case).all()

    reliability = {
        "High": 0,
        "Moderate": 0,
        "Low": 0
    }

    for case in cases:

        for point in (case.landmarks or []):

            category = point.get("reliability")

            if category in reliability:
                reliability[category] += 1

    return {
        "cases": len(cases),
        "reliability": reliability,
        "model_loaded": predictor.loaded,
        "note": (
            "MRE/SDR is computed only for cases "
            "with supplied ground truth."
        )
    }


# =========================================================
# BEFORE / AFTER COMPARISON
# =========================================================

@app.get(
    "/api/cases/{case_id}/comparison",
    tags=["Reports"]
)
def comparison(
    case_id: int,
    db: Session = Depends(get_db)
):

    case = db.get(Case, case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found."
        )

    before = case.initial_landmarks or []
    after = case.landmarks or []

    before_evaluation = {}
    after_evaluation = case.evaluation or {}

    if case.ground_truth and before:

        truth = [
            [point["x"], point["y"]]
            if isinstance(point, dict)
            else point
            for point in case.ground_truth
        ]

        before_evaluation = localization_metrics(
            [
                [point["x"], point["y"]]
                for point in before
            ],
            truth
        )

        if len(after) == 19:
            after_evaluation = localization_metrics(
                [
                    [point["x"], point["y"]]
                    for point in after
                ],
                truth
            )

    return {
        "before_landmarks": before,
        "after_landmarks": after,
        "before_measurements": calculate_measurements(before),
        "after_measurements": case.measurements or {},
        "corrected_count": sum(
            1
            for point in after
            if point.get("manually_corrected")
        ),
        "before_evaluation": before_evaluation,
        "after_evaluation": after_evaluation
    }


# =========================================================
# GENERATE / RETRIEVE CASE REPORT
# =========================================================

@app.get(
    "/api/cases/{case_id}/report",
    tags=["Reports"]
)
def report(
    case_id: int,
    db: Session = Depends(get_db)
):

    case = db.get(Case, case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found."
        )

    return {
        "title": "Cephalometric AI Analysis Report",
        "case_id": case.id,
        "patient_code": case.patient_code,
        "created_at": case.created_at.isoformat(),
        "landmarks": case.landmarks or [],
        "initial_landmarks": case.initial_landmarks or [],
        "measurements": case.measurements or {},
        "clinical_analysis": (
            generate_clinical_analysis(case.measurements)
            if case.measurements
            else None
        ),
        "evaluation": case.evaluation or {},
        "history": case.history or [],
        "disclaimer": (
            "Research decision-support prototype. "
            "Not validated for diagnosis or treatment planning."
        )
    }


# =========================================================
# ROOT
# =========================================================

@app.get("/", tags=["Health"])
def root():

    return {
        "message": "Cephalo AI API is running.",
        "version": "2.0.0",
        "docs": "/docs"
    }
