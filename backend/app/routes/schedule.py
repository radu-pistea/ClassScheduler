from flask import Blueprint, jsonify, request
from scheduler_engine.generator import generate_schedule
from app import db
from app.models.schedule_entry import ScheduleEntry
from sqlalchemy import func
from app.schemas.schedule import ScheduleEntryResponse, RunSummaryResponse


schedule_bp = Blueprint('schedule', __name__)

# Helper to get the db session (if you have a get_db, otherwise use db.session)
def get_db():
    return db.session

@schedule_bp.route('/generate', methods=['POST'])
def generate_schedule_route():
    session = get_db()
    schedule_entries = generate_schedule(session)
    # Assume each entry is a dict or has to_dict()
    result = [entry.to_dict() if hasattr(entry, 'to_dict') else entry for entry in schedule_entries]
    return jsonify(result), 200

# GET /runs/<run_id>: returns all ScheduleEntry items for that run_id
@schedule_bp.route('/runs/<run_id>', methods=['GET'])
def get_schedule_by_run(run_id):
    entries = ScheduleEntry.query.filter_by(run_id=run_id).all()
    # Use Pydantic model for serialization
    result = [ScheduleEntryResponse.from_orm(entry).dict() for entry in entries]
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
        RunSummaryResponse(run_id=run_id, created_at=created_at).dict()
        for run_id, created_at in runs
    ]
    return jsonify(result), 200 