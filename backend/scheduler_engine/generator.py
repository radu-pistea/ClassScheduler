from app.models.lecturer import Lecturer
from app.models.module import Module
from app.models.room import Room
from app.models.timeslot import Timeslot
from app.models.schedule_entry import ScheduleEntry
from app import db
from scheduler_engine.constraints import is_valid_assignment
from app.schemas.module import ModuleResponse
from app.schemas.room import RoomResponse
from app.schemas.timeslot import TimeslotResponse
from app.schemas.lecturer import LecturerResponse
from app.schemas.schedule import ScheduleEntryResponse
import uuid
from datetime import datetime
from collections import defaultdict

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

    # Get lecturers with their available timeslots
    lecturers = Lecturer.query.all()
    modules = [ModuleResponse.model_validate(m).model_dump() for m in Module.query.all()]
    rooms = [RoomResponse.model_validate(r).model_dump() for r in Room.query.all()]
    timeslots = [TimeslotResponse.model_validate(t).model_dump() for t in Timeslot.query.filter_by(is_weekend=False).all()]

    schedule = []  # List of assignments
    schedule_entries = []  # List of ScheduleEntry objects
    conflicts = []  # List of conflict dicts
    lecturer_timeslot_map = defaultdict(set)  # lecturer_id -> set of timeslot_id

    # For each module, try to assign required weekly hours
    for module in modules:
        hours_needed = int(module['weekly_hours'])
        assigned_hours = 0
        for lecturer in lecturers:
            lecturer_dict = LecturerResponse.model_validate(lecturer).model_dump()
            for room in rooms:
                for timeslot in timeslots:
                    day = timeslot['day']
                    start_time = timeslot['start_time']
                    end_time = timeslot['end_time']
                    timeslot_id = timeslot['id']
                    
                    # Check if lecturer is available at this timeslot
                    if not any(ts.id == timeslot_id for ts in lecturer.available_timeslots):
                        conflicts.append({
                            "type": "lecturer_unavailable",
                            "lecturer_id": lecturer.id,
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
                    if timeslot_id in lecturer_timeslot_map[lecturer.id]:
                        conflicts.append({
                            "type": "lecturer_overlap",
                            "lecturer_id": lecturer.id,
                            "timeslot_id": timeslot_id,
                            "module_id": module['id']
                        })
                        continue
                        
                    lecturer_assignments = [a for a in schedule if a['lecturer']['id'] == lecturer.id]
                    if len(lecturer_assignments) >= lecturer_dict.get('max_weekly_hours', hours_needed):
                        continue
                    module_assignments = [a for a in schedule if a['module']['id'] == module['id']]
                    if len(module_assignments) >= hours_needed:
                        break
                    if is_valid_assignment(lecturer_dict, module, room, timeslot, schedule):
                        assignment = {
                            'module': module,
                            'lecturer': lecturer_dict,
                            'room': room,
                            'timeslot': timeslot
                        }
                        schedule.append(assignment)
                        # Create ScheduleEntry instance
                        entry = ScheduleEntry(
                            module_id=module['id'],
                            lecturer_id=lecturer.id,
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
                        lecturer_timeslot_map[lecturer.id].add(timeslot_id)
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
        'schedule': [ScheduleEntryResponse.model_validate(entry).model_dump() for entry in ScheduleEntry.query.filter_by(run_id=run_id).all()],
        'conflicts': conflicts
    }
