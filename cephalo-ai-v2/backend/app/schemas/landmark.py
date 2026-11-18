
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Literal
import math


class LandmarkPoint(BaseModel):
    index: int = Field(ge=0, le=18)
    name: str
    x: float
    y: float

    uncertainty_px: float = Field(ge=0)
    confidence: float = Field(ge=0, le=1)

    reliability: Literal["High", "Moderate", "Low"]

    manually_corrected: bool = False


class LandmarkCorrection(BaseModel):
    x: float
    y: float

    @field_validator("x", "y")
    @classmethod
    def validate_finite_coordinates(cls, value):
        if not math.isfinite(value):
            raise ValueError("Coordinates must be finite numbers")
        return value


class LandmarkUpdateResponse(BaseModel):
    points: list[LandmarkPoint]
    measurements: dict
    history: list
    evaluation: dict
