from app import db

class Module(db.Model):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    program_level = db.Column(db.String(50), nullable=False)
    weekly_hours = db.Column(db.Float, nullable=False)
    expected_students = db.Column(db.Integer, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'program_level': self.program_level,
            'weekly_hours': self.weekly_hours,
            'expected_students': self.expected_students
        }
