from app import db
from datetime import datetime

class Timeslot(db.Model):
    __tablename__ = 'timeslots'
    
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_weekend = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    schedule_entries = db.relationship('ScheduleEntry', backref='timeslot', lazy=True)
    available_lecturers = db.relationship('Lecturer', secondary='lecturer_timeslot', backref=db.backref('available_timeslots', lazy=True))
    
    def __repr__(self):
        return f'<Timeslot {self.day} {self.start_time}-{self.end_time}>'
    
    @staticmethod
    def validate_time_format(time_str):
        """Validate time format (HH:MM)"""
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_day(day):
        """Validate day is a valid weekday"""
        valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return day in valid_days
    
    @staticmethod
    def is_weekend_day(day):
        """Check if the day is a weekend day"""
        return day in ['Saturday', 'Sunday']
