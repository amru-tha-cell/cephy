
# from datetime import datetime
# from pydantic import BaseModel, Field

# from app.schemas.landmark import LandmarkPoint


# class CaseUploadResponse(BaseModel):
#     case_id: int
#     patient_code: str
#     image_url: str

#     image_width: int
#     image_height: int

#     status: str
#     model_loaded: bool

#     points: list[LandmarkPoint] = Field(default_factory=list)
#     measurements: dict = Field(default_factory=dict)


# class CaseResponse(BaseModel):
#     case_id: int
#     patient_code: str
#     image_url: str

#     image_width: int
#     image_height: int

#     created_at: datetime

#     points: list[LandmarkPoint] = Field(default_factory=list)
#     measurements: dict = Field(default_factory=dict)
#     history: list = Field(default_factory=list)
#     evaluation: dict = Field(default_factory=dict)
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.landmark import LandmarkPoint


class CaseUploadResponse(BaseModel):
    case_id: int
    patient_code: str
    image_url: str

    image_width: int
    image_height: int

    status: str
    model_loaded: bool

    points: list[LandmarkPoint] = Field(default_factory=list)
    measurements: dict = Field(default_factory=dict)


class CaseResponse(BaseModel):
    case_id: int
    patient_code: str
    image_url: str

    image_width: int
    image_height: int

    created_at: datetime

    points: list[LandmarkPoint] = Field(default_factory=list)
    measurements: dict = Field(default_factory=dict)
    clinical_analysis: Optional[dict] = None
    history: list = Field(default_factory=list)
    evaluation: dict = Field(default_factory=dict)