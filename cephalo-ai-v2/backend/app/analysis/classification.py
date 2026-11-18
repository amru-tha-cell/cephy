
"""
Skeletal classification from ANB angle.

This is a preliminary, configurable research rule.
It is not a standalone clinical diagnosis.
"""

import math


# Initial research thresholds in degrees.
# These can be configured after clinical literature review.
CLASS_III_UPPER = 0.0
CLASS_I_UPPER = 4.0


def classify_skeletal_pattern(measurements: dict) -> dict:
    """
    Classify skeletal pattern using ANB.

    Rules:
        ANB < 0       -> Class III
        0 <= ANB <= 4 -> Class I
        ANB > 4       -> Class II
    """

    anb = measurements.get("ANB")

    if anb is None:
        return {
            "classification": None,
            "anb": None,
            "status": "unavailable",
            "interpretation": (
                "Skeletal classification cannot be calculated "
                "because the ANB measurement is unavailable."
            ),
            "method": "ANB-based preliminary classification"
        }

    try:
        anb = float(anb)
    except (TypeError, ValueError):
        raise ValueError("ANB must be a valid numeric value.")

    if not math.isfinite(anb):
        raise ValueError("ANB must be a finite numeric value.")

    if anb < CLASS_III_UPPER:
        classification = "Class III"
        interpretation = (
            "ANB is below 0 degrees, indicating a "
            "Class III skeletal relationship pattern."
        )

    elif anb <= CLASS_I_UPPER:
        classification = "Class I"
        interpretation = (
            "ANB is between 0 and 4 degrees, indicating a "
            "Class I skeletal relationship pattern."
        )

    else:
        classification = "Class II"
        interpretation = (
            "ANB is above 4 degrees, indicating a "
            "Class II skeletal relationship pattern."
        )

    return {
        "classification": classification,
        "anb": round(anb, 2),
        "status": "calculated",
        "interpretation": interpretation,
        "method": "ANB-based preliminary classification",
        "thresholds": {
            "class_III": "ANB < 0 degrees",
            "class_I": "0 <= ANB <= 4 degrees",
            "class_II": "ANB > 4 degrees"
        },
        "clinical_note": (
            "This is a preliminary research classification. "
            "Clinical interpretation requires assessment of "
            "the complete cephalometric analysis."
        )
    }
