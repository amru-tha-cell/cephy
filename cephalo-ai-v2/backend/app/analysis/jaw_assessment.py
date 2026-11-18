
"""
Preliminary maxillary and mandibular assessment using SNA and SNB.

Reference ranges are configurable research assumptions,
not universal clinical diagnostic standards.
"""

import math


# Configurable preliminary reference ranges (degrees).
SNA_REFERENCE = {
    "lower": 80.0,
    "upper": 84.0,
    "normal": 82.0,
}

SNB_REFERENCE = {
    "lower": 78.0,
    "upper": 82.0,
    "normal": 80.0,
}


def _assess_angle(value, reference, jaw_name, angle_name):
    if value is None:
        return {
            "jaw": jaw_name,
            "measurement": angle_name,
            "value": None,
            "assessment": "unavailable",
            "status": "unavailable",
            "interpretation": f"{angle_name} measurement is unavailable.",
        }

    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{angle_name} must be numeric.")

    if not math.isfinite(value):
        raise ValueError(f"{angle_name} must be finite.")

    lower = reference["lower"]
    upper = reference["upper"]

    if value < lower:
        assessment = "possible retrusion"
        interpretation = (
            f"{angle_name} is below the preliminary reference range. "
            f"This may indicate a retrusive {jaw_name} position."
        )
    elif value > upper:
        assessment = "possible protrusion"
        interpretation = (
            f"{angle_name} is above the preliminary reference range. "
            f"This may indicate a protrusive {jaw_name} position."
        )
    else:
        assessment = "within reference range"
        interpretation = (
            f"{angle_name} is within the preliminary reference range."
        )

    return {
        "jaw": jaw_name,
        "measurement": angle_name,
        "value": round(value, 2),
        "assessment": assessment,
        "status": "calculated",
        "reference_range": {
            "lower": lower,
            "upper": upper,
            "normal": reference["normal"],
        },
        "interpretation": interpretation,
    }


def assess_jaws(measurements: dict) -> dict:
    """
    Assess maxillary and mandibular position using SNA and SNB.

    Expected input:
        {
            "SNA": 82.0,
            "SNB": 80.0,
            "ANB": 2.0
        }
    """

    if not isinstance(measurements, dict):
        raise ValueError("Measurements must be provided as a dictionary.")

    maxilla = _assess_angle(
        measurements.get("SNA"),
        SNA_REFERENCE,
        "maxilla",
        "SNA",
    )

    mandible = _assess_angle(
        measurements.get("SNB"),
        SNB_REFERENCE,
        "mandible",
        "SNB",
    )

    return {
        "maxillary_assessment": maxilla,
        "mandibular_assessment": mandible,
        "method": "Preliminary SNA/SNB reference-range assessment",
        "reference_basis": "Configurable research assumptions",
        "clinical_note": (
            "These assessments are preliminary interpretations of "
            "angular measurements. They do not independently establish "
            "a clinical diagnosis or determine surgical treatment."
        ),
    }
