from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from app import db
from functools import wraps
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    # Simple email validation regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    return True, None

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({"error": "Admin privileges required"}), 403
            
        return fn(*args, **kwargs)
    return wrapper

@auth_bp.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({
        "access_token": access_token,
        "user": user.to_dict()
    }), 200

@auth_bp.route('/register', methods=['POST'])
@admin_required
def register():
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    email = request.json.get('email', None)
    password = request.json.get('password', None)
    is_admin = request.json.get('is_admin', False)

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    # Validate email format
    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    # Validate password strength
    is_valid_password, password_error = validate_password(password)
    if not is_valid_password:
        return jsonify({"error": password_error}), 400

    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    # Create new user
    new_user = User(email=email, is_admin=is_admin)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            "message": "User registered successfully",
            "user": new_user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to register user"}), 500
