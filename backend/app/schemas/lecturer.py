from pydantic import BaseModel
from pydantic.config import ConfigDict
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .timeslot import TimeslotResponse

class LecturerResponse(BaseModel):
    id: int
    name: str
    email: str
    specialty: Optional[str] = None
    available_timeslots: List["TimeslotResponse"]

    model_config = ConfigDict(from_attributes=True)

class LecturerAvailabilityResponse(BaseModel):
    id: int
    name: str
    email: str
    specialty: Optional[str] = None
    availability: Dict[str, List[str]]  # day -> list of times

    model_config = ConfigDict(from_attributes=True)

class LecturerCreate(BaseModel):
    name: str
    email: str
    specialty: Optional[str] = None
    availability: Optional[Dict[str, List[str]]] = None

class LecturerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    specialty: Optional[str] = None
    availability: Optional[Dict[str, List[str]]] = None

from .timeslot import TimeslotResponse
LecturerResponse.model_rebuild() 