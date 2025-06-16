from pydantic import BaseModel
from pydantic.config import ConfigDict
from typing import Optional

class ModuleResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    program_level: str
    weekly_hours: float
    expected_students: Optional[int] = None

    model_config = ConfigDict(from_attributes=True) 