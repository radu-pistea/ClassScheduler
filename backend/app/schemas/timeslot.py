from pydantic import BaseModel
from typing import Optional, List, TYPE_CHECKING
from pydantic.config import ConfigDict

if TYPE_CHECKING:
    from .lecturer import LecturerResponse

class TimeslotBase(BaseModel):
    day: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    is_weekend: Optional[bool] = None

class TimeslotCreate(TimeslotBase):
    day: str
    start_time: str
    end_time: str
    is_weekend: bool

class TimeslotUpdate(TimeslotBase):
    pass

class TimeslotResponse(TimeslotBase):
    id: int
    available_lecturers: List["LecturerResponse"]

    model_config = ConfigDict(from_attributes=True)

from .lecturer import LecturerResponse
TimeslotResponse.model_rebuild() 