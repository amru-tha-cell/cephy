
"""
Central clinical analysis service.

Combines:
1. Skeletal classification using ANB
2. Maxillary and mandibular assessment using SNA/SNB
3. Preliminary surgical considerations

This service does not modify the existing landmark detector
or cephalometric measurement calculations.
"""

from app.analysis.classification import classify_skeletal_pattern
from app.analysis.jaw_assessment import assess_jaws
from app.analysis.surgery_assessment import assess_surgical_considerations


def generate_clinical_analysis(measurements: dict) -> dict:
    """
    Generate the complete preliminary analysis from measurements.

    Expected input:
        {
            "SNA": 82.0,
            "SNB": 80.0,
            "ANB": 2.0
        }
    """

    if not isinstance(measurements, dict):
        raise ValueError("Measurements must be provided as a dictionary.")

    classification = classify_skeletal_pattern(measurements)

    jaw_assessment = assess_jaws(measurements)

    surgical_assessment = assess_surgical_considerations(
        classification,
        jaw_assessment
    )

    return {
        "status": "completed",
        "input_measurements": {
            "SNA": measurements.get("SNA"),
            "SNB": measurements.get("SNB"),
            "ANB": measurements.get("ANB"),
        },
        "skeletal_classification": classification,
        "jaw_assessment": jaw_assessment,
        "surgical_considerations": surgical_assessment,
        "disclaimer": (
            "Research decision-support output only. "
            "Not a confirmed clinical diagnosis or surgical prescription. "
            "Final interpretation and treatment planning require "
            "qualified orthodontic and maxillofacial specialist review."
        ),
    }
