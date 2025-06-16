from app import db
from sqlalchemy.dialects.postgresql import JSON
import json
from datetime import datetime

# Association table for lecturer-timeslot relationship
lecturer_timeslot = db.Table('lecturer_timeslot',
    db.Column('lecturer_id', db.Integer, db.ForeignKey('lecturers.id'), primary_key=True),
    db.Column('timeslot_id', db.Integer, db.ForeignKey('timeslots.id'), primary_key=True)
)

class Lecturer(db.Model):
    __tablename__ = 'lecturers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    specialty = db.Column(db.String(200), nullable=True)
    max_weekly_hours = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Many-to-many relationship with timeslots
    available_timeslots = db.relationship("Timeslot", secondary=lecturer_timeslot, back_populates="available_lecturers")
    
    def __repr__(self):
        return f'<Lecturer {self.name}>'
