
from app.db.models import Case
from app.services.case_service import correct_landmark


def test_correction_preserves_original_prediction():
    original = [
        {
            "index": i,
            "name": f"Landmark_{i}",
            "x": float(100 + i),
            "y": float(200 + i),
        }
        for i in range(19)
    ]

    case = Case(
        image_width=512,
        image_height=512,
        landmarks=[p.copy() for p in original],
        initial_landmarks=[p.copy() for p in original],
        history=[],
    )

    correct_landmark(
        db=FakeDB(),
        case=case,
        index=5,
        x=150,
        y=250,
    )

    assert case.initial_landmarks == original
    assert case.landmarks[5]["x"] == 150
    assert case.landmarks[5]["y"] == 250
    assert case.landmarks[5]["manually_corrected"] is True


class FakeDB:
    def commit(self):
        pass

    def refresh(self, case):
        pass
