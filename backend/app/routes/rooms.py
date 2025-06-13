from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.room import Room
from app.models.user import User
from app import db
from functools import wraps
from sqlalchemy import or_, desc

rooms_bp = Blueprint('rooms', __name__)

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
        'name': Room.name,
        'capacity': Room.capacity
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

@rooms_bp.route('/', methods=['POST'])
@admin_required
def create_room():
    if not request.is_json:
        return error_response("Missing JSON in request", BAD_REQUEST)

    data = request.get_json()
    
    # Validate required fields
    if 'name' not in data:
        return error_response("Missing required field: name", BAD_REQUEST)

    # Validate capacity if provided
    if 'capacity' in data:
        try:
            capacity = int(data['capacity'])
            if capacity < 0:
                return error_response("Capacity must be a positive number", BAD_REQUEST)
        except (ValueError, TypeError):
            return error_response("Capacity must be a valid integer", BAD_REQUEST)

    # Check if room name already exists
    if Room.query.filter_by(name=data['name']).first():
        return error_response("Room name already exists", BAD_REQUEST)

    try:
        room = Room(
            name=data['name'],
            capacity=data.get('capacity')
        )
        
        db.session.add(room)
        db.session.commit()
        
        return success_response({
            "message": "Room created successfully",
            "room": room.to_dict()
        }, 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to create room", SERVER_ERROR)

@rooms_bp.route('/', methods=['GET'])
@jwt_required()
def get_rooms():
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
        query = Room.query
        
        # Apply search if provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Room.name.ilike(search_term)
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
            "rooms": [room.to_dict() for room in pagination.items],
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
        return error_response("Failed to fetch rooms", SERVER_ERROR)

@rooms_bp.route('/<int:room_id>', methods=['GET'])
@jwt_required()
def get_room(room_id):
    room = Room.query.get(room_id)
    
    if not room:
        return error_response("Room not found", NOT_FOUND)
        
    return success_response({
        "room": room.to_dict()
    })

@rooms_bp.route('/<int:room_id>', methods=['PUT'])
@admin_required
def update_room(room_id):
    if not request.is_json:
        return error_response("Missing JSON in request", BAD_REQUEST)

    room = Room.query.get(room_id)
    if not room:
        return error_response("Room not found", NOT_FOUND)

    data = request.get_json()
    
    # Check if name is being updated and if it's already taken
    if 'name' in data and data['name'] != room.name:
        if Room.query.filter_by(name=data['name']).first():
            return error_response("Room name already exists", BAD_REQUEST)

    # Validate capacity if provided
    if 'capacity' in data:
        try:
            capacity = int(data['capacity'])
            if capacity < 0:
                return error_response("Capacity must be a positive number", BAD_REQUEST)
        except (ValueError, TypeError):
            return error_response("Capacity must be a valid integer", BAD_REQUEST)

    try:
        # Update fields if provided
        if 'name' in data:
            room.name = data['name']
        if 'capacity' in data:
            room.capacity = int(data['capacity'])

        db.session.commit()
        
        return success_response({
            "message": "Room updated successfully",
            "room": room.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to update room", SERVER_ERROR)

@rooms_bp.route('/<int:room_id>', methods=['DELETE'])
@admin_required
def delete_room(room_id):
    room = Room.query.get(room_id)
    
    if not room:
        return error_response("Room not found", NOT_FOUND)

    try:
        db.session.delete(room)
        db.session.commit()
        
        return success_response({
            "message": "Room deleted successfully"
        })
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to delete room", SERVER_ERROR)
