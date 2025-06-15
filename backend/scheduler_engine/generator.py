from app.models.lecturer import Lecturer
from app.models.module import Module
from app.models.room import Room
from app.models.timeslot import Timeslot
from app.models.schedule_entry import ScheduleEntry
from app import db
from scheduler_engine.constraints import is_valid_assignment
import uuid
from datetime import datetime
from collections import defaultdict

# Helper to convert SQLAlchemy objects to dicts

def obj_to_dict(obj):
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

def generate_schedule(session):
    """
    Generates a schedule by assigning each module to a lecturer, room, and timeslot without conflicts.
    Saves results as ScheduleEntry objects in the DB.
    Returns a dict with 'schedule' (list of saved entries) and 'conflicts' (list of conflict dicts).
    """
    # Clear previous schedule batch
    session.query(ScheduleEntry).delete()
    session.commit()

    # Assign a new run_id and created_at for this batch
    run_id = str(uuid.uuid4())
    created_at = datetime.utcnow()

    lecturers = [obj_to_dict(l) for l in Lecturer.query.all()]
    modules = [obj_to_dict(m) for m in Module.query.all()]
    rooms = [obj_to_dict(r) for r in Room.query.all()]
    timeslots = [obj_to_dict(t) for t in Timeslot.query.filter_by(is_weekend=False).all()]

    schedule = []  # List of assignments
    schedule_entries = []  # List of ScheduleEntry objects
    conflicts = []  # List of conflict dicts
    lecturer_timeslot_map = defaultdict(set)  # lecturer_id -> set of timeslot_id

    # For each module, try to assign required weekly hours
    for module in modules:
        hours_needed = int(module['weekly_hours'])
        assigned_hours = 0
        for lecturer in lecturers:
            lecturer_avail = lecturer.get('availability', {})
            if not lecturer_avail:
                continue
            for room in rooms:
                for timeslot in timeslots:
                    day = timeslot['day']
                    start_time = timeslot['start_time']
                    end_time = timeslot['end_time']
                    timeslot_id = timeslot['id']
                    if day not in lecturer_avail or start_time not in lecturer_avail[day]:
                        continue
                    # Check if room has sufficient capacity
                    if module['expected_students'] > room['capacity']:
                        conflicts.append({
                            "type": "room_over_capacity",
                            "room_id": room['id'],
                            "module_id": module['id'],
                            "capacity": room['capacity'],
                            "required": module['expected_students']
                        })
                        continue
                    # Check if lecturer is already booked at this timeslot
                    if timeslot_id in lecturer_timeslot_map[lecturer['id']]:
                        conflicts.append({
                            "type": "lecturer_overlap",
                            "lecturer_id": lecturer['id'],
                            "timeslot_id": timeslot_id,
                            "module_id": module['id']
                        })
                        continue
                    lecturer_assignments = [a for a in schedule if a['lecturer']['id'] == lecturer['id']]
                    if len(lecturer_assignments) >= lecturer.get('max_weekly_hours', hours_needed):
                        continue
                    module_assignments = [a for a in schedule if a['module']['id'] == module['id']]
                    if len(module_assignments) >= hours_needed:
                        break
                    if is_valid_assignment(lecturer, module, room, timeslot, schedule):
                        assignment = {
                            'module': module,
                            'lecturer': lecturer,
                            'room': room,
                            'timeslot': timeslot
                        }
                        schedule.append(assignment)
                        # Create ScheduleEntry instance
                        entry = ScheduleEntry(
                            module_id=module['id'],
                            lecturer_id=lecturer['id'],
                            room_id=room['id'],
                            timeslot_id=timeslot['id'],
                            day=day,
                            start_time=start_time,
                            end_time=end_time,
                            run_id=run_id,
                            created_at=created_at
                        )
                        session.add(entry)
                        schedule_entries.append(entry)
                        lecturer_timeslot_map[lecturer['id']].add(timeslot_id)
                        assigned_hours += 1
                        if assigned_hours >= hours_needed:
                            break
                if assigned_hours >= hours_needed:
                    break
            if assigned_hours >= hours_needed:
                break
    session.commit()
    # Return only entries for this run_id
    return {
        'schedule': [entry.to_dict() for entry in ScheduleEntry.query.filter_by(run_id=run_id).all()],
        'conflicts': conflicts
    }
