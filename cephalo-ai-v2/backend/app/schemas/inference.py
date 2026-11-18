
# from pydantic import BaseModel, Field

# from app.schemas.landmark import LandmarkPoint


# class InferenceResponse(BaseModel):
#     case_id: int
#     status: str = "completed"
#     model_loaded: bool
#     image_width: int
#     image_height: int
#     mc_samples: int

#     points: list[LandmarkPoint] = Field(default_factory=list)
#     measurements: dict = Field(default_factory=dict)
#     heatmaps: list = Field(default_factory=list)
from pydantic import BaseModel, Field
from typing import Optional

from app.schemas.landmark import LandmarkPoint


class InferenceResponse(BaseModel):
    case_id: int
    status: str = "completed"
    model_loaded: bool
    image_width: int
    image_height: int
    mc_samples: int

    points: list[LandmarkPoint] = Field(default_factory=list)
    measurements: dict = Field(default_factory=dict)
    clinical_analysis: Optional[dict] = None
    heatmaps: list = Field(default_factory=list)