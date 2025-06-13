from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.module import Module
from app.models.user import User
from app import db
from functools import wraps
from sqlalchemy import or_, desc

modules_bp = Blueprint('modules', __name__)

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
    sort_by = request.args.get('sort_by', 'code').lower()
    sort_order = request.args.get('sort_order', 'asc').lower()
    
    # Validate sort_by field
    valid_sort_fields = {
        'code': Module.code,
        'name': Module.name,
        'program_level': Module.program_level,
        'weekly_hours': Module.weekly_hours
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

@modules_bp.route('/', methods=['POST'])
@admin_required
def create_module():
    if not request.is_json:
        return error_response("Missing JSON in request", BAD_REQUEST)

    data = request.get_json()
    
    # Validate required fields
    required_fields = ['code', 'name', 'program_level', 'weekly_hours']
    for field in required_fields:
        if field not in data:
            return error_response(f"Missing required field: {field}", BAD_REQUEST)

    # Validate weekly_hours is a positive number
    try:
        weekly_hours = float(data['weekly_hours'])
        if weekly_hours <= 0:
            return error_response("Weekly hours must be a positive number", BAD_REQUEST)
    except (ValueError, TypeError):
        return error_response("Weekly hours must be a valid number", BAD_REQUEST)

    # Check if module code already exists
    if Module.query.filter_by(code=data['code']).first():
        return error_response("Module code already exists", BAD_REQUEST)

    try:
        module = Module(
            code=data['code'],
            name=data['name'],
            description=data.get('description'),
            program_level=data['program_level'],
            weekly_hours=weekly_hours
        )
        
        db.session.add(module)
        db.session.commit()
        
        return success_response({
            "message": "Module created successfully",
            "module": module.to_dict()
        }, 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to create module", SERVER_ERROR)

@modules_bp.route('/', methods=['GET'])
@jwt_required()
def get_modules():
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
        query = Module.query
        
        # Apply search if provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Module.code.ilike(search_term),
                    Module.name.ilike(search_term),
                    Module.description.ilike(search_term),
                    Module.program_level.ilike(search_term)
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
            "modules": [module.to_dict() for module in pagination.items],
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
        return error_response("Failed to fetch modules", SERVER_ERROR)

@modules_bp.route('/<int:module_id>', methods=['GET'])
@jwt_required()
def get_module(module_id):
    module = Module.query.get(module_id)
    
    if not module:
        return error_response("Module not found", NOT_FOUND)
        
    return success_response({
        "module": module.to_dict()
    })

@modules_bp.route('/<int:module_id>', methods=['PUT'])
@admin_required
def update_module(module_id):
    if not request.is_json:
        return error_response("Missing JSON in request", BAD_REQUEST)

    module = Module.query.get(module_id)
    if not module:
        return error_response("Module not found", NOT_FOUND)

    data = request.get_json()
    
    # Check if code is being updated and if it's already taken
    if 'code' in data and data['code'] != module.code:
        if Module.query.filter_by(code=data['code']).first():
            return error_response("Module code already exists", BAD_REQUEST)

    # Validate weekly_hours if provided
    if 'weekly_hours' in data:
        try:
            weekly_hours = float(data['weekly_hours'])
            if weekly_hours <= 0:
                return error_response("Weekly hours must be a positive number", BAD_REQUEST)
        except (ValueError, TypeError):
            return error_response("Weekly hours must be a valid number", BAD_REQUEST)

    try:
        # Update fields if provided
        if 'code' in data:
            module.code = data['code']
        if 'name' in data:
            module.name = data['name']
        if 'description' in data:
            module.description = data['description']
        if 'program_level' in data:
            module.program_level = data['program_level']
        if 'weekly_hours' in data:
            module.weekly_hours = float(data['weekly_hours'])

        db.session.commit()
        
        return success_response({
            "message": "Module updated successfully",
            "module": module.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to update module", SERVER_ERROR)

@modules_bp.route('/<int:module_id>', methods=['DELETE'])
@admin_required
def delete_module(module_id):
    module = Module.query.get(module_id)
    
    if not module:
        return error_response("Module not found", NOT_FOUND)

    try:
        db.session.delete(module)
        db.session.commit()
        
        return success_response({
            "message": "Module deleted successfully"
        })
        
    except Exception as e:
        db.session.rollback()
        return error_response("Failed to delete module", SERVER_ERROR)
