from pydantic import BaseModel
from pydantic.config import ConfigDict
from typing import Dict, List, Optional
from .timeslot import TimeslotResponse

class LecturerResponse(BaseModel):
    id: int
    name: str
    email: str
    specialty: Optional[str] = None
    available_timeslots: List[TimeslotResponse]

    model_config = ConfigDict(from_attributes=True)

class LecturerAvailabilityResponse(BaseModel):
    id: int
    name: str
    email: str
    specialty: Optional[str] = None
    availability: Dict[str, List[str]]  # day -> list of times

    model_config = ConfigDict(from_attributes=True) 