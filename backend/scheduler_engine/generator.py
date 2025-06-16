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
from sqlalchemy.orm import joinedload

def convert_time_to_str(time_obj):
    """Convert datetime.time to string in HH:MM format"""
    if hasattr(time_obj, 'strftime'):
        return time_obj.strftime('%H:%M')
    return str(time_obj)

def convert_datetime_to_str(dt_obj):
    """Convert datetime to ISO format string"""
    if hasattr(dt_obj, 'isoformat'):
        return dt_obj.isoformat()
    return str(dt_obj)

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

    # Get and convert modules to simple dicts
    modules = []
    for m in Module.query.all():
        modules.append({
            'id': m.id,
            'name': m.name,
            'code': m.code,
            'weekly_hours': float(m.weekly_hours),
            'expected_students': m.expected_students,
            'program_level': m.program_level.name if m.program_level else None,
            'description': m.description
        })

    # Get and convert rooms to simple dicts
    rooms = []
    for r in Room.query.all():
        rooms.append({
            'id': r.id,
            'name': r.name,
            'capacity': r.capacity
        })

    # Get and convert timeslots to simple dicts
    timeslots = []
    for t in Timeslot.query.filter_by(is_weekend=False).all():
        timeslots.append({
            'id': t.id,
            'day': t.day,
            'start_time': convert_time_to_str(t.start_time),
            'end_time': convert_time_to_str(t.end_time),
            'is_weekend': t.is_weekend
        })

    # Get lecturers and their available timeslots
    lecturers = []
    lecturer_timeslot_map = {}  # Map lecturer_id to list of timeslot_ids
    for l in Lecturer.query.all():
        lecturer_dict = {
            'id': l.id,
            'name': l.name,
            'email': l.email,
            'specialty': l.specialty,
            'max_weekly_hours': l.max_weekly_hours
        }
        lecturers.append(lecturer_dict)
        # Store available timeslots separately to avoid circular references
        lecturer_timeslot_map[l.id] = [ts.id for ts in l.available_timeslots]

    schedule = []  # List of assignments
    schedule_entries = []  # List of ScheduleEntry objects
    conflicts = []  # List of conflict dicts
    lecturer_timeslot_assignments = defaultdict(set)  # lecturer_id -> set of timeslot_id

    # For each module, try to assign required weekly hours
    for module in modules:
        hours_needed = int(module['weekly_hours'])
        assigned_hours = 0
        for lecturer in lecturers:
            for room in rooms:
                for timeslot in timeslots:
                    timeslot_id = timeslot['id']
                    
                    # Check if lecturer is available at this timeslot
                    if timeslot_id not in lecturer_timeslot_map[lecturer['id']]:
                        conflicts.append({
                            "type": "lecturer_unavailable",
                            "lecturer_id": lecturer['id'],
                            "timeslot_id": timeslot_id,
                            "module_id": module['id']
                        })
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
                    if timeslot_id in lecturer_timeslot_assignments[lecturer['id']]:
                        conflicts.append({
                            "type": "lecturer_overlap",
                            "lecturer_id": lecturer['id'],
                            "timeslot_id": timeslot_id,
                            "module_id": module['id']
                        })
                        continue
                        
                    lecturer_assignments = [a for a in schedule if a['lecturer']['id'] == lecturer['id']]
                    if len(lecturer_assignments) >= lecturer['max_weekly_hours']:
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
                            run_id=run_id,
                            created_at=created_at
                        )
                        session.add(entry)
                        schedule_entries.append(entry)
                        lecturer_timeslot_assignments[lecturer['id']].add(timeslot_id)
                        assigned_hours += 1
                        if assigned_hours >= hours_needed:
                            break
                if assigned_hours >= hours_needed:
                    break
            if assigned_hours >= hours_needed:
                break
    session.commit()

    # Get the entries for this run with their related timeslot information
    entries = (ScheduleEntry.query
              .filter_by(run_id=run_id)
              .join(Timeslot)
              .add_columns(
                  ScheduleEntry.id,
                  ScheduleEntry.module_id,
                  ScheduleEntry.lecturer_id,
                  ScheduleEntry.room_id,
                  ScheduleEntry.timeslot_id,
                  ScheduleEntry.run_id,
                  ScheduleEntry.created_at,
                  Timeslot.day,
                  Timeslot.start_time,
                  Timeslot.end_time
              )
              .all())

    schedule_entries = []
    for entry in entries:
        schedule_entries.append({
            'id': entry.id,
            'module_id': entry.module_id,
            'lecturer_id': entry.lecturer_id,
            'room_id': entry.room_id,
            'timeslot_id': entry.timeslot_id,
            'day': entry.day,
            'start_time': convert_time_to_str(entry.start_time),
            'end_time': convert_time_to_str(entry.end_time),
            'run_id': entry.run_id,
            'created_at': convert_datetime_to_str(entry.created_at)
        })

    return {
        'schedule': schedule_entries,
        'conflicts': conflicts
    }
