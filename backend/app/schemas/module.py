from pydantic import BaseModel
from typing import Optional
from pydantic.config import ConfigDict

class ModuleBase(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    weekly_hours: Optional[int] = None
    expected_students: Optional[int] = None
    program_level: Optional[str] = None
    description: Optional[str] = None

class ModuleCreate(ModuleBase):
    name: str
    code: str
    program_level: str
    weekly_hours: int

class ModuleUpdate(ModuleBase):
    pass

class ModuleResponse(ModuleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, obj):
        # Create a copy of the object to avoid modifying the original
        data = {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        
        # Handle program_level conversion
        if 'program_level' in data:
            if hasattr(data['program_level'], 'name'):
                data['program_level'] = data['program_level'].name
            # If it's already a string, leave it as is
        
        return cls(**data) 