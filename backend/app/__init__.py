from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.lecturers import lecturers_bp
    from app.routes.modules import modules_bp
    from app.routes.timeslots import timeslots_bp
    from app.routes.rooms import rooms_bp
    from app.routes.program_levels import program_levels_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(lecturers_bp, url_prefix='/api/lecturers')
    app.register_blueprint(modules_bp, url_prefix='/api/modules')
    app.register_blueprint(timeslots_bp, url_prefix='/api/timeslots')
    app.register_blueprint(rooms_bp, url_prefix='/api/rooms')
    app.register_blueprint(program_levels_bp, url_prefix='/api/program-levels')
    
    # Register CLI commands
    from app.cli import create_admin
    app.cli.add_command(create_admin)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
