import os
from datetime import datetime

class Config:
    """Configuration for the application"""
    
    # Database
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), '../database/timetable.db')
    
    # Flask
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
    TESTING = os.getenv('TESTING', 'False') == 'True'
    
    # Server Configuration
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # Frontend URL for CORS
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    # Application settings
    SEMESTER = "Spring 2026"
    SCHOOL_NAME = "University"
    
    # Scheduling constraints
    LUNCH_START = "13:00"  # 1 PM
    LUNCH_END = "14:00"    # 2 PM
    MIN_CLASS_DURATION = 2  # 2 hours
    MAX_CLASS_DURATION = 3  # 3 hours
    WORK_START_TIME = "08:00"  # 8 AM
    WORK_END_TIME = "17:00"    # 5 PM
    
    # Instructor constraints
    MAX_CLASSES_PER_INSTRUCTOR = 5
    MIN_CLASSES_PER_INSTRUCTOR = 3
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(os.path.dirname(__file__), '../logs/app.log')
