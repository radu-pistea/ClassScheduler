from app import db
from sqlalchemy.dialects.postgresql import JSON
import json

class Lecturer(db.Model):
    __tablename__ = 'lecturers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    specialty = db.Column(db.String(200), nullable=True)
    _availability = db.Column('availability', db.Text, nullable=True)
    
    @property
    def availability(self):
        if self._availability is None:
            return None
        if isinstance(self._availability, str):
            try:
                return json.loads(self._availability)
            except Exception:
                return None
        return self._availability
    
    @availability.setter
    def availability(self, value):
        if value is None:
            self._availability = None
        elif isinstance(value, str):
            self._availability = value
        else:
            self._availability = json.dumps(value)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'specialty': self.specialty,
            'availability': self.availability
        }
