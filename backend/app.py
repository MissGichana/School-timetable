import logging
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import dotenv # pyright: ignore[reportMissingImports]
from backend.config import Config
from backend.database import Database
from backend.scheduler import Scheduler
from backend.conflict_detector import ConflictDetector

# Load environment variables
dotenv.load_dotenv()

# Setup logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS with specific frontend URL
CORS(app, resources={
    r"/api/*": {
        "origins": [Config.FRONTEND_URL, "http://localhost:3000", "http://localhost:5000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize services
try:
    db = Database()
    scheduler = Scheduler()
    conflict_detector = ConflictDetector()
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    raise

# ==================== ADMIN ENDPOINTS ====================

@app.route('/api/admin/generate-schedule', methods=['POST'])
def generate_schedule():
    """Generate complete timetable"""
    try:
        logger.info("Generating schedule...")
        result = scheduler.generate_schedule()
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in generate_schedule: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/clear-schedule', methods=['POST'])
def clear_schedule():
    """Clear all schedules"""
    try:
        logger.info("Clearing schedule...")
        db.execute_query("DELETE FROM schedules")
        db.execute_query("DELETE FROM conflicts")
        return jsonify({'success': True, 'message': 'Schedule cleared'}), 200
    except Exception as e:
        logger.error(f"Error in clear_schedule: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/add-instructor', methods=['POST'])
def add_instructor():
    """Add new instructor"""
    try:
        data = request.json
        if not data or 'name' not in data or 'email' not in data or 'department' not in data:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        logger.info(f"Adding instructor: {data['name']}")
        db.execute_query(
            "INSERT INTO instructors (name, email, department) VALUES (?, ?, ?)",
            (data['name'], data['email'], data['department'])
        )
        return jsonify({'success': True, 'message': 'Instructor added'}), 201
    except Exception as e:
        logger.error(f"Error in add_instructor: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/add-course', methods=['POST'])
def add_course():
    """Add new course"""
    try:
        data = request.json
        required = ['code', 'name', 'credits', 'capacity', 'department']
        if not data or not all(field in data for field in required):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        logger.info(f"Adding course: {data['code']}")
        db.execute_query(
            "INSERT INTO courses (code, name, credits, capacity, department) VALUES (?, ?, ?, ?, ?)",
            (data['code'], data['name'], data['credits'], data['capacity'], data['department'])
        )
        return jsonify({'success': True, 'message': 'Course added'}), 201
    except Exception as e:
        logger.error(f"Error in add_course: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/add-classroom', methods=['POST'])
def add_classroom():
    """Add new classroom"""
    try:
        data = request.json
        if not data or 'room_number' not in data or 'capacity' not in data:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        logger.info(f"Adding classroom: {data['room_number']}")
        db.execute_query(
            "INSERT INTO classrooms (room_number, capacity, resources) VALUES (?, ?, ?)",
            (data['room_number'], data['capacity'], data.get('resources', ''))
        )
        return jsonify({'success': True, 'message': 'Classroom added'}), 201
    except Exception as e:
        logger.error(f"Error in add_classroom: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/set-instructor-availability', methods=['POST'])
def set_instructor_availability():
    """Set instructor availability"""
    try:
        data = request.json
        required = ['instructor_id', 'day', 'available']
        if not data or not all(field in data for field in required):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        logger.info(f"Updating availability for instructor {data['instructor_id']} on {data['day']}")
        db.execute_query(
            "UPDATE instructor_availability SET available = ? WHERE instructor_id = ? AND day = ?",
            (data['available'], data['instructor_id'], data['day'])
        )
        return jsonify({'success': True, 'message': 'Availability updated'}), 200
    except Exception as e:
        logger.error(f"Error in set_instructor_availability: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== DATA RETRIEVAL ENDPOINTS ====================

@app.route('/api/instructors', methods=['GET'])
def get_instructors():
    """Get all instructors"""
    try:
        instructors = db.fetch_query("SELECT * FROM instructors")
        result = [dict(inst) for inst in instructors]
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in get_instructors: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all courses"""
    try:
        courses = db.fetch_query("SELECT * FROM courses")
        result = [dict(course) for course in courses]
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in get_courses: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/classrooms', methods=['GET'])
def get_classrooms():
    """Get all classrooms"""
    try:
        classrooms = db.fetch_query("SELECT * FROM classrooms")
        result = [dict(room) for room in classrooms]
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in get_classrooms: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    """Get complete timetable"""
    try:
        schedules = db.fetch_query("""
            SELECT s.*, c.code as course_code, c.name as course_name,
                   i.name as instructor_name, r.room_number as classroom_name
            FROM schedules s
            JOIN courses c ON s.course_id = c.id
            JOIN instructors i ON s.instructor_id = i.id
            JOIN classrooms r ON s.classroom_id = r.id
            ORDER BY s.day, s.start_time
        """)
        result = [dict(row) for row in schedules]
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in get_schedules: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/instructor/<int:instructor_id>/schedule', methods=['GET'])
def get_instructor_schedule(instructor_id):
    """Get instructor's personal schedule"""
    try:
        schedules = db.fetch_query("""
            SELECT s.*, c.code as course_code, c.name as course_name, r.room_number as classroom_name
            FROM schedules s
            JOIN courses c ON s.course_id = c.id
            JOIN classrooms r ON s.classroom_id = r.id
            WHERE s.instructor_id = ?
            ORDER BY s.day, s.start_time
        """, (instructor_id,))
        
        instructor = db.fetch_one("SELECT * FROM instructors WHERE id = ?", (instructor_id,))
        
        result = {
            'instructor': dict(instructor) if instructor else None,
            'schedule': [dict(row) for row in schedules]
        }
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in get_instructor_schedule: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/student/<int:student_id>/schedule', methods=['GET'])
def get_student_schedule(student_id):
    """Get student's personal schedule"""
    try:
        student = db.fetch_one("SELECT * FROM students WHERE id = ?", (student_id,))
        
        enrollments = db.fetch_query("""
            SELECT s.*, c.code as course_code, c.name as course_name,
                   i.name as instructor_name, r.room_number as classroom_name
            FROM schedules s
            JOIN courses c ON s.course_id = c.id
            JOIN instructors i ON s.instructor_id = i.id
            JOIN classrooms r ON s.classroom_id = r.id
            WHERE c.id IN (SELECT course_id FROM enrollments WHERE student_id = ?)
            ORDER BY s.day, s.start_time
        """, (student_id,))
        
        result = {
            'student': dict(student) if student else None,
            'schedule': [dict(row) for row in enrollments]
        }
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in get_student_schedule: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/conflicts', methods=['GET'])
def get_conflicts():
    """Get all conflicts"""
    try:
        conflicts = db.fetch_query("""
            SELECT c.*, s.course_id, co.code as course_code, 
                   i.name as instructor_name, r.room_number as classroom_name
            FROM conflicts c
            LEFT JOIN schedules s ON c.schedule_id = s.id
            LEFT JOIN courses co ON s.course_id = co.id
            LEFT JOIN instructors i ON s.instructor_id = i.id
            LEFT JOIN classrooms r ON s.classroom_id = r.id
        """)
        result = [dict(row) for row in conflicts]
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in get_conflicts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/students', methods=['GET'])
def get_students():
    """Get all students"""
    try:
        students = db.fetch_query("SELECT * FROM students")
        result = [dict(student) for student in students]
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in get_students: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== STATISTICS ENDPOINTS ====================

@app.route('/api/stats/instructor-workload', methods=['GET'])
def get_instructor_workload():
    """Get instructor workload statistics"""
    try:
        workload = scheduler.get_instructor_workload()
        return jsonify(workload), 200
    except Exception as e:
        logger.error(f"Error in get_instructor_workload: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/classroom-utilization', methods=['GET'])
def get_classroom_utilization():
    """Get classroom utilization statistics"""
    try:
        utilization = scheduler.get_classroom_utilization()
        return jsonify(utilization), 200
    except Exception as e:
        logger.error(f"Error in get_classroom_utilization: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        total_courses = db.fetch_one("SELECT COUNT(*) as count FROM courses")
        total_instructors = db.fetch_one("SELECT COUNT(*) as count FROM instructors")
        total_classrooms = db.fetch_one("SELECT COUNT(*) as count FROM classrooms")
        scheduled_classes = db.fetch_one("SELECT COUNT(*) as count FROM schedules")
        
        return jsonify({
            'total_courses': total_courses['count'] if total_courses else 0,
            'total_instructors': total_instructors['count'] if total_instructors else 0,
            'total_classrooms': total_classrooms['count'] if total_classrooms else 0,
            'scheduled_classes': scheduled_classes['count'] if scheduled_classes else 0
        }), 200
    except Exception as e:
        logger.error(f"Error in get_dashboard_stats: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {error}")
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"500 error: {error}")
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    logger.info(f"Starting Flask app on {Config.HOST}:{Config.PORT}")
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT, threaded=True)
