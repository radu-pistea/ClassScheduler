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

def seed_test_data():
    """Seed test data for schedule generation"""
    # Create program level
    program_level = ProgramLevel(name="Test Level")
    db.session.add(program_level)
    db.session.commit()

    # Create lecturer with available timeslot
    lecturer = Lecturer(
        name="Test Lecturer",
        email="lect@test.com",
        specialty="Test"
    )
    db.session.add(lecturer)

    # Create module
    module = Module(
        code="TEST101",
        name="Test Module",
        description="Test Description",
        program_level=program_level.name,
        weekly_hours=2,
        expected_students=20
    )
    db.session.add(module)

    # Create room
    room = Room(
        name="Test Room",
        capacity=30
    )
    db.session.add(room)

    # Create timeslots
    timeslot1 = Timeslot(
        day="Monday",
        start_time="09:00",
        end_time="10:00",
        is_weekend=False
    )
    timeslot2 = Timeslot(
        day="Monday",
        start_time="10:00",
        end_time="11:00",
        is_weekend=False
    )
    db.session.add_all([timeslot1, timeslot2])

    # Add timeslots to lecturer's availability
    lecturer.available_timeslots.extend([timeslot1, timeslot2])
    
    db.session.commit()

def test_generate_schedule_api(client):
    """Test the schedule generation API endpoint"""
    # Seed test data
    seed_test_data()

    # Call the API
    response = client.post('/api/schedule/generate')
    
    # Assert response status
    assert response.status_code == 200, "API should return 200 OK"
    
    # Get and validate response data
    data = response.get_json()
    assert isinstance(data, dict), "Response should be a JSON object"
    assert 'schedule' in data, "Response should contain 'schedule' key"
    assert 'conflicts' in data, "Response should contain 'conflicts' key"
    
    # Validate schedule entries
    schedule = data['schedule']
    assert isinstance(schedule, list), "Schedule should be a list"
    
    if schedule:  # If any schedule entries were generated
        required_fields = {
            'id', 'module_id', 'lecturer_id', 'room_id', 'timeslot_id',
            'day', 'start_time', 'end_time', 'run_id', 'created_at'
        }
        
        for entry in schedule:
            # Check all required fields are present
            assert all(field in entry for field in required_fields), \
                f"Schedule entry missing required fields: {required_fields - set(entry.keys())}"
            
            # Validate field types
            assert isinstance(entry['id'], int), "id should be an integer"
            assert isinstance(entry['module_id'], int), "module_id should be an integer"
            assert isinstance(entry['lecturer_id'], int), "lecturer_id should be an integer"
            assert isinstance(entry['room_id'], int), "room_id should be an integer"
            assert isinstance(entry['timeslot_id'], int), "timeslot_id should be an integer"
            assert isinstance(entry['day'], str), "day should be a string"
            assert isinstance(entry['start_time'], str), "start_time should be a string"
            assert isinstance(entry['end_time'], str), "end_time should be a string"
            assert isinstance(entry['run_id'], str), "run_id should be a string"
            assert isinstance(entry['created_at'], str), "created_at should be a string"
    
    # Validate conflicts
    conflicts = data['conflicts']
    assert isinstance(conflicts, list), "Conflicts should be a list"
    
    if conflicts:  # If any conflicts were generated
        for conflict in conflicts:
            assert 'type' in conflict, "Conflict should have a type"
            assert conflict['type'] in {
                'lecturer_unavailable',
                'room_over_capacity',
                'lecturer_overlap'
            }, f"Unknown conflict type: {conflict['type']}"
            
            # Validate fields based on conflict type
            if conflict['type'] == 'lecturer_unavailable':
                assert all(key in conflict for key in ['lecturer_id', 'timeslot_id', 'module_id'])
            elif conflict['type'] == 'room_over_capacity':
                assert all(key in conflict for key in ['room_id', 'module_id', 'capacity', 'required'])
            elif conflict['type'] == 'lecturer_overlap':
                assert all(key in conflict for key in ['lecturer_id', 'timeslot_id', 'module_id']) 