from pydantic import BaseModel
from pydantic.config import ConfigDict
from typing import Optional

class RoomResponse(BaseModel):
    id: int
    name: str
    capacity: Optional[int] = None

    model_config = ConfigDict(from_attributes=True) 