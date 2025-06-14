from flask import Blueprint, jsonify, request
from scheduler_engine.generator import generate_schedule
from app import db

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