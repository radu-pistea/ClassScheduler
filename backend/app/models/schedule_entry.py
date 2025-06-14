from app import db

class ScheduleEntry(db.Model):
    __tablename__ = 'schedule_entries'

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturers.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    timeslot_id = db.Column(db.Integer, db.ForeignKey('timeslots.id'), nullable=False)
    day = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5), nullable=False)

    module = db.relationship('Module', backref='schedule_entries')
    lecturer = db.relationship('Lecturer', backref='schedule_entries')
    room = db.relationship('Room', backref='schedule_entries')
    timeslot = db.relationship('Timeslot', backref='schedule_entries')

    def to_dict(self):
        return {
            'id': self.id,
            'module_id': self.module_id,
            'lecturer_id': self.lecturer_id,
            'room_id': self.room_id,
            'timeslot_id': self.timeslot_id,
            'day': self.day,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'module': self.module.to_dict() if self.module else None,
            'lecturer': self.lecturer.to_dict() if self.lecturer else None,
            'room': self.room.to_dict() if self.room else None,
            'timeslot': self.timeslot.to_dict() if self.timeslot else None
        } 