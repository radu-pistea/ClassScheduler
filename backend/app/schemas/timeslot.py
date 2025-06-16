from pydantic import BaseModel
from pydantic.config import ConfigDict
from typing import List
from .lecturer import LecturerResponse

class TimeslotResponse(BaseModel):
    id: int
    day: str
    start_time: str  # Format: "HH:MM"
    end_time: str    # Format: "HH:MM"
    is_weekend: bool
    available_lecturers: List[LecturerResponse]

    model_config = ConfigDict(from_attributes=True) 