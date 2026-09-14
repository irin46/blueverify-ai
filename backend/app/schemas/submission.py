from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class SubmissionCreate(BaseModel):
    """
    Shape of the JSON body the user sends when POSTing a new submission.
    Pydantic validates every field automatically before it reaches the endpoint.
    """

    submitter_name: str = Field(..., min_length=1, examples=["Jane Doe"])
    org_name: str = Field(..., min_length=1, examples=["Green Earth NGO"])
    location_name: str = Field(..., min_length=1, examples=["Sundarbans Delta"])
    latitude: float = Field(..., ge=-90, le=90, examples=[21.9])
    longitude: float = Field(..., ge=-180, le=180, examples=[89.2])
    ecosystem_type: str = Field(..., examples=["mangrove"])
    area_hectares: float = Field(..., gt=0, examples=[120.5])
    start_date: date = Field(..., examples=["2023-06-01"])
    evidence_text: Optional[str] = Field(None, examples=["Sentinel-2 imagery confirms canopy regrowth."])


class SubmissionResponse(BaseModel):
    """
    Shape of the JSON we send back after saving a submission.
    Includes the database-generated id and created_at timestamp.
    """

    id: int
    submitter_name: str
    org_name: str
    location_name: str
    latitude: float
    longitude: float
    ecosystem_type: str
    area_hectares: float
    start_date: date
    evidence_text: Optional[str]
    is_duplicate_risk: bool
    duplicate_of_id: Optional[int]
    ai_score: Optional[float]
    ai_risk_level: Optional[str]
    ai_explanation: Optional[str]
    satellite_status: Optional[str]
    coastal_match: Optional[bool]
    satellite_explanation: Optional[str]
    ndvi: Optional[float]
    ndvi_status: Optional[str]
    ndvi_explanation: Optional[str]
    estimated_carbon_tco2e: Optional[float]
    credits_released: Optional[float]
    credit_stage: Optional[str]
    verification_status: str
    created_at: datetime

    # Tells Pydantic to read data from ORM objects (not just plain dicts)
    model_config = {"from_attributes": True}
