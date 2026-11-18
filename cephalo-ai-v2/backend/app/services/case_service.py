from sqlalchemy.orm import Session
from app.db.models import Case
from app.measurements.cephalometry import calculate_measurements

# def create_case(db:Session, patient_code, image_path, width, height):
#     case=Case(patient_code=patient_code,image_path=str(image_path),image_width=width,image_height=height)
#     db.add(case); db.commit(); db.refresh(case); return case

# def save_prediction(db:Session,case,points):
#     case.landmarks=points; case.initial_landmarks=points; case.measurements=calculate_measurements(points)
#     case.history=(case.history or [])+[{'type':'AI prediction','landmarks':points}]
#     db.commit(); db.refresh(case); return case

# def correct_landmark(db: Session, case, index, x, y):
#     if index < 0 or index >= 19:
#         raise ValueError('Landmark index must be between 0 and 18')

#     if not case.landmarks or len(case.landmarks) != 19:
#         raise ValueError('Case has no complete prediction to correct')

#     x = float(x)
#     y = float(y)

#     if not (0 <= x < case.image_width and 0 <= y < case.image_height):
#         raise ValueError('Coordinates must be within image boundaries')

#     points = [p.copy() for p in case.landmarks]

#     before = points[index].copy()

#     points[index] = {
#         **points[index],
#         'x': x,
#         'y': y,
#         'manually_corrected': True
#     }

#     case.landmarks = points

#     if not case.initial_landmarks:
#         case.initial_landmarks = points

#     case.measurements = calculate_measurements(points)

#     case.history = (case.history or []) + [{
#         "type": "AI prediction",
#         "landmarks": points
#     }]

#     db.commit()
#     db.refresh(case)

#     return casefrom sqlalchemy.orm import Session
from app.db.models import Case
from app.measurements.cephalometry import calculate_measurements

def create_case(db:Session, patient_code, image_path, width, height):
    case=Case(patient_code=patient_code,image_path=str(image_path),image_width=width,image_height=height)
    db.add(case); db.commit(); db.refresh(case); return case

def save_prediction(db:Session,case,points):
    case.landmarks=points; case.initial_landmarks=points; case.measurements=calculate_measurements(points)
    case.history=(case.history or [])+[{'type':'AI prediction','landmarks':points}]
    db.commit(); db.refresh(case); return case

def correct_landmark(db: Session, case, index, x, y):
    if index < 0 or index >= 19:
        raise ValueError('Landmark index must be between 0 and 18')

    if not case.landmarks or len(case.landmarks) != 19:
        raise ValueError('Case has no complete prediction to correct')

    x = float(x)
    y = float(y)

    if not (0 <= x < case.image_width and 0 <= y < case.image_height):
        raise ValueError('Coordinates must be within image boundaries')

    points = [p.copy() for p in case.landmarks]

    before = points[index].copy()

    points[index] = {
        **points[index],
        'x': x,
        'y': y,
        'manually_corrected': True
    }

    case.landmarks = points

    if not case.initial_landmarks:
        case.initial_landmarks = points

    case.measurements = calculate_measurements(points)

    case.history = (case.history or []) + [{
        "type": "Landmark correction",
        "landmark_index": index,
        "before": before,
        "after": points[index]
    }]

    db.commit()
    db.refresh(case)

    return case