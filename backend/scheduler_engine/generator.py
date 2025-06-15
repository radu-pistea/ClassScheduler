from app.models.lecturer import Lecturer
from app.models.module import Module
from app.models.room import Room
from app.models.timeslot import Timeslot
from app.models.schedule_entry import ScheduleEntry
from app import db
from scheduler_engine.constraints import is_valid_assignment
import uuid
from datetime import datetime

# Helper to convert SQLAlchemy objects to dicts

def obj_to_dict(obj):
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

def generate_schedule(session):
    """
    Generates a schedule by assigning each module to a lecturer, room, and timeslot without conflicts.
    Saves results as ScheduleEntry objects in the DB.
    Returns a list of saved entries (dicts).
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
                    if day not in lecturer_avail or start_time not in lecturer_avail[day]:
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
                        assigned_hours += 1
                        if assigned_hours >= hours_needed:
                            break
                if assigned_hours >= hours_needed:
                    break
            if assigned_hours >= hours_needed:
                break
    session.commit()
    # Return only entries for this run_id
    return [entry.to_dict() for entry in ScheduleEntry.query.filter_by(run_id=run_id).all()]
