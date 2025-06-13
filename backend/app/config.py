import os
from datetime import timedelta

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')  # Change this in production!
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
