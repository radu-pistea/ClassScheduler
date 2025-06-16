from app import db
from datetime import datetime

class Module(db.Model):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    program_level_id = db.Column(db.Integer, db.ForeignKey('program_levels.id'), nullable=False)
    weekly_hours = db.Column(db.Float, nullable=False)
    expected_students = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    program_level = db.relationship('ProgramLevel', backref=db.backref('modules', lazy=True))
    
    def __repr__(self):
        return f'<Module {self.code}>'
