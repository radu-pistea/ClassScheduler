import pytest
from app import create_app, db
from app.models.lecturer import Lecturer
from app.models.module import Module
from app.models.room import Room
from app.models.timeslot import Timeslot
from app.models.program_level import ProgramLevel
from app.models.schedule_entry import ScheduleEntry

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def seed_data():
    # Program Level
    program_level = ProgramLevel(name="Test Level")
    db.session.add(program_level)
    db.session.commit()
    # Lecturer
    lecturer = Lecturer(
        name="Test Lecturer",
        email="lect@test.com",
        specialty="Test",
    )
    lecturer.availability = {"Monday": ["09:00", "10:00"]}
    db.session.add(lecturer)
    # Module
    module = Module(
        code="TEST101",
        name="Test Module",
        description="Test Desc",
        program_level=program_level.name,
        weekly_hours=1
    )
    db.session.add(module)
    # Room
    room = Room(name="Test Room", capacity=10)
    db.session.add(room)
    # Timeslot
    t1 = Timeslot(day="Monday", start_time="09:00", end_time="10:00", is_weekend=False)
    db.session.add(t1)
    db.session.commit()


def test_generate_schedule_api(client):
    seed_data()
    # Call the API
    response = client.post('/api/schedule/generate')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check DB for ScheduleEntry
    entries = ScheduleEntry.query.all()
    assert len(entries) > 0 