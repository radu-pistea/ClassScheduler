from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.timeslot import Timeslot
from app.models.user import User
from app import db
from functools import wraps
from sqlalchemy import or_, desc
from datetime import datetime

timeslots_bp = Blueprint('timeslots', __name__)

# HTTP Status Codes
BAD_REQUEST = 400
UNAUTHORIZED = 401
FORBIDDEN = 403
NOT_FOUND = 404
SERVER_ERROR = 500

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin:
            return error_response("Admin privileges required", FORBIDDEN)
            
        return fn(*args, **kwargs)
    return wrapper

def success_response(data, status_code=200):
    return jsonify({
        "status": "success",
        "data": data
    }), status_code

def error_response(message, status_code=BAD_REQUEST):
    return jsonify({
        "status": "error",
        "message": message
    }), status_code

def get_sort_params():
    """Get and validate sort parameters from request."""
    sort_by = request.args.get('sort_by', 'day').lower()
    sort_order = request.args.get('sort_order', 'asc').lower()
    
    # Validate sort_by field
    valid_sort_fields = {
        'day': Timeslot.day,
        'start_time': Timeslot.start_time,
        'end_time': Timeslot.end_time,
        'is_weekend': Timeslot.is_weekend
    }
    
    if sort_by not in valid_sort_fields:
        return None, error_response(
            f"Invalid sort field. Must be one of: {', '.join(valid_sort_fields.keys())}",
            BAD_REQUEST
        )
    
    # Validate sort_order
    if sort_order not in ['asc', 'desc']:
        return None, error_response(
            "Invalid sort order. Must be 'asc' or 'desc'",
            BAD_REQUEST
        )
    
    # Get the column to sort by
    sort_column = valid_sort_fields[sort_by]
    
    # Apply sort order
    if sort_order == 'desc':
        sort_column = desc(sort_column)
    
    return sort_column, None

def validate_timeslot_data(data, is_update=False):
    """Validate timeslot data"""
    if not is_update:
        required_fields = ['day', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"

    # Validate day
    if 'day' in data and not Timeslot.validate_day(data['day']):
        return False, "Invalid day. Must be a valid weekday"

    # Validate time format
    if 'start_time' in data and not Timeslot.validate_time_format(data['start_time']):
        return False, "Invalid start time format. Use HH:MM format"
    if 'end_time' in data and not Timeslot.validate_time_format(data['end_time']):
        return False, "Invalid end time format. Use HH:MM format"

    # Validate start time is before end time
    if 'start_time' in data and 'end_time' in data:
        start = datetime.strptime(data['start_time'], "%H:%M")
        end = datetime.strptime(data['end_time'], "%H:%M")
        if start >= end:
            return False, "Start time must be before end time"

    return True, None

@timeslots_bp.route('/', methods=['POST'])
@admin_required
def create_timeslot():
    if not request.is_json:
        return error_response("Missing JSON in request", BAD_REQUEST)

    data = request.get_json()
    
    # Validate data
    is_valid, error_message = validate_timeslot_data(data)
    if not is_valid:
        return error_response(error_message, BAD_REQUEST)

    # Set is_weekend based on day
    is_weekend = Timeslot.is_weekend_day(data['day'])

    try:
        timeslot = Timeslot(
            day=data['day'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            is_weekend=is_weekend
        )
        
        db.session.add(timeslot)
        db.session.commit()
        
        return success_response({
            "message": "Timeslot created successfully",
            "timeslot": timeslot.to_dict()
        }, 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to create timeslot", SERVER_ERROR)

@timeslots_bp.route('/', methods=['GET'])
@jwt_required()
def get_timeslots():
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '').strip()
        
        # Validate pagination parameters
        if page < 1:
            return error_response("Page number must be greater than 0", BAD_REQUEST)
        if per_page < 1 or per_page > 100:
            return error_response("Per page must be between 1 and 100", BAD_REQUEST)
        
        # Get sort parameters
        sort_column, sort_error = get_sort_params()
        if sort_error:
            return sort_error
        
        # Base query
        query = Timeslot.query
        
        # Apply search if provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Timeslot.day.ilike(search_term),
                    Timeslot.start_time.ilike(search_term),
                    Timeslot.end_time.ilike(search_term)
                )
            )
        
        # Apply sorting
        query = query.order_by(sort_column)
        
        # Get paginated results
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return success_response({
            "timeslots": [timeslot.to_dict() for timeslot in pagination.items],
            "pagination": {
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": page,
                "per_page": per_page,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev
            }
        })
    except Exception as e:
        return error_response("Failed to fetch timeslots", SERVER_ERROR)

@timeslots_bp.route('/<int:timeslot_id>', methods=['GET'])
@jwt_required()
def get_timeslot(timeslot_id):
    timeslot = Timeslot.query.get(timeslot_id)
    
    if not timeslot:
        return error_response("Timeslot not found", NOT_FOUND)
        
    return success_response({
        "timeslot": timeslot.to_dict()
    })

@timeslots_bp.route('/<int:timeslot_id>', methods=['PUT'])
@admin_required
def update_timeslot(timeslot_id):
    if not request.is_json:
        return error_response("Missing JSON in request", BAD_REQUEST)

    timeslot = Timeslot.query.get(timeslot_id)
    if not timeslot:
        return error_response("Timeslot not found", NOT_FOUND)

    data = request.get_json()
    
    # Validate data
    is_valid, error_message = validate_timeslot_data(data, is_update=True)
    if not is_valid:
        return error_response(error_message, BAD_REQUEST)

    try:
        # Update fields if provided
        if 'day' in data:
            timeslot.day = data['day']
            timeslot.is_weekend = Timeslot.is_weekend_day(data['day'])
        if 'start_time' in data:
            timeslot.start_time = data['start_time']
        if 'end_time' in data:
            timeslot.end_time = data['end_time']

        db.session.commit()
        
        return success_response({
            "message": "Timeslot updated successfully",
            "timeslot": timeslot.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to update timeslot", SERVER_ERROR)

@timeslots_bp.route('/<int:timeslot_id>', methods=['DELETE'])
@admin_required
def delete_timeslot(timeslot_id):
    timeslot = Timeslot.query.get(timeslot_id)
    
    if not timeslot:
        return error_response("Timeslot not found", NOT_FOUND)

    try:
        db.session.delete(timeslot)
        db.session.commit()
        
        return success_response({
            "message": "Timeslot deleted successfully"
        })
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to delete timeslot", SERVER_ERROR)
