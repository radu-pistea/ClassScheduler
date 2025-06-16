from flask import Blueprint, jsonify, request
from scheduler_engine.generator import generate_schedule
from app import db
from app.models.schedule_entry import ScheduleEntry
from sqlalchemy import func
from app.schemas.schedule import ScheduleEntryResponse, RunSummaryResponse, ScheduleGenerationResponse
from datetime import datetime


schedule_bp = Blueprint('schedule', __name__)

# Helper to get the db session (if you have a get_db, otherwise use db.session)
def get_db():
    return db.session

@schedule_bp.route('/generate', methods=['POST'])
def generate_schedule_route():
    try:
        session = get_db()
        result = generate_schedule(session)
        
        # Ensure all values are basic Python types
        schedule = []
        for entry in result['schedule']:
            schedule.append({
                'id': int(entry['id']),
                'module_id': int(entry['module_id']),
                'lecturer_id': int(entry['lecturer_id']),
                'room_id': int(entry['room_id']),
                'timeslot_id': int(entry['timeslot_id']),
                'day': str(entry['day']),
                'start_time': str(entry['start_time']),
                'end_time': str(entry['end_time']),
                'run_id': str(entry['run_id']),
                'created_at': str(entry['created_at']) if entry['created_at'] else None
            })
        
        conflicts = []
        for conflict in result['conflicts']:
            conflicts.append({
                'type': str(conflict['type']),
                'lecturer_id': int(conflict.get('lecturer_id', 0)),
                'timeslot_id': int(conflict.get('timeslot_id', 0)),
                'module_id': int(conflict.get('module_id', 0)),
                'room_id': int(conflict.get('room_id', 0)),
                'capacity': int(conflict.get('capacity', 0)),
                'required': int(conflict.get('required', 0))
            })
        
        response = {
            'schedule': schedule,
            'conflicts': conflicts
        }
        
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# GET /runs/<run_id>: returns all ScheduleEntry items for that run_id
@schedule_bp.route('/runs/<run_id>', methods=['GET'])
def get_schedule_by_run(run_id):
    entries = ScheduleEntry.query.filter_by(run_id=run_id).all()
    # Use Pydantic model for serialization
    result = [ScheduleEntryResponse.from_orm(entry).model_dump() for entry in entries]
    return jsonify(result), 200

# GET /runs: returns a list of unique run_ids with their earliest created_at, ordered by date descending
@schedule_bp.route('/runs', methods=['GET'])
def list_runs():
    # Get unique run_ids and their earliest created_at
    runs = db.session.query(
        ScheduleEntry.run_id,
        func.min(ScheduleEntry.created_at).label('created_at')
    ).group_by(ScheduleEntry.run_id).order_by(func.min(ScheduleEntry.created_at).desc()).all()
    result = [
        RunSummaryResponse(run_id=run_id, created_at=created_at).model_dump()
        for run_id, created_at in runs
    ]
    return jsonify(result), 200 