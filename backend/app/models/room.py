from app import db

class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'capacity': self.capacity
        }
