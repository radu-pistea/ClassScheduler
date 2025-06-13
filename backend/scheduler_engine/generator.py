from app.models.lecturer import Lecturer
from app.models.module import Module
from app.models.room import Room
from app.models.timeslot import Timeslot
from app import db
from scheduler_engine.constraints import is_valid_assignment

# Helper to convert SQLAlchemy objects to dicts

def obj_to_dict(obj):
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

def generate_schedule():
    """
    Generates a schedule by assigning each module to a lecturer, room, and timeslot without conflicts.
    Returns a list of assignments (dicts).
    """
    lecturers = [obj_to_dict(l) for l in Lecturer.query.all()]
    modules = [obj_to_dict(m) for m in Module.query.all()]
    rooms = [obj_to_dict(r) for r in Room.query.all()]
    timeslots = [obj_to_dict(t) for t in Timeslot.query.filter_by(is_weekend=False).all()]

    schedule = []  # List of assignments

    # For each module, try to assign required weekly hours
    for module in modules:
        hours_needed = int(module['weekly_hours'])
        assigned_hours = 0
        for lecturer in lecturers:
            # Check lecturer availability and specialty (if needed)
            lecturer_avail = lecturer.get('availability', {})
            if not lecturer_avail:
                continue
            for room in rooms:
                for timeslot in timeslots:
                    # Check if lecturer is available at this timeslot
                    day = timeslot['day']
                    start_time = timeslot['start_time']
                    if day not in lecturer_avail or start_time not in lecturer_avail[day]:
                        continue
                    # Check max weekly hours for lecturer
                    lecturer_assignments = [a for a in schedule if a['lecturer']['id'] == lecturer['id']]
                    if len(lecturer_assignments) >= lecturer.get('max_weekly_hours', hours_needed):
                        continue
                    # Check if already assigned enough hours for this module
                    module_assignments = [a for a in schedule if a['module']['id'] == module['id']]
                    if len(module_assignments) >= hours_needed:
                        break
                    # Check constraints
                    if is_valid_assignment(lecturer, module, room, timeslot, schedule):
                        assignment = {
                            'module': module,
                            'lecturer': lecturer,
                            'room': room,
                            'timeslot': timeslot
                        }
                        schedule.append(assignment)
                        assigned_hours += 1
                        if assigned_hours >= hours_needed:
                            break
                if assigned_hours >= hours_needed:
                    break
            if assigned_hours >= hours_needed:
                break
    return schedule
