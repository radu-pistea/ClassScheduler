from app import db
from datetime import datetime

class Timeslot(db.Model):
    __tablename__ = 'timeslots'
    
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.String(5), nullable=False)  # Format: "HH:MM"
    end_time = db.Column(db.String(5), nullable=False)    # Format: "HH:MM"
    is_weekend = db.Column(db.Boolean, default=False)
    
    # Many-to-many relationship with lecturers
    available_lecturers = db.relationship("Lecturer", secondary="lecturer_timeslot", back_populates="available_timeslots")
    
    def to_dict(self):
        return {
            'id': self.id,
            'day': self.day,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'is_weekend': self.is_weekend
        }
    
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
