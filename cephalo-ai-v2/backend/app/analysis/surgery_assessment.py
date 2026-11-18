
"""
Preliminary orthognathic surgery decision-support assessment.

This module generates research-oriented considerations from
skeletal classification and jaw-position assessments.

It does NOT prescribe surgery or determine surgical movements.
"""


def assess_surgical_considerations(
    classification: dict,
    jaw_assessment: dict,
) -> dict:
    """
    Generate preliminary surgical considerations.

    Parameters:
        classification:
            Output from classify_skeletal_pattern()

        jaw_assessment:
            Output from assess_jaws()
    """

    if not isinstance(classification, dict):
        raise ValueError("Classification must be a dictionary.")

    if not isinstance(jaw_assessment, dict):
        raise ValueError("Jaw assessment must be a dictionary.")

    considerations = []

    maxilla = jaw_assessment.get("maxillary_assessment", {})
    mandible = jaw_assessment.get("mandibular_assessment", {})

    skeletal_class = classification.get("classification")

    maxillary_status = maxilla.get("assessment")
    mandibular_status = mandible.get("assessment")

    if (
        classification.get("status") != "calculated"
        or maxilla.get("status") != "calculated"
        or mandible.get("status") != "calculated"
    ):
        return {
            "status": "insufficient_data",
            "considerations": [],
            "summary": (
                "Insufficient measurement information for "
                "preliminary surgical considerations."
            ),
            "clinical_note": (
                "A qualified orthodontist and maxillofacial surgeon "
                "must assess the complete clinical record."
            ),
        }

    # Maxillary considerations
    if maxillary_status == "possible retrusion":
        considerations.append({
            "procedure": "Maxillary advancement evaluation",
            "region": "maxilla",
            "reason": (
                "SNA is below the preliminary reference range."
            ),
            "type": "possible_consideration",
        })

    elif maxillary_status == "possible protrusion":
        considerations.append({
            "procedure": "Maxillary setback evaluation",
            "region": "maxilla",
            "reason": (
                "SNA is above the preliminary reference range."
            ),
            "type": "possible_consideration",
        })

    # Mandibular considerations
    if mandibular_status == "possible retrusion":
        considerations.append({
            "procedure": "Mandibular advancement evaluation",
            "region": "mandible",
            "reason": (
                "SNB is below the preliminary reference range."
            ),
            "type": "possible_consideration",
        })

    elif mandibular_status == "possible protrusion":
        considerations.append({
            "procedure": "Mandibular setback evaluation",
            "region": "mandible",
            "reason": (
                "SNB is above the preliminary reference range."
            ),
            "type": "possible_consideration",
        })

    # Bimaxillary evaluation
    if len(considerations) == 2:
        considerations.append({
            "procedure": "Bimaxillary surgery evaluation",
            "region": "both jaws",
            "reason": (
                "Both maxillary and mandibular angular assessments "
                "show deviations from their preliminary reference ranges."
            ),
            "type": "further_evaluation",
        })

    if not considerations:
        summary = (
            "No jaw-position-based surgical consideration was "
            "flagged by the preliminary SNA/SNB assessment."
        )
    else:
        summary = (
            "One or more possible surgical evaluation areas "
            "were identified. Further clinical assessment is required."
        )

    return {
        "status": "calculated",
        "skeletal_classification": skeletal_class,
        "considerations": considerations,
        "summary": summary,
        "method": (
            "Rule-based preliminary assessment using ANB, SNA and SNB "
            "classification outputs."
        ),
        "clinical_note": (
            "These are research decision-support flags, not surgical "
            "recommendations. Actual treatment planning requires "
            "clinical examination, facial and dental assessment, "
            "occlusion analysis, imaging and specialist judgment."
        ),
    }
