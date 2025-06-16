from app import db
from datetime import datetime

class ScheduleEntry(db.Model):
    __tablename__ = 'schedule_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturers.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    timeslot_id = db.Column(db.Integer, db.ForeignKey('timeslots.id'), nullable=False)
    run_id = db.Column(db.String(36), nullable=False)  # UUID for batch runs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships with backrefs
    module = db.relationship('Module', backref=db.backref('schedule_entries', lazy=True))
    lecturer = db.relationship('Lecturer', backref=db.backref('schedule_entries', lazy=True))
    room = db.relationship('Room', backref=db.backref('schedule_entries', lazy=True))
    timeslot = db.relationship('Timeslot', backref=db.backref('schedule_entries', lazy=True))
    
    def __repr__(self):
        return f'<ScheduleEntry {self.module_id} {self.lecturer_id} {self.room_id} {self.timeslot_id}>' 