from pydantic import BaseModel
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

    class Config:
        orm_mode = True

class RunSummaryResponse(BaseModel):
    run_id: str
    created_at: datetime

    class Config:
        orm_mode = True 