import random
from datetime import time
from app import create_app, db
from app.models.lecturer import Lecturer
from app.models.module import Module
from app.models.room import Room
from app.models.timeslot import Timeslot
from app.models.program_level import ProgramLevel
from sqlalchemy import text

app = create_app()

LECTURERS = [
    {"name": f"Lecturer {i}", "email": f"lecturer{i}@example.com"}
    for i in range(1, 10)
]

MODULES = [
    {"name": "Mathematics", "code": "MATH101"},
    {"name": "Physics", "code": "PHYS101"},
    {"name": "Chemistry", "code": "CHEM101"},
    {"name": "Biology", "code": "BIO101"},
    {"name": "Computer Science", "code": "CS101"},
]

ROOMS = [
    {"name": "Room A"},
    {"name": "Room B"},
    {"name": "Room C"},
]

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
times = [
    ("08:00", "09:00"), ("09:00", "10:00"), ("10:00", "11:00"), ("11:00", "12:00"),
    ("12:00", "13:00"), ("13:00", "14:00"), ("14:00", "15:00"), ("15:00", "16:00"),
    ("16:00", "17:00"), ("17:00", "18:00")
]

def parse_time(time_str):
    """Convert time string to time object"""
    return time.fromisoformat(time_str)

def seed():
    with app.app_context():
        # Remove all existing data
        db.session.execute(text('DELETE FROM lecturer_timeslot'))
        db.session.query(Lecturer).delete()
        db.session.query(Module).delete()
        db.session.query(Room).delete()
        db.session.query(Timeslot).delete()
        db.session.commit()

        # Add rooms
        room_objs = []
        for i, room in enumerate(ROOMS):
            capacity = random.randint(40, 60)
            r = Room(name=room["name"], capacity=capacity)
            db.session.add(r)
            room_objs.append(r)
        db.session.commit()

        # Add timeslots
        timeslot_objs = []
        for i in range(10):
            day = random.choice(days)
            start, end = times[i % len(times)]
            t = Timeslot(
                day=day,
                start_time=parse_time(start),
                end_time=parse_time(end),
                is_weekend=False
            )
            db.session.add(t)
            timeslot_objs.append(t)
        db.session.commit()

        # Add lecturers
        lecturer_objs = []
        for l in LECTURERS:
            lecturer = Lecturer(
                name=l["name"],
                email=l["email"],
                specialty=random.choice(["AI", "Networks", "Databases"]),
                max_weekly_hours=random.randint(15, 30)
            )
            lecturer.available_timeslots = random.sample(timeslot_objs, k=random.randint(7, 10))
            db.session.add(lecturer)
            lecturer_objs.append(lecturer)
        db.session.commit()

        # Ensure at least one program level exists
        program_level = ProgramLevel.query.first()
        if not program_level:
            program_level = ProgramLevel(name="Undergraduate")
            db.session.add(program_level)
            db.session.commit()

        # Add modules
        for m in MODULES:
            weekly_hours = random.randint(1, 3)
            expected_students = random.randint(10, 40)
            module = Module(
                name=m["name"],
                code=m["code"],
                weekly_hours=weekly_hours,
                expected_students=expected_students,
                program_level_id=program_level.id
            )
            db.session.add(module)
        db.session.commit()

        print("Mock data seeded successfully.")

if __name__ == "__main__":
    seed() 