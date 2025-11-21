from pydantic import BaseModel
from typing import Optional

class Well(BaseModel):
    well_name: str
    location: Optional[str] = None
    status: Optional[str] = None
    field: Optional[str] = None

class SeismicSurvey(BaseModel):
    survey_name: str
    survey_type: Optional[str] = None
    acquisition_date: Optional[str] = None

class Log(BaseModel):
    log_name: str
    well_name: str
    # Curve data can be complex, representing as a simple string for now
    curve_data: Optional[str] = None
