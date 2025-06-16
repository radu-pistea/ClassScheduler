from pydantic import BaseModel
from pydantic.config import ConfigDict
from typing import Optional, List
from datetime import datetime

class ScheduleEntryResponse(BaseModel):
    id: int
    module_id: int
    lecturer_id: int
    room_id: int
    timeslot_id: int
    day: str
    start_time: str
    end_time: str
    run_id: str
    created_at: datetime
    # Optionally, nested models for module, lecturer, room, timeslot can be added here

    model_config = ConfigDict(from_attributes=True)

class RunSummaryResponse(BaseModel):
    run_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) 