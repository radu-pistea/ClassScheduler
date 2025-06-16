from pydantic import BaseModel
from typing import Optional
from pydantic.config import ConfigDict

class RoomBase(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None

class RoomCreate(RoomBase):
    name: str
    capacity: int

class RoomUpdate(RoomBase):
    pass

class RoomResponse(RoomBase):
    id: int

    model_config = ConfigDict(from_attributes=True) 