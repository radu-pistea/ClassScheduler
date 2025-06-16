from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.lecturer import Lecturer
from app.models.user import User
from app import db
from functools import wraps
from sqlalchemy import or_, desc
from app.schemas.lecturer import LecturerResponse, LecturerCreate, LecturerUpdate
from app.schemas.timeslot import TimeslotResponse

lecturers_bp = Blueprint('lecturers', __name__)

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
    sort_by = request.args.get('sort_by', 'name').lower()
    sort_order = request.args.get('sort_order', 'asc').lower()
    
    # Validate sort_by field
    valid_sort_fields = {
        'name': Lecturer.name,
        'email': Lecturer.email,
        'specialty': Lecturer.specialty
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

@lecturers_bp.route('/', methods=['POST'])
@admin_required
def create_lecturer():
    if not request.is_json:
        return error_response("Missing JSON in request", BAD_REQUEST)

    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'email']
    for field in required_fields:
        if field not in data:
            return error_response(f"Missing required field: {field}", BAD_REQUEST)

    # Check if email already exists
    if Lecturer.query.filter_by(email=data['email']).first():
        return error_response("Email already registered", BAD_REQUEST)

    try:
        lecturer = Lecturer(
            name=data['name'],
            email=data['email'],
            specialty=data.get('specialty'),
            availability=data.get('availability')
        )
        
        db.session.add(lecturer)
        db.session.commit()
        
        return success_response({
            "message": "Lecturer created successfully",
            "lecturer": LecturerResponse.model_validate(lecturer).model_dump()
        }, 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to create lecturer", SERVER_ERROR)

@lecturers_bp.route('/', methods=['GET'])
@jwt_required()
def get_lecturers():
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
        query = Lecturer.query
        
        # Apply search if provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Lecturer.name.ilike(search_term),
                    Lecturer.specialty.ilike(search_term)
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
            "lecturers": [LecturerResponse.model_validate(lecturer).model_dump() for lecturer in pagination.items],
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
        return error_response("Failed to fetch lecturers", SERVER_ERROR)

@lecturers_bp.route('/<int:lecturer_id>', methods=['GET'])
@jwt_required()
def get_lecturer(lecturer_id):
    lecturer = Lecturer.query.get(lecturer_id)
    
    if not lecturer:
        return error_response("Lecturer not found", NOT_FOUND)
        
    return success_response({
        "lecturer": LecturerResponse.model_validate(lecturer).model_dump()
    })

@lecturers_bp.route('/<int:lecturer_id>', methods=['PUT'])
@admin_required
def update_lecturer(lecturer_id):
    if not request.is_json:
        return error_response("Missing JSON in request", BAD_REQUEST)

    lecturer = Lecturer.query.get(lecturer_id)
    if not lecturer:
        return error_response("Lecturer not found", NOT_FOUND)

    data = request.get_json()
    
    # Check if email is being updated and if it's already taken
    if 'email' in data and data['email'] != lecturer.email:
        if Lecturer.query.filter_by(email=data['email']).first():
            return error_response("Email already registered", BAD_REQUEST)

    try:
        # Update fields if provided
        if 'name' in data:
            lecturer.name = data['name']
        if 'email' in data:
            lecturer.email = data['email']
        if 'specialty' in data:
            lecturer.specialty = data['specialty']
        if 'availability' in data:
            lecturer.availability = data['availability']

        db.session.commit()
        
        return success_response({
            "message": "Lecturer updated successfully",
            "lecturer": LecturerResponse.model_validate(lecturer).model_dump()
        })
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to update lecturer", SERVER_ERROR)

@lecturers_bp.route('/<int:lecturer_id>', methods=['DELETE'])
@admin_required
def delete_lecturer(lecturer_id):
    lecturer = Lecturer.query.get(lecturer_id)
    
    if not lecturer:
        return error_response("Lecturer not found", NOT_FOUND)

    try:
        db.session.delete(lecturer)
        db.session.commit()
        
        return success_response({
            "message": "Lecturer deleted successfully"
        })
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to delete lecturer", SERVER_ERROR)

@lecturers_bp.route('/<int:lecturer_id>/timeslots', methods=['POST'])
def add_available_timeslot(lecturer_id):
    lecturer = Lecturer.query.get_or_404(lecturer_id)
    data = request.get_json()
    timeslot_id = data.get('timeslot_id')
    timeslot = Timeslot.query.get_or_404(timeslot_id)
    lecturer.available_timeslots.append(timeslot)
    db.session.commit()
    return jsonify({
        "message": "Timeslot added successfully",
        "lecturer": LecturerResponse.model_validate(lecturer).model_dump()
    }), 200
